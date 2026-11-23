"""Build an HTML caregiver email with embedded PNG charts and a text alternative."""

import base64
import json
import math
import subprocess
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from html import escape
from pathlib import Path
from string import Template

from caregiver_view import as_time, mgdl
from email_report import format_email_report

ROOT = Path(__file__).resolve().parent
LOGO = ROOT / "samples" / "8c067082-8ffa-479f-9531-aeddc01b81f8.JPG"


def display_readings(report):
    """Return (display readings, example flag); fill an empty display with labelled demo values.

    This never mutates original_information or caregiver_action. Synthetic display
    values cannot become clinical input, a measured reading or a reassuring alert.
    """
    original = report["original_information"]
    readings = list(original.get("glucose_history", []))
    if original["glucose"] is not None:
        readings.append(original["glucose"])
    if readings:
        return readings, original.get("synthetic", False)
    now = as_time(report["caregiver_action"]["generated_at"])
    return [{"value": value, "unit": "mg/dL", "measured_at": (now + timedelta(minutes=minutes)).isoformat()}
            for minutes, value in ((-120, 250), (-90, 240), (-60, 220), (-30, 195),
                                   (0, report["estimated_current_glucose"]["estimate"]))], True


def chart_data(report):
    """Report dict -> JSON drawing specification, converting measured units to mg/dL."""
    readings, example = display_readings(report)
    points = [{"x": as_time(item["measured_at"]).timestamp(), "y": round(mgdl(item), 1)} for item in readings]
    now = as_time(report["caregiver_action"]["generated_at"]).timestamp()
    forecast = [{"x": as_time(item["at"]).timestamp(), "y": item["estimate"], "low": item["low"], "high": item["high"]}
                for item in report["forecast"]]
    min_x = min([point["x"] for point in points] + [now - 7200])
    max_x = max([point["x"] for point in points] + [now + 7200]) + 600
    ticks = [{"x": min_x + (max_x-min_x)*i/3,
              "label": datetime.fromtimestamp(min_x + (max_x-min_x)*i/3, timezone(timedelta(hours=8))).strftime("%d %b\n%H:%M")}
             for i in range(4)]
    food = [{"label": label, "estimate": report["food"][key]["estimate"],
             "low": report["food"][key]["illustrative_range"][0], "high": report["food"][key]["illustrative_range"][1], "color": color}
            for label, key, color in (("Total carbohydrates", "carbohydrate_g", "#245FE8"), ("Sugar", "sugar_g", "#D48A16"))]
    data = {"measured": points, "forecast": forecast, "now": now, "min_x": min_x, "max_x": max_x, "ticks": ticks,
            "max_y": math.ceil(max([p["y"] for p in points] + [p["high"] for p in forecast] + report["estimated_current_glucose"]["illustrative_range"] + [240])/20)*20,
            "current_estimate": {"x": now, "y": report["estimated_current_glucose"]["estimate"],
                                 "low": report["estimated_current_glucose"]["illustrative_range"][0],
                                 "high": report["estimated_current_glucose"]["illustrative_range"][1]},
            "food": food, "food_max": max(item["high"] for item in food),
            "reading_label": "DEMO example readings" if example else "Measured / latest"}
    if report.get("language") == "zh-CN":
        from chinese_email import chart_labels
        return chart_labels(data)
    return data


def render_charts(report):
    """Report -> two PNG byte arrays, rendered by Windows System.Drawing in a child process.

    No installs, network requests or files are made. The fixed renderer receives
    data through stdin, never executable user input. Requires Windows PowerShell.
    """
    script = (ROOT / "chart_renderer.ps1").read_text(encoding="utf-8")
    try:
        result = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
                                input=json.dumps(chart_data(report)), capture_output=True, text=True,
                                timeout=40, check=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        encoded = json.loads(result.stdout.lstrip("\ufeff"))
        return {name: base64.b64decode(encoded[name], validate=True) for name in ("glucose", "food")}
    except (subprocess.SubprocessError, ValueError, KeyError) as error:
        raise OSError("PNG chart rendering failed; check Windows PowerShell and System.Drawing availability.") from error


def html_body(report, sources, text_only=False):
    """Report + URLs -> escaped HTML, or Chinese text when text_only; no network or mutation."""
    original = report["original_information"]
    action = report["caregiver_action"]
    history, example = display_readings(report)
    reading = history[-1]
    readable = lambda value: as_time(value).astimezone(timezone(timedelta(hours=8))).strftime("%d %b %Y, %H:%M (UTC%z)")
    values = {"patient": original["patient_id"], "prepared": readable(action["generated_at"]),
              "level": action["level"].upper(), "color": action["color"], "background": action["background"],
              "action_title": action["title"], "action_detail": action["detail"],
              "sugar_action": action["sugar"], "doctor_action": action["doctor"],
              "current": f"{reading['value']:g} {reading['unit']}",
              "current_label": "ILLUSTRATIVE GLUCOSE (DEMO)" if example else "LATEST RECORDED GLUCOSE",
              "measured_at": readable(reading["measured_at"]),
              "freshness": "DEMO value; not a patient measurement" if example else ("Recent supplied reading" if action["fresh"] else "Reading is old or future-dated; check again"),
              "history_note": f"{len(history)} DEMO example values; not patient measurements" if example else f"{len(history)} supplied readings",
              "history_values": " | ".join(f"{readable(r['measured_at'])}: {r['value']:g} {r['unit']}" for r in history[-6:]),
              "meal_time": readable(original["meal_captured_at"]), "food_source": "Simulated estimates; image recognition is not implemented",
              "suggestions": report["suggestions"], "warning": report["warning"]}
    estimate = report["estimated_current_glucose"]
    values.update(estimated_current=f"{estimate['estimate']:g} {estimate['unit']}",
                  estimated_range=f"{estimate['illustrative_range'][0]:g} to {estimate['illustrative_range'][1]:g} {estimate['unit']}",
                  summary_status="Slightly High" if estimate.get("display_status") == "slightly_high" else "Simulation only",
                  logo_image="cid:glycat-logo")
    forecast = report["forecast"][0]
    values.update(forecast_value=f"{forecast['estimate']:g} {forecast['unit']}", forecast_range=f"{forecast['low']:g} to {forecast['high']:g}")
    for key, name in (("carbohydrate_g", "carbs"), ("sugar_g", "sugar")):
        item = report["food"][key]
        values[name + "_value"] = f"{item['estimate']:g}"
        values[name + "_range"] = f"{item['illustrative_range'][0]:g} to {item['illustrative_range'][1]:g}"
    template = "email_template.html"
    if report.get("language") == "zh-CN":
        from chinese_email import display_values, text_body
        values = display_values(report, values, history, example)
        if text_only:
            return text_body(report, values)
        template = "email_template_zh.html"
    values.update(sources)
    return Template((ROOT / template).read_text(encoding="utf-8")).substitute({key: escape(str(value), quote=True) for key, value in values.items()})


def compose_email(report, raw, subtype, sender, recipient):
    """Report/image/addresses -> MIME email with charts, supplied meal bytes and local GlyCat logo."""
    charts = render_charts(report)
    message = EmailMessage()
    message["Subject"] = "[SIMULATED DEMO] " + report["caregiver_action"]["title"]
    message["From"], message["To"] = sender, recipient
    if report.get("language") == "zh-CN":
        from chinese_email import action_text
        message.replace_header("Subject", "[模拟演示] 用餐与血糖报告 - " + action_text(report["caregiver_action"])["action_title"])
    message.set_content(html_body(report, {}, text_only=True) if report.get("language") == "zh-CN" else format_email_report(report))
    message.add_alternative(html_body(report, {"glucose_image": "cid:glucose-chart", "food_image": "cid:food-chart", "meal_image": "cid:meal-photo"}), subtype="html")
    part = message.get_payload()[-1]
    for name, image in charts.items():
        part.add_related(image, maintype="image", subtype="png", cid=f"<{name}-chart>", filename=name + "-chart.png", disposition="inline")
    part.add_related(raw, maintype="image", subtype=subtype, cid="<meal-photo>", filename="meal." + subtype, disposition="inline")
    part.add_related(LOGO.read_bytes(), maintype="image", subtype="jpeg", cid="<glycat-logo>", filename="glycat-logo.jpg", disposition="inline")
    return message


def write_preview(report, raw, subtype, destination):
    """Render a self-contained HTML file to destination; intended for explicit local preview only."""
    charts = render_charts(report)
    sources = {name + "_image": "data:image/png;base64," + base64.b64encode(image).decode("ascii") for name, image in charts.items()}
    sources["meal_image"] = f"data:image/{subtype};base64," + base64.b64encode(raw).decode("ascii")
    sources["logo_image"] = "data:image/jpeg;base64," + base64.b64encode(LOGO.read_bytes()).decode("ascii")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html_body(report, sources), encoding="utf-8")
