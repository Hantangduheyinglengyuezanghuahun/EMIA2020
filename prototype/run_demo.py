"""Read a meal photo and optional glucose JSON, analyze once, email once, then exit."""

import argparse
import base64
import json
import os
import smtplib
from datetime import datetime, timezone
from pathlib import Path

import server

ROOT = Path(__file__).resolve().parent


def read_event(image_path, glucose_path, patient_id, captured_at=None):
    """Paths + patient string + optional ISO timestamp -> validated event, bytes, subtype.

    Missing glucose files mean no measurement; malformed existing files fail.
    Glucose JSON contains value, unit and measured_at. Units follow server.py.
    Without captured_at, the image's file modification time is used as a demo proxy.
    Reads local files only and sends nothing.
    """
    if image_path.stat().st_size > server.MAX_IMAGE:
        raise ValueError("Image exceeds the 5 MiB limit.")
    raw = image_path.read_bytes()
    glucose = None
    extras = {}
    if glucose_path.is_file():
        glucose = json.loads(glucose_path.read_text(encoding="utf-8-sig"))
        if isinstance(glucose, dict) and ("current" in glucose or "history" in glucose):
            extras = {"glucose_history": glucose.get("history", []), "synthetic": glucose.get("synthetic", False),
                      "severe_symptoms": glucose.get("severe_symptoms", False)}
            glucose = glucose.get("current")
    captured_at = captured_at or datetime.fromtimestamp(image_path.stat().st_mtime, timezone.utc).isoformat()
    data = {"patient_id": patient_id, "meal_captured_at": captured_at,
            "image": {"content_base64": base64.b64encode(raw).decode("ascii")}, "glucose": glucose}
    data.update(extras)
    return server.validate_event(data)


def load_mail_settings():
    """Read ignored SMTP JSON and optional CA bundle into this process; never print secrets."""
    config = json.loads((ROOT / ".env.smtp.json").read_text(encoding="utf-8-sig"))
    fields = {"HOST": "host", "PORT": "port", "MODE": "mode", "USER": "user",
              "FROM": "sender", "TO": "recipient", "PASSWORD": "password"}
    for suffix, key in fields.items():
        os.environ["SMTP_" + suffix] = str(config[key])
    bundle = ROOT / ".env.smtp-ca.pem"
    if bundle.is_file() and not os.environ.get("SSL_CERT_FILE"):
        os.environ["SSL_CERT_FILE"] = str(bundle)
    server.smtp_settings()


def main(argv=None):
    """CLI arguments -> exit code. Default sends one real email; --preview sends none.

    Optional argv is a list of argument strings for testing. Local SMTP settings
    and public CA certificates are loaded only for a send. No HTTP server starts.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=ROOT / "samples" / "demo-meal.png")
    parser.add_argument("--glucose", type=Path, default=ROOT / "samples" / "glucose.json")
    parser.add_argument("--patient-id", default="demo-patient-001")
    parser.add_argument("--captured-at", help="Actual ISO 8601 meal capture time with timezone, if known.")
    parser.add_argument("--preview", action="store_true", help="Print the report without sending email.")
    parser.add_argument("--html-preview", type=Path, help="Save a visual HTML preview with embedded images; sends no email.")
    parser.add_argument("--language", choices=("en", "zh-CN"), default="en", help="Email language (default: en).")
    args = parser.parse_args(argv)
    try:
        event, raw, subtype = read_event(args.image, args.glucose, args.patient_id, args.captured_at)
        report = server.analyze(event, raw)
        report["language"] = args.language
        print("Image:", args.image)
        print("Measured glucose:", "provided" if event["glucose"] is not None else "unavailable")
        if args.html_preview:
            from visual_email import write_preview
            write_preview(report, raw, subtype, args.html_preview)
            print("Visual preview saved:", args.html_preview)
            return 0
        if args.preview:
            print(json.dumps(report, indent=2, ensure_ascii=False))
            print("Preview complete; no email sent.")
            return 0
        load_mail_settings()
        server.send_email(report, raw, subtype)
        print("Email accepted by SMTP for", os.environ["SMTP_TO"], "(inbox delivery not confirmed).")
        return 0
    except (OSError, ValueError, KeyError, TypeError, OverflowError, smtplib.SMTPException) as error:
        print("Failed or unconfirmed (" + type(error).__name__ + "). Check input files and local SMTP/TLS settings before retrying.")
        return 1
    finally:
        os.environ.pop("SMTP_PASSWORD", None)


if __name__ == "__main__":
    raise SystemExit(main())
