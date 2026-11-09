"""Local demonstration server: JSON image input, mock analysis, real SMTP output."""

import base64
import binascii
import hmac
import json
import math
import os
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage
from email.utils import parseaddr
from http.server import BaseHTTPRequestHandler, HTTPServer

MAX_IMAGE = 5 * 1024 * 1024
MAX_BODY = 7 * 1024 * 1024
DISCLAIMER = (
    "DEMO ONLY: food and current glucose estimates and suggestions are simulated. "
    "Ranges are illustrative, not validated 90% confidence intervals. "
    "Do not use these outputs to decide insulin timing, dosage, or medical urgency. "
    "Use actual glucose measurements and the patient's clinician-provided care plan. "
    "This prototype does not detect emergencies."
)


def timestamp(value):
    """Validate an ISO 8601 string with timezone; return the original string."""
    if not isinstance(value, str) or len(value) > 64:
        raise ValueError("A timestamp with timezone is required.")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("Use an ISO 8601 timestamp with timezone.") from None
    if parsed.utcoffset() is None:
        raise ValueError("Timestamps must include a timezone.")
    return value


def validate_event(data):
    """Return (normalized event dict, image bytes, MIME subtype); no I/O.

    Input is a JSON object with patient_id, meal_captured_at, image and optional
    glucose. Glucose values are positive mg/dL or mmol/L measurements, not estimates.
    Only PNG/JPEG signatures are checked; this is not full image decoding.
    """
    if not isinstance(data, dict):
        raise ValueError("The request must be a JSON object.")
    patient = data.get("patient_id")
    if not isinstance(patient, str) or not patient.strip() or len(patient) > 100:
        raise ValueError("patient_id must be a nonempty string of at most 100 characters.")
    captured = timestamp(data.get("meal_captured_at"))
    picture = data.get("image")
    if not isinstance(picture, dict):
        raise ValueError("image must contain content_base64.")
    encoded = picture.get("content_base64")
    if not isinstance(encoded, str) or len(encoded) > 4 * ((MAX_IMAGE + 2) // 3):
        raise ValueError("Image must be base64 and no larger than 5 MiB decoded.")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error):
        raise ValueError("Invalid base64 image.") from None
    if not raw or len(raw) > MAX_IMAGE:
        raise ValueError("Image must be nonempty and no larger than 5 MiB.")
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        subtype = "png"
    elif raw.startswith(b"\xff\xd8\xff"):
        subtype = "jpeg"
    else:
        raise ValueError("Only PNG or JPEG image signatures are accepted.")
    glucose = data.get("glucose")
    if glucose is not None:
        if not isinstance(glucose, dict):
            raise ValueError("glucose must be an object or null.")
        value, unit = glucose.get("value"), glucose.get("unit")
        if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
            raise ValueError("glucose.value must be a finite positive number.")
        if unit not in ("mg/dL", "mmol/L"):
            raise ValueError("glucose.unit must be mg/dL or mmol/L.")
        glucose = {"value": value, "unit": unit, "measured_at": timestamp(glucose.get("measured_at"))}
    event = {"patient_id": patient, "meal_captured_at": captured, "glucose": glucose}
    return event, raw, subtype


def mock_food_analysis(image_bytes):
    """Replaceable CV stub: bytes -> fixed gram estimates, without inspecting food."""
    return {
        "source": "fixed_demo_stub",
        "sugar_g": {"estimate": 12, "illustrative_range": [6, 20]},
        "carbohydrate_g": {"estimate": 60, "illustrative_range": [40, 85]},
    }


def mock_glucose_analysis(event, food):
    """Replaceable model stub: dicts -> fixed mg/dL estimate; ignores measurements."""
    return {"source": "fixed_demo_stub", "estimate": 140, "unit": "mg/dL",
            "illustrative_range": [100, 190], "uses_measured_glucose": False}


def mock_llm_analysis(event, food, glucose):
    """Replaceable LLM stub: dicts -> templated text; no network or clinical reasoning."""
    measurement = "provided" if event["glucose"] is not None else "not provided"
    return (
        f"Demo report for {event['patient_id']}: a measured glucose reading was {measurement}. "
        "Food and glucose estimates are fixed examples and do not describe this patient's condition. "
        "Caregiver: review the attached meal photo and confirm the recorded reading and time. "
        "Follow the patient's existing care plan; ask their clinician about treatment questions. "
        "Insulin timing, dose recommendations and emergency assessment are unavailable in this demo."
    )


def analyze(event, raw):
    """Run all stubs and return JSON-safe report; measured data stays separate."""
    food = mock_food_analysis(raw)
    glucose = mock_glucose_analysis(event, food)
    return {
        "demo": True, "warning": DISCLAIMER, "original_information": event,
        "food": food, "estimated_current_glucose": glucose,
        "uncertainty": {"intended_coverage": 0.90, "validated": False,
                        "confidence_level": None, "meaning": "Illustrative demo ranges only"},
        "suggestions": mock_llm_analysis(event, food, glucose),
    }


def smtp_settings():
    """Read environment configuration; validate addresses/TLS; never log credentials."""
    settings = {key: os.environ.get("SMTP_" + key, "") for key in
                ("HOST", "PORT", "MODE", "USER", "PASSWORD", "FROM", "TO")}
    settings["MODE"] = settings["MODE"] or "starttls"
    if not settings["HOST"] or not settings["FROM"] or not settings["TO"]:
        raise ValueError("Set SMTP_HOST, SMTP_FROM and SMTP_TO before sending.")
    for key in ("FROM", "TO"):
        address = settings[key]
        if "\r" in address or "\n" in address or parseaddr(address)[1] != address or address.count("@") != 1:
            raise ValueError("SMTP_FROM and SMTP_TO must each be one plain email address.")
    mode = settings["MODE"]
    if mode not in ("ssl", "starttls", "plain"):
        raise ValueError("SMTP_MODE must be ssl, starttls or plain.")
    if mode == "plain" and settings["HOST"] not in ("localhost", "127.0.0.1", "::1"):
        raise ValueError("Unencrypted SMTP is allowed only for local testing.")
    settings["PORT"] = int(settings["PORT"] or (465 if mode == "ssl" else 587))
    if not 1 <= settings["PORT"] <= 65535:
        raise ValueError("SMTP_PORT must be between 1 and 65535.")
    if bool(settings["USER"]) != bool(settings["PASSWORD"]):
        raise ValueError("Set both SMTP_USER and SMTP_PASSWORD, or neither.")
    return settings


def send_email(report, raw, subtype):
    """Send a report and image via SMTP; return only after server acceptance.

    report: dict, raw: PNG/JPEG bytes, subtype: png/jpeg. Sends private data to
    configured SMTP_TO. SMTP acceptance does not prove delivery to an inbox.
    """
    config = smtp_settings()
    message = EmailMessage()
    message["Subject"] = "[SIMULATED DEMO] Meal and glucose caregiver report"
    message["From"], message["To"] = config["FROM"], config["TO"]
    message.set_content(DISCLAIMER + "\n\n" + json.dumps(report, indent=2, ensure_ascii=False))
    message.add_attachment(raw, maintype="image", subtype=subtype, filename="meal." + subtype)
    client = smtplib.SMTP_SSL if config["MODE"] == "ssl" else smtplib.SMTP
    options = {"timeout": 20}
    if config["MODE"] == "ssl":
        options["context"] = ssl.create_default_context()
    with client(config["HOST"], config["PORT"], **options) as smtp:
        if config["MODE"] == "starttls":
            smtp.starttls(context=ssl.create_default_context())
        if config["USER"]:
            smtp.login(config["USER"], config["PASSWORD"])
        smtp.send_message(message)


class Handler(BaseHTTPRequestHandler):
    """Authenticated local JSON API. Processes one request at a time; stores no events."""

    def log_message(self, format, *args):
        """Suppress access logs so request details do not enter console logs."""
        return

    def reply(self, status, payload):
        """Serialize dict to UTF-8 JSON and write a non-cacheable HTTP response."""
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        """Expose only a health check, without patient data or SMTP credentials."""
        self.reply(200 if self.path == "/health" else 404,
                   {"status": "ok", "demo": True} if self.path == "/health" else {"error": "Not found"})

    def do_POST(self):
        """Validate authenticated JSON; preview or send; surface SMTP failure as 502."""
        self.connection.settimeout(30)
        if self.path not in ("/preview", "/events"):
            self.reply(404, {"error": "Not found"})
            return
        supplied = self.headers.get("Authorization", "").encode("utf-8")
        expected = ("Bearer " + self.server.api_token).encode("utf-8")
        if not hmac.compare_digest(supplied, expected):
            self.reply(401, {"error": "A valid Bearer API_TOKEN is required."})
            return
        if self.headers.get_content_type() != "application/json":
            self.reply(415, {"error": "Use application/json."})
            return
        try:
            if self.headers.get("Transfer-Encoding"):
                raise ValueError("Transfer-Encoding is unsupported; send Content-Length.")
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_BODY:
                self.reply(413, {"error": "JSON body must be between 1 byte and 7 MiB."})
                return
            data = json.loads(self.rfile.read(length))
            event, raw, subtype = validate_event(data)
        except (ValueError, OverflowError, RecursionError):
            self.reply(400, {"error": "Invalid event: check the documented schema, image, units and timestamps."})
            return
        except (OSError, TimeoutError):
            self.reply(408, {"error": "Request body could not be read in time."})
            return
        report = analyze(event, raw)
        if self.path == "/preview":
            self.reply(200, {"email_status": "not_sent_preview", "report": report})
            return
        try:
            send_email(report, raw, subtype)
        except (ValueError, OSError, smtplib.SMTPException):
            self.reply(502, {"email_status": "failed_or_unconfirmed", "report": report,
                             "error": "SMTP failed. Check local configuration and provider status before retrying."})
            return
        self.reply(200, {"email_status": "accepted_by_smtp", "report": report})


def main():
    """Start on loopback only; require a token. Stops on Ctrl+C; writes no patient files."""
    token = os.environ.get("API_TOKEN", "")
    if len(token) < 16:
        raise SystemExit("Set API_TOKEN to a random secret of at least 16 characters.")
    server = HTTPServer(("127.0.0.1", int(os.environ.get("PORT", "8000"))), Handler)
    server.api_token = token
    print(f"Demo API listening on http://127.0.0.1:{server.server_port}; Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
