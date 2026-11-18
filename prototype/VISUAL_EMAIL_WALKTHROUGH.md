# Visual caregiver email: line-by-line walkthrough

Every nonblank line in each new source file is explained below. For existing files, all added/replaced lines relative to the published baseline are covered, including the retained readable-email work. Blank lines are separators only. Source code is included alongside each explanation so the exact field, condition, label, coordinates and branch can be reviewed.

The JSON-only SMTP body was replaced first by readable text and now by MIME text/HTML alternatives. The original photo is delivered as a downloadable inline related image, enabling the email template to display it. Chart PNGs use the same related-image mechanism. The former single-reading validation block is replaced by a shared validator for current and historical readings. No real glucose forecast or image-based food model is introduced.

Caregiver screening considers only actual fresh supplied readings and severe-symptom flags. Missing, synthetic, stale and future-dated data cannot be reassuring. Freshness (15 minutes), the 180 chart reference and repeated-high lookback (two hours) are prototype policies requiring clinical review. Fixed forecasts never influence action colours. The CDC sources are linked in README and the template.

## caregiver_view.py

| Line | Source | Explanation |
| --- | --- | --- |
| 1 | `"""Create measured-reading screening cards and an explicitly simulated forecast."""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 3 | `from datetime import datetime, timedelta, timezone` | Import datetime, timedelta, timezone to support the visual caregiver email. |
| 6 | `def as_time(value):` | Define as_time: Timezone-qualified ISO string -> aware datetime; validation happens in server.py. |
| 7 | `"""Timezone-qualified ISO string -> aware datetime; validation happens in server.py."""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 8 | `return datetime.fromisoformat(value.replace("Z", "+00:00"))` | Return the constructed value to the caller to support the visual caregiver email. |
| 11 | `def mgdl(reading):` | Define mgdl: Reading dict -> glucose in mg/dL for plotting and threshold comparison only. |
| 12 | `"""Reading dict -> glucose in mg/dL for plotting and threshold comparison only."""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 13 | `return reading["value"] * (18.0182 if reading["unit"] == "mmol/L" else 1)` | Return the constructed value to the caller to support the visual caregiver email. |
| 16 | `def caregiver_summary(event, now=None):` | Define caregiver_summary: Validated event + optional aware clock -> action cards; never uses AI estimates. |
| 17 | `"""Validated event + optional aware clock -> action cards; never uses AI estimates.` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 19 | `Fresh means at most 15 minutes old; this is a prototype policy, not a clinical` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 20 | `standard. Supplied severe symptoms override missing/stale readings. These` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 21 | `generic screening rules do not determine insulin doses or certify safety.` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 22 | `"""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 23 | `now = now or datetime.now(timezone.utc)` | Store the displayed expression in `now` to screen fresh supplied readings and severe symptoms without using model estimates. |
| 24 | `reading = event["glucose"]` | Store the displayed expression in `reading` to screen fresh supplied readings and severe symptoms without using model estimates. |
| 25 | `result = {"level": "review", "title": "Check glucose before deciding", "color": "#AD6600",` | Store the displayed expression in `result` to screen fresh supplied readings and severe symptoms without using model estimates. |
| 26 | `"background": "#FFF5DE", "sugar": "No sugar-change decision available.",` | Continue the multiline statement: Store the displayed expression in `result` to screen fresh supplied readings and severe symptoms without using model estimates. |
| 27 | `"doctor": "Follow the care plan; contact the care team if concerned.",` | Continue the multiline statement: Store the displayed expression in `result` to screen fresh supplied readings and severe symptoms without using model estimates. |
| 28 | `"detail": "A recent measured reading is needed to assess the glucose threshold alerts.",` | Continue the multiline statement: Store the displayed expression in `result` to screen fresh supplied readings and severe symptoms without using model estimates. |
| 29 | `"generated_at": now.isoformat(), "fresh": False}` | Continue the multiline statement: Store the displayed expression in `result` to screen fresh supplied readings and severe symptoms without using model estimates. |
| 30 | `if event.get("synthetic", False):` | Check `event.get('synthetic', False)`; execute this branch when true to screen fresh supplied readings and severe symptoms without using model estimates. |
| 31 | `result["title"] = "Demonstration only — safety unassessed"` | Store the displayed expression in `result['title']` to screen fresh supplied readings and severe symptoms without using model estimates. |
| 32 | `result["detail"] = "These example readings are synthetic. Do not use this report for treatment."` | Store the displayed expression in `result['detail']` to screen fresh supplied readings and severe symptoms without using model estimates. |
| 33 | `return result` | Return the constructed value to the caller to screen fresh supplied readings and severe symptoms without using model estimates. |
| 34 | `severe = event.get("severe_symptoms", False)` | Store the displayed expression in `severe` to screen fresh supplied readings and severe symptoms without using model estimates. |
| 35 | `if severe:` | Check `severe`; execute this branch when true to screen fresh supplied readings and severe symptoms without using model estimates. |
| 36 | `result.update(level="urgent", title="Seek emergency medical help", color="#B42318", background="#FEECE9",` | Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 37 | `detail="Severe symptoms were reported. Get emergency help now; do not wait for an email response.",` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 38 | `sugar="If unconscious or unable to swallow, do not give food or drink by mouth.",` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 39 | `doctor="Emergency help now; follow the prescribed emergency plan.")` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 40 | `return result` | Return the constructed value to the caller to screen fresh supplied readings and severe symptoms without using model estimates. |
| 41 | `if reading is None:` | Check `reading is None`; execute this branch when true to screen fresh supplied readings and severe symptoms without using model estimates. |
| 42 | `return result` | Return the constructed value to the caller to screen fresh supplied readings and severe symptoms without using model estimates. |
| 43 | `age = (now - as_time(reading["measured_at"])).total_seconds()` | Store the displayed expression in `age` to screen fresh supplied readings and severe symptoms without using model estimates. |
| 44 | `if age < 0 or age > 900:` | Check `age < 0 or age > 900`; execute this branch when true to screen fresh supplied readings and severe symptoms without using model estimates. |
| 45 | `result["detail"] = "The latest reading is old or future-dated. Obtain a current reading; the old value is shown below."` | Store the displayed expression in `result['detail']` to screen fresh supplied readings and severe symptoms without using model estimates. |
| 46 | `return result` | Return the constructed value to the caller to screen fresh supplied readings and severe symptoms without using model estimates. |
| 47 | `result["fresh"] = True` | Store the displayed expression in `result['fresh']` to screen fresh supplied readings and severe symptoms without using model estimates. |
| 48 | `value = mgdl(reading)` | Store the displayed expression in `value` to screen fresh supplied readings and severe symptoms without using model estimates. |
| 49 | `if value < 55:` | Check `value < 55`; execute this branch when true to screen fresh supplied readings and severe symptoms without using model estimates. |
| 50 | `result.update(level="urgent", title="Very low reading — urgent help", color="#B42318", background="#FEECE9",` | Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 51 | `detail="A measured glucose below 55 mg/dL needs immediate attention. Follow the emergency care plan.",` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 52 | `sugar="If awake and able to swallow, follow the prescribed low-glucose treatment plan. Otherwise give nothing by mouth.",` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 53 | `doctor="Seek urgent medical help; do not wait for this prototype.")` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 54 | `elif value < 70:` | Check `value < 70`; execute this branch when true to screen fresh supplied readings and severe symptoms without using model estimates. |
| 55 | `result.update(title="Low reading — act on the low-glucose plan",` | Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 56 | `detail="The measured reading is below 70 mg/dL. Check on the patient and follow their prescribed low-glucose plan.",` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 57 | `sugar="More fast-acting carbohydrate may be needed under the low-glucose plan, if awake and able to swallow.",` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 58 | `doctor="Seek urgent help for severe symptoms or if the low reading does not improve.")` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 59 | `elif value >= 250:` | Check `value >= 250`; execute this branch when true to screen fresh supplied readings and severe symptoms without using model estimates. |
| 60 | `result.update(title="High reading — contact the care team",` | Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 61 | `detail="A reading of at least 250 mg/dL needs the prescribed high-glucose/ketone plan and care-team advice.",` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 62 | `sugar="Extra sugar is not a correction for this high reading. Review future meal choices with the care team.",` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 63 | `doctor="Contact the care team. Emergency help if readings stay at 300 mg/dL or above, or severe symptoms occur.")` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 64 | `recent = [r for r in event.get("glucose_history", [])` | Store the displayed expression in `recent` to screen fresh supplied readings and severe symptoms without using model estimates. |
| 65 | `if 0 < (as_time(reading["measured_at"]) - as_time(r["measured_at"])).total_seconds() <= 7200]` | Continue the multiline statement: Store the displayed expression in `recent` to screen fresh supplied readings and severe symptoms without using model estimates. |
| 66 | `if value >= 300 and recent and mgdl(recent[-1]) >= 300:` | Check `value >= 300 and recent and (mgdl(recent[-1]) >= 300)`; execute this branch when true to screen fresh supplied readings and severe symptoms without using model estimates. |
| 67 | `result.update(level="urgent", title="Repeated very high readings — emergency help", color="#B42318",` | Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 68 | `background="#FEECE9", doctor="Seek emergency medical help now.",` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 69 | `detail="The latest and previous supplied readings are both at least 300 mg/dL. Follow the emergency plan.")` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 70 | `elif value > 180:` | Check `value > 180`; execute this branch when true to screen fresh supplied readings and severe symptoms without using model estimates. |
| 71 | `result.update(title="Above example reference — review the care plan",` | Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 72 | `detail="The reading is above the chart's example 180 mg/dL reference. Personal targets depend on meal timing and the care plan.",` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 73 | `sugar="Discuss meal portions and sugar choices with the care team; do not treat this as a low reading.")` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 74 | `else:` | Continue the multiline statement: Check `value > 180`; execute this branch when true to screen fresh supplied readings and severe symptoms without using model estimates. |
| 75 | `result.update(level="monitor", title="No threshold alert in the latest reading", color="#087F73", background="#E8F7F3",` | Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 76 | `detail="Continue prescribed monitoring. This reading alone cannot establish that the patient is safe.",` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 77 | `sugar="No extra sugar or restriction is indicated by these prototype threshold checks.",` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 78 | `doctor="Continue the care plan. Seek help for symptoms or concerns, regardless of this colour.")` | Continue the multiline statement: Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 79 | `return result` | Return the constructed value to the caller to screen fresh supplied readings and severe symptoms without using model estimates. |
| 82 | `def demo_forecast(now):` | Define demo_forecast: Aware clock -> three fixed future demo points in mg/dL; no physiological model. |
| 83 | `"""Aware clock -> three fixed future demo points in mg/dL; no physiological model."""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 84 | `return [{"at": (now + timedelta(minutes=minutes)).isoformat(), "estimate": value,` | Return the constructed value to the caller to provide fixed, labelled future examples. |
| 85 | `"low": low, "high": high, "unit": "mg/dL", "source": "fixed_demo_stub"}` | Continue the multiline statement: Return the constructed value to the caller to provide fixed, labelled future examples. |
| 86 | `for minutes, value, low, high in ((30, 160, 110, 210), (60, 150, 95, 205), (120, 125, 85, 190))]` | Continue the multiline statement: Return the constructed value to the caller to provide fixed, labelled future examples. |

## visual_email.py

| Line | Source | Explanation |
| --- | --- | --- |
| 1 | `"""Build an HTML caregiver email with embedded PNG charts and a text alternative."""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 3 | `import base64` | Import base64 to support the visual caregiver email. |
| 4 | `import json` | Import json to support the visual caregiver email. |
| 5 | `import math` | Import math to support the visual caregiver email. |
| 6 | `import subprocess` | Import subprocess to support the visual caregiver email. |
| 7 | `from datetime import datetime, timedelta, timezone` | Import datetime, timedelta, timezone to support the visual caregiver email. |
| 8 | `from email.message import EmailMessage` | Import EmailMessage to support the visual caregiver email. |
| 9 | `from html import escape` | Import escape to support the visual caregiver email. |
| 10 | `from pathlib import Path` | Import Path to support the visual caregiver email. |
| 11 | `from string import Template` | Import Template to support the visual caregiver email. |
| 13 | `from caregiver_view import as_time, mgdl` | Import as_time, mgdl to support the visual caregiver email. |
| 14 | `from email_report import format_email_report` | Import format_email_report to support the visual caregiver email. |
| 16 | `ROOT = Path(__file__).resolve().parent` | Store the displayed expression in `ROOT` to support the visual caregiver email. |
| 19 | `def chart_data(report):` | Define chart_data: Report dict -> JSON drawing specification, converting measured units to mg/dL. |
| 20 | `"""Report dict -> JSON drawing specification, converting measured units to mg/dL."""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 21 | `original = report["original_information"]` | Store the displayed expression in `original` to convert measured units and build separate measured/forecast plotting data. |
| 22 | `readings = list(original.get("glucose_history", []))` | Store the displayed expression in `readings` to convert measured units and build separate measured/forecast plotting data. |
| 23 | `if original["glucose"] is not None:` | Check `original['glucose'] is not None`; execute this branch when true to convert measured units and build separate measured/forecast plotting data. |
| 24 | `readings.append(original["glucose"])` | Call `readings.append` to convert measured units and build separate measured/forecast plotting data. |
| 25 | `points = [{"x": as_time(item["measured_at"]).timestamp(), "y": round(mgdl(item), 1)} for item in readings]` | Store the displayed expression in `points` to convert measured units and build separate measured/forecast plotting data. |
| 26 | `now = as_time(report["caregiver_action"]["generated_at"]).timestamp()` | Store the displayed expression in `now` to convert measured units and build separate measured/forecast plotting data. |
| 27 | `forecast = [{"x": as_time(item["at"]).timestamp(), "y": item["estimate"], "low": item["low"], "high": item["high"]}` | Store the displayed expression in `forecast` to convert measured units and build separate measured/forecast plotting data. |
| 28 | `for item in report["forecast"]]` | Continue the multiline statement: Store the displayed expression in `forecast` to convert measured units and build separate measured/forecast plotting data. |
| 29 | `min_x = min([point["x"] for point in points] + [now - 7200])` | Store the displayed expression in `min_x` to convert measured units and build separate measured/forecast plotting data. |
| 30 | `max_x = max([point["x"] for point in points] + [now + 7200]) + 600` | Store the displayed expression in `max_x` to convert measured units and build separate measured/forecast plotting data. |
| 31 | `ticks = [{"x": min_x + (max_x-min_x)*i/3,` | Store the displayed expression in `ticks` to convert measured units and build separate measured/forecast plotting data. |
| 32 | `"label": datetime.fromtimestamp(min_x + (max_x-min_x)*i/3, timezone(timedelta(hours=8))).strftime("%d %b\n%H:%M")}` | Continue the multiline statement: Store the displayed expression in `ticks` to convert measured units and build separate measured/forecast plotting data. |
| 33 | `for i in range(4)]` | Continue the multiline statement: Store the displayed expression in `ticks` to convert measured units and build separate measured/forecast plotting data. |
| 34 | `food = [{"label": label, "estimate": report["food"][key]["estimate"],` | Store the displayed expression in `food` to convert measured units and build separate measured/forecast plotting data. |
| 35 | `"low": report["food"][key]["illustrative_range"][0], "high": report["food"][key]["illustrative_range"][1], "color": color}` | Continue the multiline statement: Store the displayed expression in `food` to convert measured units and build separate measured/forecast plotting data. |
| 36 | `for label, key, color in (("Total carbohydrates", "carbohydrate_g", "#245FE8"), ("Sugar", "sugar_g", "#D48A16"))]` | Continue the multiline statement: Store the displayed expression in `food` to convert measured units and build separate measured/forecast plotting data. |
| 37 | `return {"measured": points, "forecast": forecast, "now": now, "min_x": min_x, "max_x": max_x, "ticks": ticks,` | Return the constructed value to the caller to convert measured units and build separate measured/forecast plotting data. |
| 38 | `"max_y": math.ceil(max([p["y"] for p in points] + [p["high"] for p in forecast] + [240])/40)*40,` | Continue the multiline statement: Return the constructed value to the caller to convert measured units and build separate measured/forecast plotting data. |
| 39 | `"food": food, "food_max": max(item["high"] for item in food)}` | Continue the multiline statement: Return the constructed value to the caller to convert measured units and build separate measured/forecast plotting data. |
| 42 | `def render_charts(report):` | Define render_charts: Report -> two PNG byte arrays, rendered by Windows System.Drawing in a child process. |
| 43 | `"""Report -> two PNG byte arrays, rendered by Windows System.Drawing in a child process.` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 45 | `No installs, network requests or files are made. The fixed renderer receives` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 46 | `data through stdin, never executable user input. Requires Windows PowerShell.` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 47 | `"""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 48 | `script = (ROOT / "chart_renderer.ps1").read_text(encoding="utf-8")` | Store the displayed expression in `script` to render PNGs locally using Windows drawing. |
| 49 | `try:` | Protect this operation with the shown error/cleanup handlers to render PNGs locally using Windows drawing. |
| 50 | `result = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],` | Store the displayed expression in `result` to render PNGs locally using Windows drawing. |
| 51 | `input=json.dumps(chart_data(report)), capture_output=True, text=True,` | Continue the multiline statement: Store the displayed expression in `result` to render PNGs locally using Windows drawing. |
| 52 | `timeout=40, check=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` | Continue the multiline statement: Store the displayed expression in `result` to render PNGs locally using Windows drawing. |
| 53 | `encoded = json.loads(result.stdout.lstrip("\ufeff"))` | Store the displayed expression in `encoded` to render PNGs locally using Windows drawing. |
| 54 | `return {name: base64.b64decode(encoded[name], validate=True) for name in ("glucose", "food")}` | Return the constructed value to the caller to render PNGs locally using Windows drawing. |
| 55 | `except (subprocess.SubprocessError, ValueError, KeyError) as error:` | Catch the listed expected failures and produce a controlled failure instead of sending an incomplete report. |
| 56 | `raise OSError("PNG chart rendering failed; check Windows PowerShell and System.Drawing availability.") from error` | Stop this path with the stated validation/rendering failure; invalid data is not silently accepted. |
| 59 | `def html_body(report, sources):` | Define html_body: Report + image URLs -> escaped table-based HTML; supports CID or local-preview data URLs. |
| 60 | `"""Report + image URLs -> escaped table-based HTML; supports CID or local-preview data URLs."""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 61 | `original = report["original_information"]` | Store the displayed expression in `original` to fill the email template with escaped values. |
| 62 | `action = report["caregiver_action"]` | Store the displayed expression in `action` to fill the email template with escaped values. |
| 63 | `reading = original["glucose"]` | Store the displayed expression in `reading` to fill the email template with escaped values. |
| 64 | `history = list(original.get("glucose_history", []))` | Store the displayed expression in `history` to fill the email template with escaped values. |
| 65 | `if reading is not None:` | Check `reading is not None`; execute this branch when true to fill the email template with escaped values. |
| 66 | `history.append(reading)` | Call `history.append` to fill the email template with escaped values. |
| 67 | `readable = lambda value: as_time(value).astimezone(timezone(timedelta(hours=8))).strftime("%d %b %Y, %H:%M (UTC%z)")` | Store the displayed expression in `readable` to fill the email template with escaped values. |
| 68 | `values = {"patient": original["patient_id"], "prepared": readable(action["generated_at"]),` | Store the displayed expression in `values` to fill the email template with escaped values. |
| 69 | `"level": action["level"].upper(), "color": action["color"], "background": action["background"],` | Continue the multiline statement: Store the displayed expression in `values` to fill the email template with escaped values. |
| 70 | `"action_title": action["title"], "action_detail": action["detail"],` | Continue the multiline statement: Store the displayed expression in `values` to fill the email template with escaped values. |
| 71 | `"sugar_action": action["sugar"], "doctor_action": action["doctor"],` | Continue the multiline statement: Store the displayed expression in `values` to fill the email template with escaped values. |
| 72 | `"current": f"{reading['value']:g} {reading['unit']}" if reading else "Unavailable",` | Continue the multiline statement: Store the displayed expression in `values` to fill the email template with escaped values. |
| 73 | `"measured_at": readable(reading["measured_at"]) if reading else "No measured reading supplied",` | Continue the multiline statement: Store the displayed expression in `values` to fill the email template with escaped values. |
| 74 | `"freshness": "Synthetic example" if original.get("synthetic") else ("Recent supplied reading" if action["fresh"] else "Freshness not confirmed"),` | Continue the multiline statement: Store the displayed expression in `values` to fill the email template with escaped values. |
| 75 | `"history_note": f"{len(history)} supplied readings" + (" (synthetic examples)" if original.get("synthetic") else ""),` | Continue the multiline statement: Store the displayed expression in `values` to fill the email template with escaped values. |
| 76 | `"history_values": " &#124; ".join(f"{readable(r['measured_at'])}: {r['value']:g} {r['unit']}" for r in history[-6:]) or "No measured history is available.",` | Continue the multiline statement: Store the displayed expression in `values` to fill the email template with escaped values. |
| 77 | `"meal_time": readable(original["meal_captured_at"]), "food_source": "Simulated estimates; image recognition is not implemented",` | Continue the multiline statement: Store the displayed expression in `values` to fill the email template with escaped values. |
| 78 | `"suggestions": report["suggestions"], "warning": report["warning"]}` | Continue the multiline statement: Store the displayed expression in `values` to fill the email template with escaped values. |
| 79 | `forecast = report["forecast"][0]` | Store the displayed expression in `forecast` to fill the email template with escaped values. |
| 80 | `values.update(forecast_value=f"{forecast['estimate']:g} {forecast['unit']}", forecast_range=f"{forecast['low']:g} to {forecast['high']:g}")` | Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 81 | `for key, name in (("carbohydrate_g", "carbs"), ("sugar_g", "sugar")):` | Iterate `(('carbohydrate_g', 'carbs'), ('sugar_g', 'sugar'))` as `(key, name)` to fill the email template with escaped values. |
| 82 | `item = report["food"][key]` | Store the displayed expression in `item` to fill the email template with escaped values. |
| 83 | `values[name + "_value"] = f"{item['estimate']:g}"` | Store the displayed expression in `values[name + '_value']` to fill the email template with escaped values. |
| 84 | `values[name + "_range"] = f"{item['illustrative_range'][0]:g} to {item['illustrative_range'][1]:g}"` | Store the displayed expression in `values[name + '_range']` to fill the email template with escaped values. |
| 85 | `values.update(sources)` | Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 86 | `return Template((ROOT / "email_template.html").read_text(encoding="utf-8")).substitute({key: escape(str(value), quote=True) for key, value in values.items()})` | Return the constructed value to the caller to fill the email template with escaped values. |
| 89 | `def compose_email(report, raw, subtype, sender, recipient):` | Define compose_email: Report/image/addresses -> MIME message with text, HTML and three downloadable inline images. |
| 90 | `"""Report/image/addresses -> MIME message with text, HTML and three downloadable inline images."""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 91 | `charts = render_charts(report)` | Store the displayed expression in `charts` to assemble text, HTML and related downloadable images. |
| 92 | `message = EmailMessage()` | Store the displayed expression in `message` to assemble text, HTML and related downloadable images. |
| 93 | `message["Subject"] = "[SIMULATED DEMO] " + report["caregiver_action"]["title"]` | Store the displayed expression in `message['Subject']` to assemble text, HTML and related downloadable images. |
| 94 | `message["From"], message["To"] = sender, recipient` | Store the displayed expression in `(message['From'], message['To'])` to assemble text, HTML and related downloadable images. |
| 95 | `message.set_content(format_email_report(report))` | Set the readable text alternative; HTML and charts are attached separately. |
| 96 | `message.add_alternative(html_body(report, {"glucose_image": "cid:glucose-chart", "food_image": "cid:food-chart", "meal_image": "cid:meal-photo"}), subtype="html")` | Add HTML alongside the readable text body, so the email client can choose its supported format. |
| 97 | `part = message.get_payload()[-1]` | Store the displayed expression in `part` to assemble text, HTML and related downloadable images. |
| 98 | `for name, image in charts.items():` | Iterate `charts.items()` as `(name, image)` to assemble text, HTML and related downloadable images. |
| 99 | `part.add_related(image, maintype="image", subtype="png", cid=f"<{name}-chart>", filename=name + "-chart.png", disposition="inline")` | Attach these PNG/photo bytes to the HTML MIME part with a content ID, inline disposition and downloadable filename. |
| 100 | `part.add_related(raw, maintype="image", subtype=subtype, cid="<meal-photo>", filename="meal." + subtype, disposition="inline")` | Attach these PNG/photo bytes to the HTML MIME part with a content ID, inline disposition and downloadable filename. |
| 101 | `return message` | Return the constructed value to the caller to assemble text, HTML and related downloadable images. |
| 104 | `def write_preview(report, raw, subtype, destination):` | Define write_preview: Render a self-contained HTML file to destination; intended for explicit local preview only. |
| 105 | `"""Render a self-contained HTML file to destination; intended for explicit local preview only."""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 106 | `charts = render_charts(report)` | Store the displayed expression in `charts` to save an explicit local preview without sending. |
| 107 | `sources = {name + "_image": "data:image/png;base64," + base64.b64encode(image).decode("ascii") for name, image in charts.items()}` | Store the displayed expression in `sources` to save an explicit local preview without sending. |
| 108 | `sources["meal_image"] = f"data:image/{subtype};base64," + base64.b64encode(raw).decode("ascii")` | Store the displayed expression in `sources['meal_image']` to save an explicit local preview without sending. |
| 109 | `destination = Path(destination)` | Store the displayed expression in `destination` to save an explicit local preview without sending. |
| 110 | `destination.parent.mkdir(parents=True, exist_ok=True)` | Call `destination.parent.mkdir` to save an explicit local preview without sending. |
| 111 | `destination.write_text(html_body(report, sources), encoding="utf-8")` | Write this explicitly requested local preview/artifact as UTF-8. |

## chart_renderer.ps1

| Line | Source | Explanation |
| --- | --- | --- |
| 1 | `# Render two email-safe PNG charts using Windows' built-in drawing library.` | Explain the purpose of the renderer. |
| 2 | `$ErrorActionPreference = 'Stop'` | Make renderer errors terminate the operation so Python cannot report a successful visual email with missing charts. |
| 3 | `Add-Type -AssemblyName System.Drawing` | Load Windows System.Drawing without package installation. |
| 4 | `$payload = [Console]::In.ReadToEnd() &#124; ConvertFrom-Json` | Read drawing data from standard input as JSON; the payload is not executed as PowerShell. |
| 5 | `$outputs = @{}` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 6 | `function Colour($hex) { [System.Drawing.ColorTranslator]::FromHtml($hex) }` | Define a local drawing helper for colours, text, rectangles, lines or axis-coordinate conversion. |
| 7 | `function Text($value, $x, $y, $size = 23, $hex = '#334155') {` | Define a local drawing helper for colours, text, rectangles, lines or axis-coordinate conversion. |
| 8 | `$font = [System.Drawing.Font]::new('Arial', [single]$size, [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Pixel)` | Create or configure the indicated drawing object; its matched finally block releases it. |
| 9 | `$brush = [System.Drawing.SolidBrush]::new((Colour $hex))` | Create or configure the indicated drawing object; its matched finally block releases it. |
| 10 | `try { $g.DrawString([string]$value, $font, $brush, [single]$x, [single]$y) }` | Draw the displayed chart label using the specified position, font size and colour. |
| 11 | `finally { $font.Dispose(); $brush.Dispose() }` | Release drawing objects or memory streams even on failure, avoiding resource leaks across email requests. |
| 12 | `}` | Close or select the surrounding rendering branch; this structural line adds no measurement or external side effect. |
| 13 | `function Box($x, $y, $width, $height, $hex) {` | Define a local drawing helper for colours, text, rectangles, lines or axis-coordinate conversion. |
| 14 | `$brush = [System.Drawing.SolidBrush]::new((Colour $hex))` | Create or configure the indicated drawing object; its matched finally block releases it. |
| 15 | `try { $g.FillRectangle($brush, [single]$x, [single]$y, [single]$width, [single]$height) }` | Draw the indicated food bar or background rectangle using chart-scaled gram quantities. |
| 16 | `finally { $brush.Dispose() }` | Release drawing objects or memory streams even on failure, avoiding resource leaks across email requests. |
| 17 | `}` | Close or select the surrounding rendering branch; this structural line adds no measurement or external side effect. |
| 18 | `function Line($x1, $y1, $x2, $y2, $hex, $width = 3, $dashed = $false) {` | Define a local drawing helper for colours, text, rectangles, lines or axis-coordinate conversion. |
| 19 | `$pen = [System.Drawing.Pen]::new((Colour $hex), [single]$width)` | Create or configure the indicated drawing object; its matched finally block releases it. |
| 20 | `if ($dashed) { $pen.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Dash }` | Check the displayed drawing condition so absent readings, curve bands and chart placement are handled explicitly. |
| 21 | `try { $g.DrawLine($pen, [single]$x1, [single]$y1, [single]$x2, [single]$y2) }` | Draw the specified measured/forecast segment, reference line or range whisker; dashed styling distinguishes demo forecasts. |
| 22 | `finally { $pen.Dispose() }` | Release drawing objects or memory streams even on failure, avoiding resource leaks across email requests. |
| 23 | `}` | Close or select the surrounding rendering branch; this structural line adds no measurement or external side effect. |
| 24 | `foreach ($kind in @('glucose', 'food')) {` | Iterate the displayed graph types, points, ticks, reference values or food rows to render all supplied data. |
| 25 | `$bitmap = [System.Drawing.Bitmap]::new(1200, 480)` | Create or configure the indicated drawing object; its matched finally block releases it. |
| 26 | `$g = [System.Drawing.Graphics]::FromImage($bitmap)` | Create or configure the indicated drawing object; its matched finally block releases it. |
| 27 | `$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias` | Create or configure the indicated drawing object; its matched finally block releases it. |
| 28 | `$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit` | Create or configure the indicated drawing object; its matched finally block releases it. |
| 29 | `$g.Clear([System.Drawing.Color]::White)` | Create or configure the indicated drawing object; its matched finally block releases it. |
| 30 | `try {` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 31 | `if ($kind -eq 'glucose') {` | Check the displayed drawing condition so absent readings, curve bands and chart placement are handled explicitly. |
| 32 | `Text 'GLUCOSE HISTORY + DEMO FORECAST' 30 12 26 '#142D48'` | Draw the displayed chart label using the specified position, font size and colour. |
| 33 | `Text 'mg/dL' 30 52 20` | Draw the displayed chart label using the specified position, font size and colour. |
| 34 | `$minX = [double]$payload.min_x` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 35 | `$maxX = [double]$payload.max_x` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 36 | `$maxY = [double]$payload.max_y` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 37 | `function Px($value) { 90 + 1050 * ([double]$value - $minX) / ($maxX - $minX) }` | Define a local drawing helper for colours, text, rectangles, lines or axis-coordinate conversion. |
| 38 | `function Py($value) { 370 - 275 * [double]$value / $maxY }` | Define a local drawing helper for colours, text, rectangles, lines or axis-coordinate conversion. |
| 39 | `for ($i = 0; $i -le 4; $i++) {` | Iterate the displayed graph types, points, ticks, reference values or food rows to render all supplied data. |
| 40 | `$value = $i * $maxY / 4` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 41 | `$y = Py $value` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 42 | `Line 90 $y 1140 $y '#E2E8F0' 1` | Draw the specified measured/forecast segment, reference line or range whisker; dashed styling distinguishes demo forecasts. |
| 43 | `Text ([math]::Round($value)) 24 ($y - 14) 20` | Draw the displayed chart label using the specified position, font size and colour. |
| 44 | `}` | Close or select the surrounding rendering branch; this structural line adds no measurement or external side effect. |
| 45 | `foreach ($reference in @(70, 180)) {` | Iterate the displayed graph types, points, ticks, reference values or food rows to render all supplied data. |
| 46 | `$y = Py $reference` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 47 | `Line 90 $y 1140 $y '#CBD5E1' 2 $true` | Draw the specified measured/forecast segment, reference line or range whisker; dashed styling distinguishes demo forecasts. |
| 48 | `}` | Close or select the surrounding rendering branch; this structural line adds no measurement or external side effect. |
| 49 | `$forecast = @($payload.forecast)` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 50 | `$polygon = [System.Collections.Generic.List[System.Drawing.PointF]]::new()` | Create or configure the indicated drawing object; its matched finally block releases it. |
| 51 | `foreach ($point in $forecast) { $polygon.Add([System.Drawing.PointF]::new((Px $point.x), (Py $point.high))) }` | Iterate the displayed graph types, points, ticks, reference values or food rows to render all supplied data. |
| 52 | `for ($i = $forecast.Count - 1; $i -ge 0; $i--) { $polygon.Add([System.Drawing.PointF]::new((Px $forecast[$i].x), (Py $forecast[$i].low))) }` | Iterate the displayed graph types, points, ticks, reference values or food rows to render all supplied data. |
| 53 | `if ($polygon.Count -ge 3) {` | Check the displayed drawing condition so absent readings, curve bands and chart placement are handled explicitly. |
| 54 | `$brush = [System.Drawing.SolidBrush]::new((Colour '#EDE5FF'))` | Create or configure the indicated drawing object; its matched finally block releases it. |
| 55 | `try { $g.FillPolygon($brush, $polygon.ToArray()) } finally { $brush.Dispose() }` | Release drawing objects or memory streams even on failure, avoiding resource leaks across email requests. |
| 56 | `}` | Close or select the surrounding rendering branch; this structural line adds no measurement or external side effect. |
| 57 | `$points = @($payload.measured)` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 58 | `for ($i = 1; $i -lt $points.Count; $i++) {` | Iterate the displayed graph types, points, ticks, reference values or food rows to render all supplied data. |
| 59 | `Line (Px $points[$i-1].x) (Py $points[$i-1].y) (Px $points[$i].x) (Py $points[$i].y) '#167D8D' 4` | Draw the specified measured/forecast segment, reference line or range whisker; dashed styling distinguishes demo forecasts. |
| 60 | `}` | Close or select the surrounding rendering branch; this structural line adds no measurement or external side effect. |
| 61 | `foreach ($point in $points) {` | Iterate the displayed graph types, points, ticks, reference values or food rows to render all supplied data. |
| 62 | `$brush = [System.Drawing.SolidBrush]::new((Colour '#167D8D'))` | Create or configure the indicated drawing object; its matched finally block releases it. |
| 63 | `try { $g.FillEllipse($brush, [single]((Px $point.x)-5), [single]((Py $point.y)-5), 10, 10) } finally { $brush.Dispose() }` | Release drawing objects or memory streams even on failure, avoiding resource leaks across email requests. |
| 64 | `}` | Close or select the surrounding rendering branch; this structural line adds no measurement or external side effect. |
| 65 | `if ($points.Count -gt 0) {` | Check the displayed drawing condition so absent readings, curve bands and chart placement are handled explicitly. |
| 66 | `$point = $points[-1]` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 67 | `Text ([string]$point.y) ([math]::Min(1040, (Px $point.x)+8)) ([math]::Max(65, (Py $point.y)-32)) 24 '#245FE8'` | Draw the displayed chart label using the specified position, font size and colour. |
| 68 | `} else { Text 'No measured history supplied' 100 120 24 '#AD6600' }` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 69 | `for ($i = 1; $i -lt $forecast.Count; $i++) {` | Iterate the displayed graph types, points, ticks, reference values or food rows to render all supplied data. |
| 70 | `Line (Px $forecast[$i-1].x) (Py $forecast[$i-1].y) (Px $forecast[$i].x) (Py $forecast[$i].y) '#8055CF' 4 $true` | Draw the specified measured/forecast segment, reference line or range whisker; dashed styling distinguishes demo forecasts. |
| 71 | `}` | Close or select the surrounding rendering branch; this structural line adds no measurement or external side effect. |
| 72 | `foreach ($point in $forecast) { Text ([string]$point.y) ((Px $point.x)-16) ((Py $point.y)-30) 21 '#8055CF' }` | Iterate the displayed graph types, points, ticks, reference values or food rows to render all supplied data. |
| 73 | `$nowX = Px $payload.now` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 74 | `Line $nowX 78 $nowX 370 '#64748B' 2 $true` | Draw the specified measured/forecast segment, reference line or range whisker; dashed styling distinguishes demo forecasts. |
| 75 | `Text 'NOW' ([math]::Min(1070, $nowX+6)) 58 19 '#64748B'` | Draw the displayed chart label using the specified position, font size and colour. |
| 76 | `foreach ($tick in $payload.ticks) { Text $tick.label ([math]::Min(1000, [math]::Max(70, (Px $tick.x)-58))) 385 18 }` | Iterate the displayed graph types, points, ticks, reference values or food rows to render all supplied data. |
| 77 | `Text 'Measured / latest' 90 435 21 '#167D8D'` | Draw the displayed chart label using the specified position, font size and colour. |
| 78 | `Text 'Dashed: fixed demo forecast' 360 435 21 '#8055CF'` | Draw the displayed chart label using the specified position, font size and colour. |
| 79 | `Text 'Shading: illustrative range' 780 435 21 '#8055CF'` | Draw the displayed chart label using the specified position, font size and colour. |
| 80 | `} else {` | Close or select the surrounding rendering branch; this structural line adds no measurement or external side effect. |
| 81 | `Text 'FOOD ESTIMATES - SIMULATED' 30 12 26 '#142D48'` | Draw the displayed chart label using the specified position, font size and colour. |
| 82 | `Text 'Estimated grams and illustrative uncertainty ranges' 30 55 22` | Draw the displayed chart label using the specified position, font size and colour. |
| 83 | `$scale = 850 / [double]$payload.food_max` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 84 | `$row = 0` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 85 | `foreach ($item in $payload.food) {` | Iterate the displayed graph types, points, ticks, reference values or food rows to render all supplied data. |
| 86 | `$top = 112 + $row * 140` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 87 | `Text ($item.label + ': ' + $item.estimate + ' g') 35 $top 27 '#142D48'` | Draw the displayed chart label using the specified position, font size and colour. |
| 88 | `Box 35 ($top+47) 850 30 '#F1F5F9'` | Draw the indicated food bar or background rectangle using chart-scaled gram quantities. |
| 89 | `Box 35 ($top+47) ($item.estimate*$scale) 30 $item.color` | Draw the indicated food bar or background rectangle using chart-scaled gram quantities. |
| 90 | `Line (35+$item.low*$scale) ($top+91) (35+$item.high*$scale) ($top+91) '#64748B' 3` | Draw the specified measured/forecast segment, reference line or range whisker; dashed styling distinguishes demo forecasts. |
| 91 | `Line (35+$item.low*$scale) ($top+83) (35+$item.low*$scale) ($top+99) '#64748B' 3` | Draw the specified measured/forecast segment, reference line or range whisker; dashed styling distinguishes demo forecasts. |
| 92 | `Line (35+$item.high*$scale) ($top+83) (35+$item.high*$scale) ($top+99) '#64748B' 3` | Draw the specified measured/forecast segment, reference line or range whisker; dashed styling distinguishes demo forecasts. |
| 93 | `Text ($item.low.ToString() + ' to ' + $item.high + ' g') 915 ($top+45) 23` | Draw the displayed chart label using the specified position, font size and colour. |
| 94 | `$row++` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 95 | `}` | Close or select the surrounding rendering branch; this structural line adds no measurement or external side effect. |
| 96 | `Text 'Sugar is included in total carbohydrates; do not add the two bars.' 35 420 22 '#64748B'` | Draw the displayed chart label using the specified position, font size and colour. |
| 97 | `}` | Close or select the surrounding rendering branch; this structural line adds no measurement or external side effect. |
| 98 | `$stream = [System.IO.MemoryStream]::new()` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 99 | `try {` | Calculate/store the displayed chart coordinate, scale, point, label or drawing state for the next rendering operation. |
| 100 | `$bitmap.Save($stream, [System.Drawing.Imaging.ImageFormat]::Png)` | Encode the completed chart as PNG into an in-memory stream for email compatibility. |
| 101 | `$outputs[$kind] = [Convert]::ToBase64String($stream.ToArray())` | Encode the PNG bytes to return to Python without an intermediate image file. |
| 102 | `} finally { $stream.Dispose() }` | Release drawing objects or memory streams even on failure, avoiding resource leaks across email requests. |
| 103 | `} finally { $g.Dispose(); $bitmap.Dispose() }` | Release drawing objects or memory streams even on failure, avoiding resource leaks across email requests. |
| 104 | `}` | Close or select the surrounding rendering branch; this structural line adds no measurement or external side effect. |
| 105 | `$outputs &#124; ConvertTo-Json -Compress` | Return both encoded chart images as a compact JSON object on stdout. |

## email_template.html

| Line | Source | Explanation |
| --- | --- | --- |
| 1 | `<!doctype html>` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 2 | `<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Caregiver meal update</title></head>` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 3 | `<body style="margin:0;background:#EDF2F7;font-family:Arial,Helvetica,sans-serif;color:#24364B">` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 4 | `<table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr><td align="center" style="padding:24px 10px">` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 5 | `<table role="presentation" width="700" cellspacing="0" cellpadding="0" style="width:100%;max-width:700px;background:#FFFFFF;border-radius:14px">` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 6 | `<tr><td style="padding:26px 28px;background:#142D48;color:#FFFFFF;border-radius:14px 14px 0 0">` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 7 | `<p style="margin:0 0 8px;font-size:12px;letter-spacing:2px;color:#B8CEE2">CARE COMPANION · PROTOTYPE</p>` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 8 | `<h1 style="margin:0;font-size:28px">Your caregiver update</h1><p style="margin:10px 0 0;color:#D7E3EE">$patient · Prepared $prepared</p></td></tr>` | Place the displayed report fields through escaped template placeholders; inline CSS and presentation tables support email clients without scripts. |
| 9 | `<tr><td style="padding:24px 28px 0">` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 10 | `<table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr><td style="padding:20px;background:$background;border-left:6px solid $color">` | Place the displayed report fields through escaped template placeholders; inline CSS and presentation tables support email clients without scripts. |
| 11 | `<p style="margin:0 0 8px;font-size:12px;font-weight:bold;color:$color">CAREGIVER ACTION · $level</p>` | Lead with the action/severity label and its selected colour; dynamic values are escaped by html_body before substitution. |
| 12 | `<h2 style="margin:0;font-size:25px;color:$color">$action_title</h2><p style="margin:12px 0 0;line-height:1.6">$action_detail</p></td></tr></table>` | Lead with the action/severity label and its selected colour; dynamic values are escaped by html_body before substitution. |
| 13 | `<p style="font-size:12px;color:#64748B;line-height:1.6">Colour key: red = urgent help · amber = check / review · teal = continue monitoring. Screening is based on supplied readings and symptoms; personal care plans take priority.</p>` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 14 | `</td></tr>` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 15 | `<tr><td style="padding:4px 28px 20px">` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 16 | `<table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr>` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 17 | `<td width="50%" valign="top" style="padding:16px;background:#F3F7FB"><p style="margin:0;color:#64748B;font-size:12px">LATEST RECORDED GLUCOSE</p><p style="margin:10px 0;font-size:30px;font-weight:bold;color:#142D48">$current</p><p style="margin:0;font-size:12px;line-height:1.6">$measured_at<br>$freshness</p></td>` | Place the displayed report fields through escaped template placeholders; inline CSS and presentation tables support email clients without scripts. |
| 18 | `<td width="50%" valign="top" style="padding:16px;background:#F4EFFF"><p style="margin:0;color:#7050A5;font-size:12px">+30 MIN DEMO FORECAST</p><p style="margin:10px 0;font-size:30px;font-weight:bold;color:#7050A5">$forecast_value</p><p style="margin:0;font-size:12px;line-height:1.6">Illustrative range: 110–210<br>Fixed example · unvalidated</p></td>` | Place the displayed report fields through escaped template placeholders; inline CSS and presentation tables support email clients without scripts. |
| 19 | `</tr></table>` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 20 | `<table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr><td style="padding:16px 0;border-bottom:1px solid #E2E8F0"><b>Sugar: more or less?</b><p style="margin:7px 0 0;line-height:1.6">$sugar_action</p></td></tr><tr><td style="padding:16px 0"><b>Do we need medical help?</b><p style="margin:7px 0 0;line-height:1.6">$doctor_action</p></td></tr></table>` | Place the displayed report fields through escaped template placeholders; inline CSS and presentation tables support email clients without scripts. |
| 21 | `</td></tr>` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 22 | `<tr><td style="padding:0 28px 22px"><h2 style="margin:0 0 8px;font-size:21px">Glucose: previous, latest and future</h2>` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 23 | `<p style="font-size:13px;line-height:1.6;color:#64748B">$history_note. All chart values use mg/dL; times use Hong Kong time (UTC+08:00).</p>` | Place the displayed report fields through escaped template placeholders; inline CSS and presentation tables support email clients without scripts. |
| 24 | `<img src="$glucose_image" alt="Glucose history and latest reading, with a dashed purple simulated forecast and illustrative range." width="644" style="display:block;width:100%;height:auto;border:1px solid #E2E8F0">` | Embed the indicated PNG/photo resource with responsive sizing and descriptive alt text. Email uses CID references; local preview uses data URLs. |
| 25 | `<p style="font-size:12px;color:#64748B;line-height:1.6">The dashed forecast and shaded range are fixed demo values. They do not drive alerts. Horizontal 70/180 reference lines are illustrative; individual targets vary. Missing history is not filled in.</p>` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 26 | `<p style="font-size:13px;line-height:1.6">$history_values</p></td></tr>` | Place the displayed report fields through escaped template placeholders; inline CSS and presentation tables support email clients without scripts. |
| 27 | `<tr><td style="padding:0 28px 24px"><h2 style="margin:0 0 12px;font-size:21px">Meal photo and food analysis</h2>` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 28 | `<img src="$meal_image" alt="Original supplied meal photograph" width="644" style="display:block;width:100%;max-height:460px;object-fit:contain;background:#F8FAFC;border-radius:8px">` | Embed the indicated PNG/photo resource with responsive sizing and descriptive alt text. Email uses CID references; local preview uses data URLs. |
| 29 | `<p style="font-size:12px;color:#64748B">Meal time: $meal_time · $food_source</p>` | Place the displayed report fields through escaped template placeholders; inline CSS and presentation tables support email clients without scripts. |
| 30 | `<img src="$food_image" alt="Simulated total carbohydrates 60 grams, range 40–85; sugar 12 grams, range 6–20. Sugar is part of total carbohydrates." width="644" style="display:block;width:100%;height:auto;border:1px solid #E2E8F0">` | Embed the indicated PNG/photo resource with responsive sizing and descriptive alt text. Email uses CID references; local preview uses data URLs. |
| 31 | `<p style="font-size:13px;line-height:1.6">Total carbohydrates: <b>60 g</b> (40–85 g) · Sugar: <b>12 g</b> (6–20 g). Both are fixed demo estimates, independent of the photo. Sugar is included within total carbohydrates.</p></td></tr>` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 32 | `<tr><td style="padding:0 28px 24px"><h2 style="font-size:21px;margin:0 0 10px">Caregiver notes</h2><p style="line-height:1.7;margin:0">$suggestions</p></td></tr>` | Place the displayed report fields through escaped template placeholders; inline CSS and presentation tables support email clients without scripts. |
| 33 | `<tr><td style="padding:22px 28px;background:#F3F7FB;border-radius:0 0 14px 14px"><b style="font-size:13px">About this prototype</b><p style="font-size:12px;line-height:1.7">$warning</p>` | Place the displayed report fields through escaped template placeholders; inline CSS and presentation tables support email clients without scripts. |
| 34 | `<p style="font-size:12px;line-height:1.7">No insulin timing or dose advice. Severe symptoms require help regardless of the colour shown here. Email is not an emergency monitoring channel.</p>` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |
| 35 | `<p style="font-size:11px;line-height:1.6"><a href="https://www.cdc.gov/diabetes/treatment/treatment-low-blood-sugar-hypoglycemia.html">Low-glucose guidance</a> · <a href="https://www.cdc.gov/diabetes/about/diabetic-ketoacidosis.html">High-glucose emergency signs</a></p></td></tr>` | Link to the primary CDC guidance supporting low-glucose and high-glucose screening explanations. |
| 36 | `</table></td></tr></table></body></html>` | Build the displayed heading, explanatory text or containing email table/document structure with inline styling. |

## test_visual_email.py

| Line | Source | Explanation |
| --- | --- | --- |
| 1 | `"""Verify action screening, history inputs, HTML escaping and embedded chart rendering."""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 3 | `import copy` | Import copy to support the visual caregiver email. |
| 4 | `import json` | Import json to support the visual caregiver email. |
| 5 | `import struct` | Import struct to support the visual caregiver email. |
| 6 | `import tempfile` | Import tempfile to support the visual caregiver email. |
| 7 | `import unittest` | Import unittest to support the visual caregiver email. |
| 8 | `from datetime import datetime, timedelta, timezone` | Import datetime, timedelta, timezone to support the visual caregiver email. |
| 9 | `from pathlib import Path` | Import Path to support the visual caregiver email. |
| 11 | `import run_demo` | Import run_demo to support the visual caregiver email. |
| 12 | `import server` | Import server to support the visual caregiver email. |
| 13 | `import visual_email` | Import visual_email to support the visual caregiver email. |
| 14 | `from caregiver_view import caregiver_summary` | Import caregiver_summary to support the visual caregiver email. |
| 15 | `from test_pipeline import EVENT, PNG` | Import EVENT, PNG to support the visual caregiver email. |
| 17 | `NOW = datetime(2026, 11, 13, 8, 0, tzinfo=timezone.utc)` | Store the displayed expression in `NOW` to support the visual caregiver email. |
| 20 | `class VisualEmailTests(unittest.TestCase):` | Define VisualEmailTests: Check the measured-data/forecast boundary before any email is sent. |
| 21 | `"""Check the measured-data/forecast boundary before any email is sent."""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 23 | `def event(self, value=120, minutes_old=0, unit="mg/dL"):` | Define event: Build a valid synthetic test fixture without labelling it as a demo scenario. |
| 24 | `"""Build a valid synthetic test fixture without labelling it as a demo scenario."""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 25 | `payload = copy.deepcopy(EVENT)` | Store the displayed expression in `payload` to support the visual caregiver email. |
| 26 | `payload["glucose"] = {"value": value, "unit": unit, "measured_at": (NOW-timedelta(minutes=minutes_old)).isoformat()}` | Store the displayed expression in `payload['glucose']` to support the visual caregiver email. |
| 27 | `return server.validate_event(payload)[0]` | Return the constructed value to the caller to support the visual caregiver email. |
| 29 | `def test_thresholds_use_fresh_measurements(self):` | Define test_thresholds_use_fresh_measurements: verify the documented behaviour under isolated test conditions |
| 30 | `for value, level in ((54, "urgent"), (55, "review"), (69, "review"), (70, "monitor"), (180, "monitor"), (181, "review"), (250, "review")):` | Iterate `((54, 'urgent'), (55, 'review'), (69, 'review'), (70, 'monitor'), (180, 'monitor'), (181, 'review'), (250, 'review'))` as `(value, level)` to verify the documented behaviour under isolated test conditions. |
| 31 | `with self.subTest(value=value):` | Enter the temporary test context so mock settings/resources are restored on exit. |
| 32 | `self.assertEqual(caregiver_summary(self.event(value), NOW)["level"], level)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 34 | `def test_missing_stale_future_and_synthetic_cannot_be_monitor(self):` | Define test_missing_stale_future_and_synthetic_cannot_be_monitor: verify the documented behaviour under isolated test conditions |
| 35 | `events = [self.event(minutes_old=16), self.event(minutes_old=-1)]` | Store the displayed expression in `events` to verify the documented behaviour under isolated test conditions. |
| 36 | `missing = self.event()` | Store the displayed expression in `missing` to verify the documented behaviour under isolated test conditions. |
| 37 | `missing["glucose"] = None` | Store the displayed expression in `missing['glucose']` to verify the documented behaviour under isolated test conditions. |
| 38 | `events.append(missing)` | Call `events.append` to verify the documented behaviour under isolated test conditions. |
| 39 | `synthetic = self.event(50)` | Store the displayed expression in `synthetic` to verify the documented behaviour under isolated test conditions. |
| 40 | `synthetic["synthetic"] = True` | Store the displayed expression in `synthetic['synthetic']` to verify the documented behaviour under isolated test conditions. |
| 41 | `events.append(synthetic)` | Call `events.append` to verify the documented behaviour under isolated test conditions. |
| 42 | `for event in events:` | Iterate `events` as `event` to verify the documented behaviour under isolated test conditions. |
| 43 | `self.assertEqual(caregiver_summary(event, NOW)["level"], "review")` | Require the displayed expected value/property; fail the regression test if it changes. |
| 45 | `def test_severe_symptoms_override_missing_reading(self):` | Define test_severe_symptoms_override_missing_reading: verify the documented behaviour under isolated test conditions |
| 46 | `event = self.event()` | Store the displayed expression in `event` to verify the documented behaviour under isolated test conditions. |
| 47 | `event.update(glucose=None, severe_symptoms=True)` | Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 48 | `self.assertEqual(caregiver_summary(event, NOW)["level"], "urgent")` | Require the displayed expected value/property; fail the regression test if it changes. |
| 50 | `def test_repeat_high_and_unit_conversion(self):` | Define test_repeat_high_and_unit_conversion: verify the documented behaviour under isolated test conditions |
| 51 | `event = self.event(305)` | Store the displayed expression in `event` to verify the documented behaviour under isolated test conditions. |
| 52 | `event["glucose_history"] = [{"value": 310, "unit": "mg/dL", "measured_at": (NOW-timedelta(minutes=30)).isoformat()}]` | Store the displayed expression in `event['glucose_history']` to verify the documented behaviour under isolated test conditions. |
| 53 | `self.assertEqual(caregiver_summary(event, NOW)["level"], "urgent")` | Require the displayed expected value/property; fail the regression test if it changes. |
| 54 | `self.assertEqual(caregiver_summary(self.event(3, unit="mmol/L"), NOW)["level"], "urgent")` | Require the displayed expected value/property; fail the regression test if it changes. |
| 56 | `def test_history_file_and_legacy_input_both_work(self):` | Define test_history_file_and_legacy_input_both_work: verify the documented behaviour under isolated test conditions |
| 57 | `with tempfile.TemporaryDirectory() as directory:` | Enter the temporary test context so mock settings/resources are restored on exit. |
| 58 | `image, glucose = Path(directory)/"meal.png", Path(directory)/"glucose.json"` | Store the displayed expression in `(image, glucose)` to verify the documented behaviour under isolated test conditions. |
| 59 | `image.write_bytes(PNG)` | Call `image.write_bytes` to verify the documented behaviour under isolated test conditions. |
| 60 | `current = self.event()["glucose"]` | Store the displayed expression in `current` to verify the documented behaviour under isolated test conditions. |
| 61 | `history = [self.event(110, minutes_old=30)["glucose"]]` | Store the displayed expression in `history` to verify the documented behaviour under isolated test conditions. |
| 62 | `glucose.write_text(json.dumps({"current": current, "history": history, "synthetic": True}))` | Write this explicitly requested local preview/artifact as UTF-8. |
| 63 | `event, raw, subtype = run_demo.read_event(image, glucose, "demo")` | Store the displayed expression in `(event, raw, subtype)` to verify the documented behaviour under isolated test conditions. |
| 64 | `self.assertEqual(event["glucose_history"], history)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 65 | `self.assertTrue(event["synthetic"])` | Require the displayed expected value/property; fail the regression test if it changes. |
| 66 | `glucose.write_text(json.dumps(current))` | Write this explicitly requested local preview/artifact as UTF-8. |
| 67 | `self.assertEqual(run_demo.read_event(image, glucose, "demo")[0]["glucose"], current)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 69 | `def test_bad_history_and_flags_rejected(self):` | Define test_bad_history_and_flags_rejected: verify the documented behaviour under isolated test conditions |
| 70 | `for patch in ({"glucose_history": "wrong"}, {"glucose_history": [{}]}, {"severe_symptoms": "yes"}, {"synthetic": 1}):` | Iterate `({'glucose_history': 'wrong'}, {'glucose_history': [{}]}, {'severe_symptoms': 'yes'}, {'synthetic': 1})` as `patch` to verify the documented behaviour under isolated test conditions. |
| 71 | `with self.subTest(patch=patch), self.assertRaises(ValueError):` | Enter the temporary test context so mock settings/resources are restored on exit. |
| 72 | `server.validate_event(dict(EVENT, **patch))` | Call `server.validate_event` to verify the documented behaviour under isolated test conditions. |
| 74 | `def test_forecast_is_not_used_for_alert_and_html_is_escaped(self):` | Define test_forecast_is_not_used_for_alert_and_html_is_escaped: verify the documented behaviour under isolated test conditions |
| 75 | `event = self.event()` | Store the displayed expression in `event` to verify the documented behaviour under isolated test conditions. |
| 76 | `event["patient_id"] = '<script>alert("x")</script>'` | Store the displayed expression in `event['patient_id']` to verify the documented behaviour under isolated test conditions. |
| 77 | `report = server.analyze(event, PNG)` | Store the displayed expression in `report` to verify the documented behaviour under isolated test conditions. |
| 78 | `report["caregiver_action"] = caregiver_summary(event, NOW)` | Store the displayed expression in `report['caregiver_action']` to verify the documented behaviour under isolated test conditions. |
| 79 | `report["estimated_current_glucose"]["estimate"] = 10` | Store the displayed expression in `report['estimated_current_glucose']['estimate']` to verify the documented behaviour under isolated test conditions. |
| 80 | `html = visual_email.html_body(report, {"glucose_image": "cid:g", "food_image": "cid:f", "meal_image": "cid:m"})` | Store the displayed expression in `html` to verify the documented behaviour under isolated test conditions. |
| 81 | `self.assertNotIn("<script>", html)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 82 | `self.assertIn("&lt;script&gt;", html)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 83 | `self.assertEqual(report["caregiver_action"]["level"], "monitor")` | Require the displayed expected value/property; fail the regression test if it changes. |
| 84 | `self.assertIn("No threshold alert", html)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 86 | `def test_actual_chart_pngs_and_mixed_units(self):` | Define test_actual_chart_pngs_and_mixed_units: verify the documented behaviour under isolated test conditions |
| 87 | `event = self.event(7.2, unit="mmol/L")` | Store the displayed expression in `event` to verify the documented behaviour under isolated test conditions. |
| 88 | `report = server.analyze(event, PNG)` | Store the displayed expression in `report` to verify the documented behaviour under isolated test conditions. |
| 89 | `self.assertAlmostEqual(visual_email.chart_data(report)["measured"][0]["y"], 129.7, places=1)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 90 | `for png in visual_email.render_charts(report).values():` | Iterate `visual_email.render_charts(report).values()` as `png` to verify the documented behaviour under isolated test conditions. |
| 91 | `self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))` | Require the displayed expected value/property; fail the regression test if it changes. |
| 92 | `self.assertEqual(struct.unpack(">II", png[16:24]), (1200, 480))` | Require the displayed expected value/property; fail the regression test if it changes. |
| 95 | `if __name__ == "__main__":` | Check `__name__ == '__main__'`; execute this branch when true to support the visual caregiver email. |
| 96 | `unittest.main()` | Call `unittest.main` to support the visual caregiver email. |

## email_report.py

| Line | Source | Explanation |
| --- | --- | --- |
| 1 | `"""Turn the internal demo report into a readable plain-text caregiver email."""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 3 | `from datetime import datetime` | Import datetime to support the visual caregiver email. |
| 4 | `from textwrap import fill` | Import fill to support the visual caregiver email. |
| 7 | `def format_email_report(report):` | Define format_email_report: Validated analysis dict -> plain-text email body; no files, network or mutations. |
| 8 | `"""Validated analysis dict -> plain-text email body; no files, network or mutations.` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 10 | `Preserve measured values and units; label every predicted value as simulated.` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 11 | `Format timezone-qualified ISO timestamps with their original UTC offsets.` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 12 | `"""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 13 | `def display_time(value):` | Define display_time: ISO timestamp string -> readable date/time with its numeric UTC offset. |
| 14 | `"""ISO timestamp string -> readable date/time with its numeric UTC offset."""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 15 | `return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%d %b %Y, %H:%M (UTC%z)")` | Return the constructed value to the caller to support the visual caregiver email. |
| 17 | `def estimate_line(label, item, unit):` | Define estimate_line: Label, estimate/range dict and unit string -> one readable estimate line. |
| 18 | `"""Label, estimate/range dict and unit string -> one readable estimate line."""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 19 | `low, high = item["illustrative_range"]` | Store the displayed expression in `(low, high)` to support the visual caregiver email. |
| 20 | `return f"{label}: {item['estimate']:g} {unit} (illustrative range: {low:g} to {high:g} {unit})"` | Return the constructed value to the caller to support the visual caregiver email. |
| 22 | `original = report["original_information"]` | Store the displayed expression in `original` to retain a readable text alternative with the same action summary. |
| 23 | `reading = original["glucose"]` | Store the displayed expression in `reading` to retain a readable text alternative with the same action summary. |
| 24 | `measured = "No measured glucose reading was provided."` | Store the displayed expression in `measured` to retain a readable text alternative with the same action summary. |
| 25 | `if reading is not None:` | Check `reading is not None`; execute this branch when true to retain a readable text alternative with the same action summary. |
| 26 | `measured = (f"Measured glucose: {reading['value']:g} {reading['unit']}\n"` | Store the displayed expression in `measured` to retain a readable text alternative with the same action summary. |
| 27 | `f"Measurement time: {display_time(reading['measured_at'])}")` | Continue the multiline statement: Store the displayed expression in `measured` to retain a readable text alternative with the same action summary. |
| 28 | `food = report["food"]` | Store the displayed expression in `food` to retain a readable text alternative with the same action summary. |
| 29 | `glucose = report["estimated_current_glucose"]` | Store the displayed expression in `glucose` to retain a readable text alternative with the same action summary. |
| 30 | `sections = [` | Store the displayed expression in `sections` to retain a readable text alternative with the same action summary. |
| 31 | `"MEAL AND GLUCOSE REPORT\nSIMULATED DEMONSTRATION",` | Continue the multiline statement: Store the displayed expression in `sections` to retain a readable text alternative with the same action summary. |
| 32 | `f"Patient: {original['patient_id']}\nMeal recorded at: {display_time(original['meal_captured_at'])}",` | Continue the multiline statement: Store the displayed expression in `sections` to retain a readable text alternative with the same action summary. |
| 33 | `"RECORDED GLUCOSE\n" + measured,` | Continue the multiline statement: Store the displayed expression in `sections` to retain a readable text alternative with the same action summary. |
| 34 | `"SIMULATED FOOD ESTIMATES\n" + estimate_line("Sugar", food["sugar_g"], "g") + "\n"` | Continue the multiline statement: Store the displayed expression in `sections` to retain a readable text alternative with the same action summary. |
| 35 | `+ estimate_line("Total carbohydrates", food["carbohydrate_g"], "g"),` | Continue the multiline statement: Store the displayed expression in `sections` to retain a readable text alternative with the same action summary. |
| 36 | `"SIMULATED CURRENT GLUCOSE\n" + estimate_line("Estimated glucose", glucose, glucose["unit"])` | Continue the multiline statement: Store the displayed expression in `sections` to retain a readable text alternative with the same action summary. |
| 37 | `+ "\nThis is a fixed demo example, not a measured reading or a validated prediction.",` | Continue the multiline statement: Store the displayed expression in `sections` to retain a readable text alternative with the same action summary. |
| 38 | `"CAREGIVER NOTES\n" + fill(report["suggestions"], width=78),` | Continue the multiline statement: Store the displayed expression in `sections` to retain a readable text alternative with the same action summary. |
| 39 | `"MEAL PHOTO\nSee the attached meal image.",` | Continue the multiline statement: Store the displayed expression in `sections` to retain a readable text alternative with the same action summary. |
| 40 | `"IMPORTANT LIMITATIONS\n" + fill(report["warning"], width=78),` | Continue the multiline statement: Store the displayed expression in `sections` to retain a readable text alternative with the same action summary. |
| 41 | `]` | Continue the multiline statement: Store the displayed expression in `sections` to retain a readable text alternative with the same action summary. |
| 42 | `if "caregiver_action" in report:` | Check `'caregiver_action' in report`; execute this branch when true to retain a readable text alternative with the same action summary. |
| 43 | `action = report["caregiver_action"]` | Store the displayed expression in `action` to retain a readable text alternative with the same action summary. |
| 44 | `sections.insert(1, f"CAREGIVER ACTION: {action['title']}\n{action['detail']}\nSugar: {action['sugar']}\nMedical help: {action['doctor']}")` | Call `sections.insert` to retain a readable text alternative with the same action summary. |
| 45 | `return "\n\n".join(sections) + "\n"` | Return the constructed value to the caller to retain a readable text alternative with the same action summary. |

## server.py

| Line | Source | Explanation |
| --- | --- | --- |
| 15 | `from email_report import format_email_report` | Import format_email_report to support the visual caregiver email. |
| 16 | `from caregiver_view import caregiver_summary, demo_forecast, as_time` | Import caregiver_summary, demo_forecast, as_time to support the visual caregiver email. |
| 25 | `"This prototype is not validated for emergency detection."` | Continue the multiline statement: Store the displayed expression in `DISCLAIMER` to support the visual caregiver email. |
| 42 | `def validate_reading(glucose):` | Define validate_reading: Reading object -> validated value, original unit and timezone-qualified measurement time. |
| 43 | `"""Reading object -> validated value, original unit and timezone-qualified measurement time."""` | Document the module/function contract, inputs, output, source assumptions or side effects; no operational statement executes on this line. |
| 44 | `if not isinstance(glucose, dict):` | Check `not isinstance(glucose, dict)`; execute this branch when true to apply consistent numeric, unit and timestamp checks to each measurement. |
| 45 | `raise ValueError("glucose must be an object.")` | Stop this path with the stated validation/rendering failure; invalid data is not silently accepted. |
| 46 | `value, unit = glucose.get("value"), glucose.get("unit")` | Store the displayed expression in `(value, unit)` to apply consistent numeric, unit and timestamp checks to each measurement. |
| 47 | `if type(value) not in (int, float) or not math.isfinite(value) or not 0 < value <= 10000:` | Check `type(value) not in (int, float) or not math.isfinite(value) or (not 0 < value <= 10000)`; execute this branch when true to apply consistent numeric, unit and timestamp checks to each measurement. |
| 48 | `raise ValueError("glucose.value must be a finite positive number within the input limit.")` | Stop this path with the stated validation/rendering failure; invalid data is not silently accepted. |
| 49 | `if unit not in ("mg/dL", "mmol/L"):` | Check `unit not in ('mg/dL', 'mmol/L')`; execute this branch when true to apply consistent numeric, unit and timestamp checks to each measurement. |
| 50 | `raise ValueError("glucose.unit must be mg/dL or mmol/L.")` | Stop this path with the stated validation/rendering failure; invalid data is not silently accepted. |
| 51 | `return {"value": value, "unit": unit, "measured_at": timestamp(glucose.get("measured_at"))}` | Return the constructed value to the caller to apply consistent numeric, unit and timestamp checks to each measurement. |
| 87 | `glucose = validate_reading(glucose)` | Store the displayed expression in `glucose` to reject malformed event/history data before analysis or sending. |
| 88 | `history = data.get("glucose_history", [])` | Store the displayed expression in `history` to reject malformed event/history data before analysis or sending. |
| 89 | `if not isinstance(history, list) or len(history) > 288:` | Check `not isinstance(history, list) or len(history) > 288`; execute this branch when true to reject malformed event/history data before analysis or sending. |
| 90 | `raise ValueError("glucose_history must be a list of at most 288 readings.")` | Stop this path with the stated validation/rendering failure; invalid data is not silently accepted. |
| 91 | `history = sorted([validate_reading(item) for item in history], key=lambda item: as_time(item["measured_at"]))` | Store the displayed expression in `history` to reject malformed event/history data before analysis or sending. |
| 92 | `if glucose is None and history:` | Check `glucose is None and history`; execute this branch when true to reject malformed event/history data before analysis or sending. |
| 93 | `glucose = history.pop()` | Store the displayed expression in `glucose` to reject malformed event/history data before analysis or sending. |
| 94 | `if glucose and history and as_time(history[-1]["measured_at"]) > as_time(glucose["measured_at"]):` | Check `glucose and history and (as_time(history[-1]['measured_at']) > as_time(glucose['measured_at']))`; execute this branch when true to reject malformed event/history data before analysis or sending. |
| 95 | `raise ValueError("The current glucose must not precede the latest history entry.")` | Stop this path with the stated validation/rendering failure; invalid data is not silently accepted. |
| 96 | `for key in ("synthetic", "severe_symptoms"):` | Iterate `('synthetic', 'severe_symptoms')` as `key` to reject malformed event/history data before analysis or sending. |
| 97 | `if type(data.get(key, False)) is not bool:` | Check `type(data.get(key, False)) is not bool`; execute this branch when true to reject malformed event/history data before analysis or sending. |
| 98 | `raise ValueError(key + " must be a boolean.")` | Stop this path with the stated validation/rendering failure; invalid data is not silently accepted. |
| 100 | `event.update(glucose_history=history, synthetic=data.get("synthetic", False), severe_symptoms=data.get("severe_symptoms", False))` | Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 135 | `action = caregiver_summary(event)` | Store the displayed expression in `action` to assemble original data, independent action screening and mock estimates. |
| 142 | `"caregiver_action": action, "forecast": demo_forecast(as_time(action["generated_at"])),` | Continue the multiline statement: Return the constructed value to the caller to assemble original data, independent action screening and mock estimates. |
| 177 | `from visual_email import compose_email` | Import compose_email to send the new MIME report through the existing SMTP connection. |
| 178 | `message = compose_email(report, raw, subtype, config["FROM"], config["TO"])` | Store the displayed expression in `message` to send the new MIME report through the existing SMTP connection. |

## run_demo.py

| Line | Source | Explanation |
| --- | --- | --- |
| 28 | `extras = {}` | Store the displayed expression in `extras` to load optional glucose history and preserve the single-reading input format. |
| 31 | `if isinstance(glucose, dict) and ("current" in glucose or "history" in glucose):` | Check `isinstance(glucose, dict) and ('current' in glucose or 'history' in glucose)`; execute this branch when true to load optional glucose history and preserve the single-reading input format. |
| 32 | `extras = {"glucose_history": glucose.get("history", []), "synthetic": glucose.get("synthetic", False),` | Store the displayed expression in `extras` to load optional glucose history and preserve the single-reading input format. |
| 33 | `"severe_symptoms": glucose.get("severe_symptoms", False)}` | Continue the multiline statement: Store the displayed expression in `extras` to load optional glucose history and preserve the single-reading input format. |
| 34 | `glucose = glucose.get("current")` | Store the displayed expression in `glucose` to load optional glucose history and preserve the single-reading input format. |
| 38 | `data.update(extras)` | Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 67 | `parser.add_argument("--html-preview", type=Path, help="Save a visual HTML preview with embedded images; sends no email.")` | Call `parser.add_argument` to select the requested preview or email operation. |
| 74 | `if args.html_preview:` | Check `args.html_preview`; execute this branch when true to select the requested preview or email operation. |
| 75 | `from visual_email import write_preview` | Import write_preview to select the requested preview or email operation. |
| 76 | `write_preview(report, raw, subtype, args.html_preview)` | Call `write_preview` to select the requested preview or email operation. |
| 77 | `print("Visual preview saved:", args.html_preview)` | Report the operation outcome locally without printing SMTP credentials. |
| 78 | `return 0` | Return the constructed value to the caller to select the requested preview or email operation. |

## test_pipeline.py

| Line | Source | Explanation |
| --- | --- | --- |
| 168 | `"SMTP_USER": "", "SMTP_PASSWORD": "",` | Continue the multiline statement: Enter the temporary test context so mock settings/resources are restored on exit. |
| 169 | `}):` | Continue the multiline statement: Enter the temporary test context so mock settings/resources are restored on exit. |
| 179 | `attachment, = [part for part in message.walk() if part.get_filename() == "meal.png"]` | Store the displayed expression in `(attachment,)` to verify the documented behaviour under isolated test conditions. |
| 182 | `html = message.get_body(preferencelist=("html",)).get_content()` | Store the displayed expression in `html` to verify the documented behaviour under isolated test conditions. |
| 183 | `self.assertIn("cid:glucose-chart", html)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 184 | `self.assertIn("CAREGIVER ACTION", html)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 185 | `self.assertEqual(len([part for part in message.walk() if part.get_content_type() == "image/png"]), 3)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 186 | `body = message.get_body(preferencelist=("plain",)).get_content()` | Store the displayed expression in `body` to verify the documented behaviour under isolated test conditions. |
| 187 | `self.assertIn("Measured glucose: 7.2 mmol/L", body)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 188 | `self.assertIn("Measurement time: 09 Nov 2026, 11:55 (UTC+0800)", body)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 189 | `self.assertIn("Sugar: 12 g (illustrative range: 6 to 20 g)", body)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 190 | `self.assertIn("Estimated glucose: 140 mg/dL", body)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 191 | `self.assertNotIn('"original_information"', body)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 193 | `def test_email_without_measured_glucose(self):` | Define test_email_without_measured_glucose: verify the documented behaviour under isolated test conditions |
| 194 | `event, raw, subtype = server.validate_event(EVENT)` | Store the displayed expression in `(event, raw, subtype)` to verify the documented behaviour under isolated test conditions. |
| 195 | `event["glucose"] = None` | Store the displayed expression in `event['glucose']` to verify the documented behaviour under isolated test conditions. |
| 196 | `body = server.format_email_report(server.analyze(event, raw))` | Store the displayed expression in `body` to verify the documented behaviour under isolated test conditions. |
| 197 | `self.assertIn("No measured glucose reading was provided.", body)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 198 | `self.assertIn("SIMULATED CURRENT GLUCOSE", body)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 199 | `self.assertIn("not a measured reading", body)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 200 | `self.assertIn("CAREGIVER NOTES", body)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 201 | `self.assertIn("not validated 90% confidence intervals", body)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 203 | `def test_email_preserves_mgdl_measurement(self):` | Define test_email_preserves_mgdl_measurement: verify the documented behaviour under isolated test conditions |
| 204 | `event, raw, subtype = server.validate_event(EVENT)` | Store the displayed expression in `(event, raw, subtype)` to verify the documented behaviour under isolated test conditions. |
| 205 | `event["glucose"].update(value=130, unit="mg/dL")` | Update the displayed action/event fields for this branch while keeping measured and simulated data separate. |
| 206 | `body = server.format_email_report(server.analyze(event, raw))` | Store the displayed expression in `body` to verify the documented behaviour under isolated test conditions. |
| 207 | `self.assertIn("Measured glucose: 130 mg/dL", body)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 208 | `self.assertIn("Total carbohydrates: 60 g", body)` | Require the displayed expected value/property; fail the regression test if it changes. |
| 228 | `"SMTP_PASSWORD": "test-secret", "SMTP_PORT": "587", "SMTP_MODE": "starttls"}), patch.object(server.smtplib, "SMTP") as smtp:` | Continue the multiline statement: Enter the temporary test context so mock settings/resources are restored on exit. |

## Artifacts, documentation and checks

The output/ ignore rule excludes generated health-data previews, screenshots and browser scratch files. The new synthetic JSON fixture contains a current reading and four historical readings, explicitly marked synthetic. It does not create patient measurements. README documents the old/new schema, colour rules, source labels, Windows renderer requirement and preview commands. The root README and original walkthrough link this current implementation; previous examples and walkthroughs remain available.

The full suite passed 30 tests after the SMTP fixtures were corrected to retain the Windows environment needed by the native renderer. Actual loopback SMTP tests check text, HTML, all three CID PNG parts and original-photo byte preservation. Rendering tests validate real 1200x480 PNGs; screening tests cover low/high boundaries, units, stale/missing/future/synthetic inputs, severe symptoms and repeated highs. The HTML test checks escaping. A rendered browser screenshot was inspected, and an offline .eml with synthetic addresses was saved under ignored output. No external mail or GitHub push occurred.
