# Complete code walkthrough

Publication preparation adds a root README linking the prototype and its tests, plus a secret-free `.env.example` JSON template. Its host, port and mode select Gmail STARTTLS; user/sender/recipient/password are placeholders to replace only in an ignored local copy. The new `samples/glucose.json` ignore rule excludes an optional patient measurement file. The client example's `cd prototype` and `samples\demo-meal.png` path now work relative to a clone rather than a developer-specific absolute directory. Personal email addresses in the historical progress record were replaced by configuration-field references. These are documentation/configuration-example changes only; no Python behavior changed.

The later file-based automation is explained line by line in [DEMO_WALKTHROUGH.md](DEMO_WALKTHROUGH.md), covering every nonblank line of `run_demo.py` and `test_demo.py`. The original server, launcher and tests described below are unchanged by that addition.

Every nonblank line in all three added Python source files is accounted for below. Blank lines only separate definitions and have no runtime behavior. Docstrings document the adjacent function or module. There was no pre-existing code in this folder and no behavior was removed.

The production path is validation -> fixed food stub -> fixed glucose stub -> suggestion template -> MIME report and image -> SMTP. The tests use separate temporary loopback servers and never send to an external mailbox.

## server.py

| Line | Source | Explanation |
| --- | --- | --- |
| 1 | `"""Local demonstration server: JSON image input, mock analysis, real SMTP output."""` | Document the surrounding module or callable: Local demonstration server: JSON image input, mock analysis, real SMTP output. |
| 3 | `import base64` | Import base64 from the standard library to encode or decode image bytes in the JSON transport. |
| 4 | `import binascii` | Import binascii from the standard library to recognize strict base64 decoding failures. |
| 5 | `import hmac` | Import hmac from the standard library to compare authentication token bytes in constant time. |
| 6 | `import json` | Import json from the standard library to serialize reports and parse request bodies. |
| 7 | `import math` | Import math from the standard library to reject non-finite glucose readings. |
| 8 | `import os` | Import os from the standard library to read configuration from environment variables. |
| 9 | `import smtplib` | Import smtplib from the standard library to send MIME messages using the SMTP protocol. |
| 10 | `import ssl` | Import ssl from the standard library to create certificate-verifying TLS contexts. |
| 11 | `from datetime import datetime` | Import datetime from the standard library to parse timezone-qualified capture and measurement times. |
| 12 | `from email.message import EmailMessage` | Import EmailMessage from the standard library to construct standards-based MIME messages and attachments. |
| 13 | `from email.utils import parseaddr` | Import parseaddr from the standard library to check that configured recipients and senders are plain addresses. |
| 14 | `from http.server import BaseHTTPRequestHandler, HTTPServer` | Import BaseHTTPRequestHandler, HTTPServer from the standard library to serve the local JSON API without third-party dependencies. |
| 16 | `MAX_IMAGE = 5 * 1024 * 1024` | Set the decoded image ceiling to 5 MiB (5 times 1024 squared bytes) to bound attachment memory use. |
| 17 | `MAX_BODY = 7 * 1024 * 1024` | Set the JSON request ceiling to 7 MiB, allowing base64 expansion while bounding input memory. |
| 18 | `DISCLAIMER = (` | Begin the shared warning string used in API reports and email bodies. |
| 19 | `"DEMO ONLY: food and current glucose estimates and suggestions are simulated. "` | State that food, current glucose and suggestions are simulated so recipients know their source. |
| 20 | `"Ranges are illustrative, not validated 90% confidence intervals. "` | Explain that the ranges have no validated 90% confidence meaning. |
| 21 | `"Do not use these outputs to decide insulin timing, dosage, or medical urgency. "` | Exclude insulin timing, dose and urgency decisions from the permitted use of the output. |
| 22 | `"Use actual glucose measurements and the patient's clinician-provided care plan. "` | Direct users to actual measurements and the existing clinician-provided plan. |
| 23 | `"This prototype does not detect emergencies."` | Explicitly disclose that the prototype does not detect emergencies. |
| 24 | `)` | Close the multiline expression above; its values and purpose are explained on the preceding lines. |
| 27 | `def timestamp(value):` | Define the timestamp function: Validate an ISO 8601 string with timezone; return the original string. |
| 28 | `"""Validate an ISO 8601 string with timezone; return the original string."""` | Document the surrounding module or callable: Validate an ISO 8601 string with timezone; return the original string. |
| 29 | `if not isinstance(value, str) or len(value) > 64:` | Require a string of at most 64 characters before attempting date parsing. |
| 30 | `raise ValueError("A timestamp with timezone is required.")` | Reject a missing, incorrectly typed or excessively long timestamp with a validation error. |
| 31 | `try:` | Begin protected parsing so invalid date syntax can become a controlled validation failure. |
| 32 | `parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))` | Replace the UTC suffix Z with +00:00 for Python 3.10 compatibility, then parse the date and time. |
| 33 | `except ValueError:` | Handle a date/time parsing failure locally. |
| 34 | `raise ValueError("Use an ISO 8601 timestamp with timezone.") from None` | Raise a clearer validation message without attaching the low-level parsing traceback as its cause. |
| 35 | `if parsed.utcoffset() is None:` | Check whether the parsed date has a timezone offset; an absent offset makes the time ambiguous. |
| 36 | `raise ValueError("Timestamps must include a timezone.")` | Reject dates without a timezone so capture and measurement times can be compared later. |
| 37 | `return value` | Return the original validated string to preserve the supplied timestamp representation. |
| 40 | `def validate_event(data):` | Define the validate_event function: Return (normalized event dict, image bytes, MIME subtype); no I/O. |
| 41 | `"""Return (normalized event dict, image bytes, MIME subtype); no I/O.` | Document the surrounding module or callable: Return (normalized event dict, image bytes, MIME subtype); no I/O. |
| 43 | `Input is a JSON object with patient_id, meal_captured_at, image and optional` | Document the surrounding module or callable: Input is a JSON object with patient_id, meal_captured_at, image and optional |
| 44 | `glucose. Glucose values are positive mg/dL or mmol/L measurements, not estimates.` | Document the surrounding module or callable: glucose. Glucose values are positive mg/dL or mmol/L measurements, not estimates. |
| 45 | `Only PNG/JPEG signatures are checked; this is not full image decoding.` | Document the surrounding module or callable: Only PNG/JPEG signatures are checked; this is not full image decoding. |
| 46 | `"""` | Document the surrounding module or callable:  |
| 47 | `if not isinstance(data, dict):` | Require the top-level JSON value to be an object, rather than a list or primitive. |
| 48 | `raise ValueError("The request must be a JSON object.")` | Stop validation with an object-schema error when that requirement fails. |
| 49 | `patient = data.get("patient_id")` | Read patient_id using get so an absent field becomes None and follows the same validation path. |
| 50 | `if not isinstance(patient, str) or not patient.strip() or len(patient) > 100:` | Require a string identifier containing non-whitespace text and limit it to 100 characters. |
| 51 | `raise ValueError("patient_id must be a nonempty string of at most 100 characters.")` | Reject an invalid identifier before it reaches the report or email. |
| 52 | `captured = timestamp(data.get("meal_captured_at"))` | Validate the meal capture timestamp with the shared timezone-aware parser. |
| 53 | `picture = data.get("image")` | Read the image object without assuming the client supplied it. |
| 54 | `if not isinstance(picture, dict):` | Require an object containing the image fields. |
| 55 | `raise ValueError("image must contain content_base64.")` | Reject a missing or incorrectly typed image object. |
| 56 | `encoded = picture.get("content_base64")` | Extract the base64 image text; image URLs are not fetched. |
| 57 | `if not isinstance(encoded, str) or len(encoded) > 4 * ((MAX_IMAGE + 2) // 3):` | Require a string and cap its encoded length at four characters per three allowed image bytes, rounded up. |
| 58 | `raise ValueError("Image must be base64 and no larger than 5 MiB decoded.")` | Reject malformed types or excessive encoded lengths before decoding them. |
| 59 | `try:` | Begin strict base64 conversion with a controlled error path. |
| 60 | `raw = base64.b64decode(encoded, validate=True)` | Decode to bytes and reject characters outside the base64 alphabet through validate=True. |
| 61 | `except (ValueError, binascii.Error):` | Catch both ordinary value errors and binary-decoding errors raised by base64 conversion. |
| 62 | `raise ValueError("Invalid base64 image.") from None` | Replace those decoder errors with a safe image-validation message. |
| 63 | `if not raw or len(raw) > MAX_IMAGE:` | Check the actual decoded length, rejecting both empty images and anything over 5 MiB. |
| 64 | `raise ValueError("Image must be nonempty and no larger than 5 MiB.")` | Raise a validation error if the decoded payload violates the size limit. |
| 65 | `if raw.startswith(b"\x89PNG\r\n\x1a\n"):` | Check the eight-byte PNG signature; this identifies the declared format without full decoding. |
| 66 | `subtype = "png"` | Select the PNG MIME subtype and attachment extension when the signature matches. |
| 67 | `elif raw.startswith(b"\xff\xd8\xff"):` | Otherwise check the leading three JPEG marker bytes. |
| 68 | `subtype = "jpeg"` | Select the JPEG MIME subtype and attachment extension for a matching signature. |
| 69 | `else:` | Use the alternate branch when neither supported image signature matches. |
| 70 | `raise ValueError("Only PNG or JPEG image signatures are accepted.")` | Reject unsupported formats rather than attaching arbitrary binary data as an image. |
| 71 | `glucose = data.get("glucose")` | Read optional glucose; an omitted field and explicit null both produce None. |
| 72 | `if glucose is not None:` | Validate glucose fields only when a reading has actually been supplied. |
| 73 | `if not isinstance(glucose, dict):` | Require a supplied glucose reading to be an object. |
| 74 | `raise ValueError("glucose must be an object or null.")` | Reject malformed glucose containers without inventing a measurement. |
| 75 | `value, unit = glucose.get("value"), glucose.get("unit")` | Extract the numeric measurement and its declared unit for independent validation. |
| 76 | `if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:` | Allow only exact int/float types, excluding booleans, and require a finite positive value. |
| 77 | `raise ValueError("glucose.value must be a finite positive number.")` | Reject text, booleans, zero, negative values, infinity and NaN as measurements. |
| 78 | `if unit not in ("mg/dL", "mmol/L"):` | Accept only the two documented glucose units; no implicit unit assumption is made. |
| 79 | `raise ValueError("glucose.unit must be mg/dL or mmol/L.")` | Reject an unknown unit to prevent ambiguous interpretation of the original reading. |
| 80 | `glucose = {"value": value, "unit": unit, "measured_at": timestamp(glucose.get("measured_at"))}` | Rebuild the reading from validated value, unchanged unit and validated measurement timestamp. |
| 81 | `event = {"patient_id": patient, "meal_captured_at": captured, "glucose": glucose}` | Build the normalized event with patient identifier, capture time and measured glucose only; ignore extra fields. |
| 82 | `return event, raw, subtype` | Return the normalized event, decoded image bytes and detected subtype for analysis and email attachment creation. |
| 85 | `def mock_food_analysis(image_bytes):` | Define the mock_food_analysis function: Replaceable CV stub: bytes -> fixed gram estimates, without inspecting food. |
| 86 | `"""Replaceable CV stub: bytes -> fixed gram estimates, without inspecting food."""` | Document the surrounding module or callable: Replaceable CV stub: bytes -> fixed gram estimates, without inspecting food. |
| 87 | `return {` | Begin returning fixed food-analysis data; the supplied bytes are deliberately not inspected. |
| 88 | `"source": "fixed_demo_stub",` | Label the food source as a fixed demonstration stub rather than a CV result. |
| 89 | `"sugar_g": {"estimate": 12, "illustrative_range": [6, 20]},` | Supply an illustrative 12 g sugar estimate with a 6 to 20 g range. |
| 90 | `"carbohydrate_g": {"estimate": 60, "illustrative_range": [40, 85]},` | Supply a separate 60 g total-carbohydrate estimate with a 40 to 85 g range; sugar and carbohydrates are not equated. |
| 91 | `}` | Close the multiline expression above; its values and purpose are explained on the preceding lines. |
| 94 | `def mock_glucose_analysis(event, food):` | Define the replacement boundary for a future model using event and food dictionaries. |
| 95 | `"""Replaceable model stub: dicts -> fixed mg/dL estimate; ignores measurements."""` | Document the surrounding module or callable: Replaceable model stub: dicts -> fixed mg/dL estimate; ignores measurements. |
| 96 | `return {"source": "fixed_demo_stub", "estimate": 140, "unit": "mg/dL",` | Return a fixed 140 mg/dL synthetic glucose estimate with its source explicitly labelled. |
| 97 | `"illustrative_range": [100, 190], "uses_measured_glucose": False}` | Add the illustrative 100 to 190 mg/dL range and disclose that no measured glucose was used. |
| 100 | `def mock_llm_analysis(event, food, glucose):` | Define the mock_llm_analysis function: Replaceable LLM stub: dicts -> templated text; no network or clinical reasoning. |
| 101 | `"""Replaceable LLM stub: dicts -> templated text; no network or clinical reasoning."""` | Document the surrounding module or callable: Replaceable LLM stub: dicts -> templated text; no network or clinical reasoning. |
| 102 | `measurement = "provided" if event["glucose"] is not None else "not provided"` | Choose wording based only on whether an original measurement exists; do not interpret its clinical value. |
| 103 | `return (` | Begin returning a single concatenated suggestion string instead of calling an LLM API. |
| 104 | `f"Demo report for {event['patient_id']}: a measured glucose reading was {measurement}. "` | Insert the patient identifier and presence of a measurement into the report template. |
| 105 | `"Food and glucose estimates are fixed examples and do not describe this patient's condition. "` | Explain that the fixed numbers do not describe this patient's condition. |
| 106 | `"Caregiver: review the attached meal photo and confirm the recorded reading and time. "` | Ask the caregiver to review the real photo and verify the reading and time. |
| 107 | `"Follow the patient's existing care plan; ask their clinician about treatment questions. "` | Refer treatment questions to the existing care plan and clinician rather than generating treatment rules. |
| 108 | `"Insulin timing, dose recommendations and emergency assessment are unavailable in this demo."` | Explicitly state that insulin timing, doses and emergency assessment are unavailable. |
| 109 | `)` | Close the multiline expression above; its values and purpose are explained on the preceding lines. |
| 112 | `def analyze(event, raw):` | Define the analyze function: Run all stubs and return JSON-safe report; measured data stays separate. |
| 113 | `"""Run all stubs and return JSON-safe report; measured data stays separate."""` | Document the surrounding module or callable: Run all stubs and return JSON-safe report; measured data stays separate. |
| 114 | `food = mock_food_analysis(raw)` | Pass the decoded image to the replaceable food stub and retain its dictionary result. |
| 115 | `glucose = mock_glucose_analysis(event, food)` | Pass event and food dictionaries to the replaceable glucose stub and retain its result. |
| 116 | `return {` | Begin assembling the complete JSON-safe report returned to HTTP clients and email recipients. |
| 117 | `"demo": True, "warning": DISCLAIMER, "original_information": event,` | Mark the report as a demo, include the warning and retain original information under its own key. |
| 118 | `"food": food, "estimated_current_glucose": glucose,` | Place food estimates and synthetic current glucose in separate report fields. |
| 119 | `"uncertainty": {"intended_coverage": 0.90, "validated": False,` | Record 0.90 as the intended future coverage target while explicitly setting validated to false. |
| 120 | `"confidence_level": None, "meaning": "Illustrative demo ranges only"},` | Set actual confidence_level to None (JSON null) and describe the ranges as illustrative, avoiding a statistical claim. |
| 121 | `"suggestions": mock_llm_analysis(event, food, glucose),` | Run the replaceable LLM template and add its string under suggestions. |
| 122 | `}` | Close the multiline expression above; its values and purpose are explained on the preceding lines. |
| 125 | `def smtp_settings():` | Define the smtp_settings function: Read environment configuration; validate addresses/TLS; never log credentials. |
| 126 | `"""Read environment configuration; validate addresses/TLS; never log credentials."""` | Document the surrounding module or callable: Read environment configuration; validate addresses/TLS; never log credentials. |
| 127 | `settings = {key: os.environ.get("SMTP_" + key, "") for key in` | Build SMTP configuration by reading SMTP-prefixed environment variables, using an empty string for missing values. |
| 128 | `("HOST", "PORT", "MODE", "USER", "PASSWORD", "FROM", "TO")}` | Enumerate the seven supported settings: host, port, TLS mode, user, password, sender and recipient. |
| 129 | `settings["MODE"] = settings["MODE"] or "starttls"` | Default to STARTTLS when SMTP_MODE is absent or empty so remote SMTP is encrypted by default. |
| 130 | `if not settings["HOST"] or not settings["FROM"] or not settings["TO"]:` | Require a host, sender and recipient before any connection is attempted. |
| 131 | `raise ValueError("Set SMTP_HOST, SMTP_FROM and SMTP_TO before sending.")` | Raise a configuration error identifying the missing required setting group. |
| 132 | `for key in ("FROM", "TO"):` | Validate the sender and recipient independently, each as a single plain address. |
| 133 | `address = settings[key]` | Select the current address for the following format checks. |
| 134 | `if "\r" in address or "\n" in address or parseaddr(address)[1] != address or address.count("@") != 1:` | Reject line breaks, display-name/list syntax and addresses without exactly one @ to avoid ambiguous headers. |
| 135 | `raise ValueError("SMTP_FROM and SMTP_TO must each be one plain email address.")` | Report invalid address syntax without printing the actual address or any credentials. |
| 136 | `mode = settings["MODE"]` | Keep the selected encryption mode in a local variable for readable validation. |
| 137 | `if mode not in ("ssl", "starttls", "plain"):` | Limit SMTP mode to the three deliberately implemented transports. |
| 138 | `raise ValueError("SMTP_MODE must be ssl, starttls or plain.")` | Reject unsupported transport modes rather than silently choosing an encryption policy. |
| 139 | `if mode == "plain" and settings["HOST"] not in ("localhost", "127.0.0.1", "::1"):` | Allow plaintext SMTP only when the configured hostname is one of the explicit local-host forms. |
| 140 | `raise ValueError("Unencrypted SMTP is allowed only for local testing.")` | Reject remote plaintext connections so patient reports are not deliberately sent without transport encryption. |
| 141 | `settings["PORT"] = int(settings["PORT"] or (465 if mode == "ssl" else 587))` | Convert the configured port to an integer; default to 465 for implicit TLS and 587 otherwise. |
| 142 | `if not 1 <= settings["PORT"] <= 65535:` | Require a valid TCP port in the inclusive range 1 to 65535. |
| 143 | `raise ValueError("SMTP_PORT must be between 1 and 65535.")` | Reject out-of-range ports before opening a socket. |
| 144 | `if bool(settings["USER"]) != bool(settings["PASSWORD"]):` | Compare whether username and password are present; a mismatch means authentication is only partly configured. |
| 145 | `raise ValueError("Set both SMTP_USER and SMTP_PASSWORD, or neither.")` | Reject partial credentials; both absent is allowed for an appropriately configured relay. |
| 146 | `return settings` | Return the validated settings dictionary to the email sender. |
| 149 | `def send_email(report, raw, subtype):` | Define the send_email function: Send a report and image via SMTP; return only after server acceptance. |
| 150 | `"""Send a report and image via SMTP; return only after server acceptance.` | Document the surrounding module or callable: Send a report and image via SMTP; return only after server acceptance. |
| 152 | `report: dict, raw: PNG/JPEG bytes, subtype: png/jpeg. Sends private data to` | Document the surrounding module or callable: report: dict, raw: PNG/JPEG bytes, subtype: png/jpeg. Sends private data to |
| 153 | `configured SMTP_TO. SMTP acceptance does not prove delivery to an inbox.` | Document the surrounding module or callable: configured SMTP_TO. SMTP acceptance does not prove delivery to an inbox. |
| 154 | `"""` | Document the surrounding module or callable:  |
| 155 | `config = smtp_settings()` | Load and validate environment configuration at sending time, so preview does not require SMTP settings. |
| 156 | `message = EmailMessage()` | Create an EmailMessage object to handle MIME structure and encoding correctly. |
| 157 | `message["Subject"] = "[SIMULATED DEMO] Meal and glucose caregiver report"` | Set a fixed subject visibly identifying every email as a simulated demonstration. |
| 158 | `message["From"], message["To"] = config["FROM"], config["TO"]` | Use only server-configured sender and recipient addresses, never an address from the event payload. |
| 159 | `message.set_content(DISCLAIMER + "\n\n" + json.dumps(report, indent=2, ensure_ascii=False))` | Build the plain-text body from the warning and indented Unicode-preserving report JSON. |
| 160 | `message.add_attachment(raw, maintype="image", subtype=subtype, filename="meal." + subtype)` | Attach the original image bytes with the detected image MIME subtype and a safe server-generated filename. |
| 161 | `client = smtplib.SMTP_SSL if config["MODE"] == "ssl" else smtplib.SMTP` | Choose the implicit-TLS SMTP class for ssl mode and ordinary SMTP for STARTTLS or local plaintext. |
| 162 | `options = {"timeout": 20}` | Set a 20-second SMTP socket timeout to limit individual network waits. |
| 163 | `if config["MODE"] == "ssl":` | Add TLS options only when creating an implicit-TLS connection. |
| 164 | `options["context"] = ssl.create_default_context()` | Use the default certificate-verifying SSL context for that connection. |
| 165 | `with client(config["HOST"], config["PORT"], **options) as smtp:` | Open the SMTP connection with host, port and options; the context manager closes it after use. |
| 166 | `if config["MODE"] == "starttls":` | Upgrade the connection when STARTTLS is selected. |
| 167 | `smtp.starttls(context=ssl.create_default_context())` | Run STARTTLS with a certificate-verifying context; failure propagates instead of falling back to plaintext. |
| 168 | `if config["USER"]:` | Authenticate only when a username was configured; settings validation guarantees the password is also present. |
| 169 | `smtp.login(config["USER"], config["PASSWORD"])` | Log in with the environment-supplied credentials without printing them. |
| 170 | `smtp.send_message(message)` | Transmit the MIME message through SMTP; failures propagate to the HTTP failure handler. |
| 173 | `class Handler(BaseHTTPRequestHandler):` | Define the Handler class: Authenticated local JSON API. Processes one request at a time; stores no events. |
| 174 | `"""Authenticated local JSON API. Processes one request at a time; stores no events."""` | Document the surrounding module or callable: Authenticated local JSON API. Processes one request at a time; stores no events. |
| 176 | `def log_message(self, format, *args):` | Define the log_message function: Suppress access logs so request details do not enter console logs. |
| 177 | `"""Suppress access logs so request details do not enter console logs."""` | Document the surrounding module or callable: Suppress access logs so request details do not enter console logs. |
| 178 | `return` | Return immediately to suppress the inherited access logger and keep request details out of console logs. |
| 180 | `def reply(self, status, payload):` | Define the reply function: Serialize dict to UTF-8 JSON and write a non-cacheable HTTP response. |
| 181 | `"""Serialize dict to UTF-8 JSON and write a non-cacheable HTTP response."""` | Document the surrounding module or callable: Serialize dict to UTF-8 JSON and write a non-cacheable HTTP response. |
| 182 | `body = json.dumps(payload, ensure_ascii=False).encode("utf-8")` | Serialize the response dictionary as Unicode-preserving JSON and encode it to UTF-8 bytes. |
| 183 | `self.send_response(status)` | Write the chosen HTTP status and standard response metadata. |
| 184 | `self.send_header("Content-Type", "application/json; charset=utf-8")` | Declare that the body is JSON encoded as UTF-8. |
| 185 | `self.send_header("Content-Length", str(len(body)))` | Declare the exact byte length so clients know how much response data to read. |
| 186 | `self.send_header("Cache-Control", "no-store")` | Tell clients and intermediaries not to cache the response, which may contain health information. |
| 187 | `self.end_headers()` | Terminate the HTTP header section before writing response bytes. |
| 188 | `self.wfile.write(body)` | Write the serialized response body to the connected client. |
| 190 | `def do_GET(self):` | Define the do_GET function: Expose only a health check, without patient data or SMTP credentials. |
| 191 | `"""Expose only a health check, without patient data or SMTP credentials."""` | Document the surrounding module or callable: Expose only a health check, without patient data or SMTP credentials. |
| 192 | `self.reply(200 if self.path == "/health" else 404,` | Choose status 200 only for /health and 404 for any other GET path. |
| 193 | `{"status": "ok", "demo": True} if self.path == "/health" else {"error": "Not found"})` | Return minimal demo health status or a not-found error; neither payload includes patient or SMTP data. |
| 195 | `def do_POST(self):` | Define the do_POST function: Validate authenticated JSON; preview or send; surface SMTP failure as 502. |
| 196 | `"""Validate authenticated JSON; preview or send; surface SMTP failure as 502."""` | Document the surrounding module or callable: Validate authenticated JSON; preview or send; surface SMTP failure as 502. |
| 197 | `self.connection.settimeout(30)` | Set a 30-second timeout for subsequent request-body I/O; this does not harden the server for public deployment. |
| 198 | `if self.path not in ("/preview", "/events"):` | Restrict POST requests to the preview and event-submission paths. |
| 199 | `self.reply(404, {"error": "Not found"})` | Return HTTP 404 for unknown POST paths. |
| 200 | `return` | Stop handling the unknown route before parsing data or attempting email. |
| 201 | `supplied = self.headers.get("Authorization", "").encode("utf-8")` | Read the Authorization header, default to empty, and encode it for safe byte comparison. |
| 202 | `expected = ("Bearer " + self.server.api_token).encode("utf-8")` | Construct the required Bearer header from the server's configured API token. |
| 203 | `if not hmac.compare_digest(supplied, expected):` | Use constant-time comparison rather than ordinary equality to check the supplied token bytes. |
| 204 | `self.reply(401, {"error": "A valid Bearer API_TOKEN is required."})` | Return HTTP 401 when authentication fails without revealing the expected token. |
| 205 | `return` | Stop unauthorized processing before reading the event or sending email. |
| 206 | `if self.headers.get_content_type() != "application/json":` | Check the media type while allowing a charset parameter on application/json. |
| 207 | `self.reply(415, {"error": "Use application/json."})` | Return HTTP 415 for a non-JSON content type. |
| 208 | `return` | Stop processing an unsupported body type. |
| 209 | `try:` | Begin protected length parsing, body decoding and event validation. |
| 210 | `if self.headers.get("Transfer-Encoding"):` | Detect Transfer-Encoding, which this minimal server does not implement. |
| 211 | `raise ValueError("Transfer-Encoding is unsupported; send Content-Length.")` | Reject such requests instead of attempting unsupported chunked-body decoding. |
| 212 | `length = int(self.headers.get("Content-Length", "0"))` | Parse Content-Length as an integer, treating an absent value as zero. |
| 213 | `if not 0 < length <= MAX_BODY:` | Require a positive declared length no greater than the configured body limit. |
| 214 | `self.reply(413, {"error": "JSON body must be between 1 byte and 7 MiB."})` | Return HTTP 413 for invalid body lengths or an oversized declared body. |
| 215 | `return` | Stop before allocating or reading the rejected request body. |
| 216 | `data = json.loads(self.rfile.read(length))` | Read exactly the declared number of bytes and parse them as JSON. |
| 217 | `event, raw, subtype = validate_event(data)` | Validate the parsed object and unpack the normalized event, raw bytes and MIME subtype. |
| 218 | `except (ValueError, OverflowError, RecursionError):` | Catch malformed JSON/schema values, integer overflow and excessive nesting as bad input. |
| 219 | `self.reply(400, {"error": "Invalid event: check the documented schema, image, units and timestamps."})` | Return HTTP 400 with a generic schema hint instead of reflecting sensitive input or tracebacks. |
| 220 | `return` | Stop the failed validation path before invoking the analysis stubs. |
| 221 | `except (OSError, TimeoutError):` | Catch network read failures and timeouts separately from invalid event contents. |
| 222 | `self.reply(408, {"error": "Request body could not be read in time."})` | Return HTTP 408 to identify an unreadable or timed-out body. |
| 223 | `return` | Stop processing after the body-read failure response. |
| 224 | `report = analyze(event, raw)` | Run the three mock-analysis stages only after authentication and validation succeed. |
| 225 | `if self.path == "/preview":` | Check whether the caller requested a preview rather than email delivery. |
| 226 | `self.reply(200, {"email_status": "not_sent_preview", "report": report})` | Return the report with explicit not_sent_preview status and HTTP 200. |
| 227 | `return` | Stop the preview path so it can never fall through into SMTP sending. |
| 228 | `try:` | Begin protected email sending so SMTP problems produce an explicit API result. |
| 229 | `send_email(report, raw, subtype)` | Pass the report and original image to the real SMTP sender. |
| 230 | `except (ValueError, OSError, smtplib.SMTPException):` | Catch configuration errors, socket failures and SMTP protocol/authentication/delivery exceptions. |
| 231 | `self.reply(502, {"email_status": "failed_or_unconfirmed", "report": report,` | Return HTTP 502, mark sending failed or unconfirmed, and preserve the report for the caller. |
| 232 | `"error": "SMTP failed. Check local configuration and provider status before retrying."})` | Provide a configuration/provider hint without exposing the raw SMTP exception or credentials. |
| 233 | `return` | Stop the failed send path so it cannot claim SMTP acceptance. |
| 234 | `self.reply(200, {"email_status": "accepted_by_smtp", "report": report})` | Return HTTP 200 with accepted_by_smtp only after sending completes without a caught exception. |
| 237 | `def main():` | Define the main function: Start on loopback only; require a token. Stops on Ctrl+C; writes no patient files. |
| 238 | `"""Start on loopback only; require a token. Stops on Ctrl+C; writes no patient files."""` | Document the surrounding module or callable: Start on loopback only; require a token. Stops on Ctrl+C; writes no patient files. |
| 239 | `token = os.environ.get("API_TOKEN", "")` | Read the API token from the environment; an absent token becomes an empty string. |
| 240 | `if len(token) < 16:` | Require at least 16 characters before starting the server; the setup guide recommends a randomly generated token. |
| 241 | `raise SystemExit("Set API_TOKEN to a random secret of at least 16 characters.")` | Exit with a setup message if the token is missing or too short. |
| 242 | `server = HTTPServer(("127.0.0.1", int(os.environ.get("PORT", "8000"))), Handler)` | Bind the HTTPServer to loopback on PORT (default 8000) and register the request handler. |
| 243 | `server.api_token = token` | Attach the configured token to the server object for authenticated POST handling. |
| 244 | `print(f"Demo API listening on http://127.0.0.1:{server.server_port}; Ctrl+C to stop.")` | Print the actual listening address after binding succeeds, without displaying the token. |
| 245 | `try:` | Enter a protected serving loop so interruption still triggers socket cleanup. |
| 246 | `server.serve_forever()` | Process requests sequentially until the process is interrupted. |
| 247 | `except KeyboardInterrupt:` | Catch Ctrl+C as a normal interactive shutdown request. |
| 248 | `pass` | Take no additional action for that interruption; cleanup happens in finally. |
| 249 | `finally:` | Ensure the following cleanup runs whether serving ends normally or by exception. |
| 250 | `server.server_close()` | Close the listening socket rather than leaving the server resource open. |
| 253 | `if __name__ == "__main__":` | Start the application only when this file is executed directly, allowing tests to import it without starting a server. |
| 254 | `main()` | Invoke the startup function under that direct-execution guard. |

## test_pipeline.py

| Line | Source | Explanation |
| --- | --- | --- |
| 1 | `"""Standard-library tests; no external email, credentials, downloads or AI calls."""` | Document the surrounding module or callable: Standard-library tests; no external email, credentials, downloads or AI calls. |
| 3 | `import base64` | Import base64 from the standard library to encode or decode image bytes in the JSON transport. |
| 4 | `import copy` | Import copy from the standard library to make independent nested event variants without mutating the baseline. |
| 5 | `import http.client` | Import http.client from the standard library to send real loopback HTTP requests to the server under test. |
| 6 | `import json` | Import json from the standard library to serialize reports and parse request bodies. |
| 7 | `import os` | Import os from the standard library to read configuration from environment variables. |
| 8 | `import socketserver` | Import socketserver from the standard library to implement a temporary in-memory SMTP test receiver. |
| 9 | `import threading` | Import threading from the standard library to run temporary network servers while tests send requests. |
| 10 | `import unittest` | Import unittest from the standard library to organize assertions, isolation and test cleanup. |
| 11 | `from contextlib import contextmanager` | Import contextmanager from the standard library to provide a context manager for temporary test-server lifetimes. |
| 12 | `from email import policy` | Import policy from the standard library to select the email parsing policy for captured MIME messages. |
| 13 | `from email.parser import BytesParser` | Import BytesParser from the standard library to inspect captured message headers, body and attachments. |
| 14 | `from http.server import HTTPServer` | Import HTTPServer from the standard library to serve the local JSON API without third-party dependencies. |
| 15 | `from unittest.mock import patch` | Import patch from the standard library to isolate environment variables and intercept secure SMTP calls. |
| 17 | `import server` | Import the local server module to exercise the application implementation rather than duplicating it. |
| 19 | `PNG = base64.b64decode(` | Begin decoding an embedded one-pixel PNG fixture so tests need no downloaded or user-supplied image. |
| 20 | `"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII="` | Provide the fixture's base64 bytes; this tiny image is synthetic test input. |
| 21 | `)` | Close the multiline expression above; its values and purpose are explained on the preceding lines. |
| 22 | `EVENT = {` | Begin the shared valid event fixture used as the baseline for API tests. |
| 23 | `"patient_id": "demo-patient-001", "meal_captured_at": "2026-11-09T12:00:00+08:00",` | Set a synthetic patient identifier and timezone-qualified meal capture time. |
| 24 | `"image": {"content_base64": base64.b64encode(PNG).decode("ascii")},` | Encode the PNG fixture as the same plain base64 image field expected from hardware. |
| 25 | `"glucose": {"value": 7.2, "unit": "mmol/L", "measured_at": "2026-11-09T11:55:00+08:00"},` | Include a synthetic 7.2 mmol/L original reading with an independent measurement time. |
| 26 | `}` | Close the multiline expression above; its values and purpose are explained on the preceding lines. |
| 27 | `TOKEN = "local-test-token-only"` | Define a fixed token for temporary local test servers only, not production configuration. |
| 30 | `@contextmanager` | Turn the generator into a context manager so test servers can be reliably started and cleaned up. |
| 31 | `def serving(instance):` | Define the serving function: Run a test-only server on a thread, then shut it down and close its socket. |
| 32 | `"""Run a test-only server on a thread, then shut it down and close its socket."""` | Document the surrounding module or callable: Run a test-only server on a thread, then shut it down and close its socket. |
| 33 | `thread = threading.Thread(target=instance.serve_forever, daemon=True)` | Create a daemon thread for the supplied server's serving loop without blocking the test method. |
| 34 | `thread.start()` | Start that thread before yielding the server to the test. |
| 35 | `try:` | Begin the cleanup-protected part of the server context. |
| 36 | `yield instance` | Yield the running instance to the with block so tests can make network requests. |
| 37 | `finally:` | Run cleanup whether a test passes or raises an exception. |
| 38 | `instance.shutdown()` | Ask the serving loop to shut down. |
| 39 | `thread.join(timeout=5)` | Wait up to five seconds for the serving thread to finish. |
| 40 | `instance.server_close()` | Release the test server's listening socket. |
| 43 | `class SMTPReceiver(socketserver.StreamRequestHandler):` | Define the SMTPReceiver class: Minimal local SMTP fixture: capture DATA bytes; accept or reject delivery. |
| 44 | `"""Minimal local SMTP fixture: capture DATA bytes; accept or reject delivery."""` | Document the surrounding module or callable: Minimal local SMTP fixture: capture DATA bytes; accept or reject delivery. |
| 46 | `def handle(self):` | Define the handle function: Serve one SMTP session without authentication; retain its message in memory. |
| 47 | `"""Serve one SMTP session without authentication; retain its message in memory."""` | Document the surrounding module or callable: Serve one SMTP session without authentication; retain its message in memory. |
| 48 | `self.wfile.write(b"220 localhost test receiver\r\n")` | Write an SMTP 220 greeting so smtplib recognizes a ready test receiver. |
| 49 | `while True:` | Read SMTP commands repeatedly until the client quits or disconnects. |
| 50 | `line = self.rfile.readline()` | Read one command line from the connected SMTP client. |
| 51 | `if not line:` | Detect an empty read, meaning the client disconnected. |
| 52 | `return` | Stop the handler after disconnection instead of looping forever. |
| 53 | `command = line.split(b" ", 1)[0].strip().upper()` | Extract the first command token, strip whitespace and uppercase it for dispatch. |
| 54 | `if command == b"DATA":` | Recognize DATA as the start of the actual email message body. |
| 55 | `self.wfile.write(b"354 End with dot\r\n")` | Send SMTP 354 to tell the client to transmit the MIME message. |
| 56 | `parts = []` | Create an in-memory list of message-body lines. |
| 57 | `while True:` | Read body lines until SMTP's terminating dot or an unexpected disconnect. |
| 58 | `part = self.rfile.readline()` | Read the next data line from the network stream. |
| 59 | `if part in (b".\r\n", b""):` | Check for the terminating dot line or end-of-stream. |
| 60 | `break` | Leave the body loop on termination rather than including the dot in the captured message. |
| 61 | `parts.append(part[1:] if part.startswith(b"..") else part)` | Reverse SMTP dot-stuffing for lines starting with two dots and append the resulting message line. |
| 62 | `self.server.messages.append(b"".join(parts))` | Join and retain the received bytes in memory for later MIME and attachment assertions. |
| 63 | `self.wfile.write(b"550 Rejected for test\r\n" if self.server.reject else b"250 Accepted\r\n")` | Return a deliberate SMTP 550 rejection or 250 acceptance according to the test case. |
| 64 | `elif command == b"QUIT":` | Recognize QUIT as the end of an SMTP session. |
| 65 | `self.wfile.write(b"221 Bye\r\n")` | Send SMTP 221 to acknowledge closing the session. |
| 66 | `return` | Exit after QUIT so the connection can close normally. |
| 67 | `else:` | Use the general acknowledgement branch for other fixture commands such as EHLO, MAIL and RCPT. |
| 68 | `self.wfile.write(b"250 OK\r\n")` | Acknowledge those commands with 250; this fixture intentionally implements only the test's minimal SMTP subset. |
| 71 | `class PipelineTests(unittest.TestCase):` | Define the PipelineTests class: Verify mock semantics, validation, HTTP behavior and real local SMTP transport. |
| 72 | `"""Verify mock semantics, validation, HTTP behavior and real local SMTP transport."""` | Document the surrounding module or callable: Verify mock semantics, validation, HTTP behavior and real local SMTP transport. |
| 74 | `def setUp(self):` | Define the setUp function: Start an isolated HTTP server; each test gets independent state. |
| 75 | `"""Start an isolated HTTP server; each test gets independent state."""` | Document the surrounding module or callable: Start an isolated HTTP server; each test gets independent state. |
| 76 | `self.http = HTTPServer(("127.0.0.1", 0), server.Handler)` | Create a new loopback HTTP server on an operating-system-assigned unused port for each test. |
| 77 | `self.http.api_token = TOKEN` | Configure that server to accept the local test token. |
| 78 | `self.running = serving(self.http)` | Create its lifetime context manager and retain it on the test instance. |
| 79 | `self.running.__enter__()` | Enter the context manually to start serving before the test runs. |
| 80 | `self.addCleanup(self.running.__exit__, None, None, None)` | Register context exit with unittest cleanup so sockets close even after assertion failures. |
| 82 | `def request(self, data=EVENT, path="/preview", token=TOKEN, content_type="application/json"):` | Define the request function: POST JSON over a real loopback socket; return (HTTP status, parsed dict). |
| 83 | `"""POST JSON over a real loopback socket; return (HTTP status, parsed dict)."""` | Document the surrounding module or callable: POST JSON over a real loopback socket; return (HTTP status, parsed dict). |
| 84 | `connection = http.client.HTTPConnection("127.0.0.1", self.http.server_port, timeout=5)` | Open an HTTP client targeting the temporary server, with a five-second socket timeout. |
| 85 | `try:` | Ensure request processing is followed by connection cleanup. |
| 86 | `body = json.dumps(data).encode("utf-8")` | Encode the selected fixture or malformed variant as UTF-8 JSON bytes. |
| 87 | `connection.request("POST", path, body, {"Content-Type": content_type,` | POST to the selected path with the selected Content-Type header, allowing tests to vary the media type. |
| 88 | `"Authorization": "Bearer " + token})` | Include the selected Bearer token so tests can exercise authorized and unauthorized requests. |
| 89 | `response = connection.getresponse()` | Wait for the HTTP response from the real server socket. |
| 90 | `return response.status, json.loads(response.read())` | Return both its numeric status and decoded JSON object for assertions. |
| 91 | `finally:` | Run connection cleanup regardless of a request or assertion failure. |
| 92 | `connection.close()` | Close the HTTP client connection to avoid leaking sockets between tests. |
| 94 | `def test_preview_preserves_original_and_marks_simulation(self):` | Define the test_preview_preserves_original_and_marks_simulation function: test preview preserves original and marks simulation |
| 95 | `status, result = self.request()` | Submit the default valid fixture through the preview endpoint. |
| 96 | `self.assertEqual(status, 200)` | Require HTTP 200 for that valid preview. |
| 97 | `self.assertEqual(result["email_status"], "not_sent_preview")` | Require explicit not_sent_preview status rather than a claim that email was sent. |
| 98 | `report = result["report"]` | Extract the report dictionary for the remaining semantic assertions. |
| 99 | `self.assertEqual(report["original_information"]["glucose"], EVENT["glucose"])` | Check that the original glucose value, unit and timestamp survive unchanged. |
| 100 | `self.assertEqual(report["estimated_current_glucose"]["estimate"], 140)` | Check that the glucose-model placeholder produces its documented fixed 140 mg/dL example. |
| 101 | `self.assertFalse(report["uncertainty"]["validated"])` | Require uncertainty to be explicitly marked unvalidated. |
| 102 | `self.assertIsNone(report["uncertainty"]["confidence_level"])` | Require a null confidence level so the illustrative interval is not presented as statistically validated. |
| 103 | `self.assertIn("Do not use", report["warning"])` | Require the output warning to include its restriction on clinical use. |
| 105 | `def test_missing_glucose_is_not_invented(self):` | Define the test_missing_glucose_is_not_invented function: test missing glucose is not invented |
| 106 | `event = copy.deepcopy(EVENT)` | Deep-copy the nested fixture so removing fields cannot mutate the shared baseline. |
| 107 | `del event["glucose"]` | Remove the glucose reading to represent hardware that did not capture one. |
| 108 | `status, result = self.request(event)` | Submit the modified event to the preview endpoint. |
| 109 | `self.assertEqual(status, 200)` | Require a valid response even when a glucose reading is absent. |
| 110 | `self.assertIsNone(result["report"]["original_information"]["glucose"])` | Require missing measured information to remain null rather than becoming a synthetic reading. |
| 111 | `self.assertIn("not provided", result["report"]["suggestions"])` | Require the suggestion template to acknowledge that the measurement was not provided. |
| 113 | `def test_mgdl_and_jpeg_supported(self):` | Define the test_mgdl_and_jpeg_supported function: test mgdl and jpeg supported |
| 114 | `event = copy.deepcopy(EVENT)` | Copy the baseline before exercising the alternative measurement unit and image signature. |
| 115 | `event["glucose"].update(value=130, unit="mg/dL")` | Set the synthetic original measurement to 130 mg/dL to verify support for the second documented unit. |
| 116 | `event["image"]["content_base64"] = base64.b64encode(b"\xff\xd8\xfffixture").decode()` | Supply bytes with a JPEG signature; this tests signature acceptance, not full JPEG validity. |
| 117 | `normalized, raw, subtype = server.validate_event(event)` | Validate the event directly and obtain normalized fields, bytes and subtype. |
| 118 | `self.assertEqual((normalized["glucose"]["value"], subtype), (130, "jpeg"))` | Require the original value to remain 130 and the detected subtype to be jpeg. |
| 120 | `def test_rejects_invalid_measurements(self):` | Define the test_rejects_invalid_measurements function: test rejects invalid measurements |
| 121 | `for value in (-1, 0, True, "7.2", float("nan"), float("inf")):` | Iterate negative, zero, boolean, text, NaN and infinity readings to cover invalid numeric inputs. |
| 122 | `with self.subTest(value=value):` | Label each numeric variant as a subtest so failures identify the offending input. |
| 123 | `event = copy.deepcopy(EVENT)` | Deep-copy the valid event independently for this numeric case. |
| 124 | `event["glucose"]["value"] = value` | Insert the current invalid measurement into the copy. |
| 125 | `self.assertEqual(self.request(event)[0], 400)` | Require HTTP 400 for each invalid reading rather than accepting it as clinical data. |
| 127 | `def test_rejects_bad_units_times_and_images(self):` | Define the test_rejects_bad_units_times_and_images function: test rejects bad units times and images |
| 128 | `for section, field, value in (` | Begin iterating malformed field variants while preserving all unrelated fixture fields. |
| 129 | `("glucose", "unit", "unknown"), ("glucose", "measured_at", "2026-11-09T12:00:00"),` | Include an unknown glucose unit and a measurement timestamp without a timezone. |
| 130 | `("image", "content_base64", "???"), ("image", "content_base64", "aGVsbG8="),` | Include invalid base64 characters and valid base64 that decodes to a non-image payload. |
| 131 | `):` | Finish the variant list and enter its loop body. |
| 132 | `with self.subTest(field=field):` | Label each malformed-field case for readable failure reports. |
| 133 | `event = copy.deepcopy(EVENT)` | Copy the baseline event so cases remain independent. |
| 134 | `event[section][field] = value` | Replace exactly the chosen nested field with the malformed value. |
| 135 | `self.assertEqual(self.request(event)[0], 400)` | Require HTTP 400 for that single invalid-field variant. |
| 136 | `self.assertEqual(self.request([])[0], 400)` | Also require HTTP 400 when the top-level JSON value is an array instead of an object. |
| 138 | `def test_authentication_and_content_type(self):` | Define the test_authentication_and_content_type function: test authentication and content type |
| 139 | `self.assertEqual(self.request(token="wrong")[0], 401)` | Require HTTP 401 for a wrong Bearer token. |
| 140 | `self.assertEqual(self.request(content_type="text/plain")[0], 415)` | Require HTTP 415 when the content type is text/plain rather than JSON. |
| 141 | `self.assertEqual(self.request(path="/unknown")[0], 404)` | Require HTTP 404 for an unknown POST route. |
| 143 | `def test_body_limit(self):` | Define the test_body_limit function: test body limit |
| 144 | `with patch.object(server, "MAX_BODY", 2):` | Temporarily lower the body limit to two bytes so an ordinary fixture exercises the oversized-body path cheaply. |
| 145 | `self.assertEqual(self.request()[0], 413)` | Require HTTP 413 for a request exceeding the temporary limit. |
| 147 | `def test_health_and_malformed_json(self):` | Define the test_health_and_malformed_json function: test health and malformed json |
| 148 | `connection = http.client.HTTPConnection("127.0.0.1", self.http.server_port, timeout=5)` | Create a separate real HTTP client for GET and deliberately malformed JSON tests. |
| 149 | `try:` | Protect this connection with unconditional cleanup. |
| 150 | `connection.request("GET", "/health")` | Request the public /health endpoint without any authentication header. |
| 151 | `response = connection.getresponse()` | Read the health response headers and status. |
| 152 | `self.assertEqual((response.status, json.loads(response.read())["status"]), (200, "ok"))` | Require HTTP 200 and status ok in the health body. |
| 153 | `connection.request("POST", "/preview", b"{", {"Content-Type": "application/json",` | POST the incomplete JSON object opening brace to /preview with the correct media type. |
| 154 | `"Authorization": "Bearer " + TOKEN})` | Use the correct API token so this test reaches JSON parsing rather than failing authentication. |
| 155 | `response = connection.getresponse()` | Read the response to the malformed body. |
| 156 | `self.assertEqual(response.status, 400)` | Require HTTP 400 for invalid JSON syntax. |
| 157 | `response.read()` | Consume the body before closing the connection. |
| 158 | `finally:` | Ensure cleanup runs even if one of the status assertions fails. |
| 159 | `connection.close()` | Close this test's HTTP connection. |
| 161 | `def smtp_roundtrip(self, reject=False):` | Define the smtp_roundtrip function: POST an event through HTTP and real SMTP to a private in-memory receiver. |
| 162 | `"""POST an event through HTTP and real SMTP to a private in-memory receiver."""` | Document the surrounding module or callable: POST an event through HTTP and real SMTP to a private in-memory receiver. |
| 163 | `receiver = socketserver.TCPServer(("127.0.0.1", 0), SMTPReceiver)` | Create a local SMTP receiver on an operating-system-assigned port; no external provider is contacted. |
| 164 | `receiver.messages, receiver.reject = [], reject` | Initialize its captured-message list and choose whether the receiver should reject DATA. |
| 165 | `with serving(receiver), patch.dict(os.environ, {` | Start the receiver and replace environment variables only within this test context. |
| 166 | `"SMTP_HOST": "127.0.0.1", "SMTP_PORT": str(receiver.server_address[1]),` | Point SMTP settings to that loopback receiver and its dynamically assigned port. |
| 167 | `"SMTP_MODE": "plain", "SMTP_FROM": "sender@example.test", "SMTP_TO": "caregiver@example.test",` | Use explicitly local plaintext transport and synthetic sender/recipient addresses for fixture delivery. |
| 168 | `}, clear=True):` | Clear unrelated environment settings for isolation and enter the SMTP test block. |
| 169 | `status, result = self.request(path="/events")` | POST to /events, traversing validation, mock analysis and real SMTP transmission through sockets. |
| 170 | `return status, result, receiver.messages` | Return HTTP results and the bytes captured by the test receiver for verification. |
| 172 | `def test_real_smtp_delivery_and_attachment(self):` | Define the test_real_smtp_delivery_and_attachment function: test real smtp delivery and attachment |
| 173 | `status, result, messages = self.smtp_roundtrip()` | Run the HTTP-to-SMTP helper with message acceptance enabled. |
| 174 | `self.assertEqual((status, result["email_status"], len(messages)), (200, "accepted_by_smtp", 1))` | Require HTTP 200, accepted_by_smtp status and exactly one received message. |
| 175 | `message = BytesParser(policy=policy.default).parsebytes(messages[0])` | Parse the captured MIME bytes using the standard email policy for structured inspection. |
| 176 | `self.assertEqual(message["To"], "caregiver@example.test")` | Require the message recipient to match the configured synthetic caregiver address. |
| 177 | `self.assertIn("SIMULATED DEMO", message["Subject"])` | Require the visible subject to identify the email as a simulated demo. |
| 178 | `attachment, = list(message.iter_attachments())` | Unpack exactly one attachment, making missing or extra attachments fail the test. |
| 179 | `self.assertEqual(attachment.get_payload(decode=True), PNG)` | Decode the attachment and compare it byte for byte with the original PNG fixture. |
| 180 | `self.assertEqual(attachment.get_content_type(), "image/png")` | Require the attachment MIME type to be image/png. |
| 181 | `self.assertIn('"value": 7.2', message.get_body(preferencelist=("plain",)).get_content())` | Require the plain-text report body to include the original 7.2 reading rather than losing it during serialization. |
| 183 | `def test_smtp_rejection_is_failure(self):` | Define the test_smtp_rejection_is_failure function: test smtp rejection is failure |
| 184 | `status, result, messages = self.smtp_roundtrip(reject=True)` | Run the real local SMTP path with the receiver deliberately rejecting the message body. |
| 185 | `self.assertEqual((status, result["email_status"]), (502, "failed_or_unconfirmed"))` | Require HTTP 502 and failed_or_unconfirmed status instead of reporting acceptance. |
| 187 | `def test_missing_smtp_configuration(self):` | Define the test_missing_smtp_configuration function: test missing smtp configuration |
| 188 | `with patch.dict(os.environ, {}, clear=True):` | Temporarily clear all environment variables so no SMTP settings can leak in from the developer's terminal. |
| 189 | `self.assertEqual(self.request(path="/events")[0], 502)` | Require HTTP 502 when /events cannot obtain required SMTP configuration. |
| 191 | `def test_remote_plaintext_smtp_blocked(self):` | Define the test_remote_plaintext_smtp_blocked function: test remote plaintext smtp blocked |
| 192 | `with patch.dict(os.environ, {"SMTP_HOST": "example.test", "SMTP_MODE": "plain",` | Configure a synthetic remote SMTP hostname with plaintext transport to exercise its validation restriction. |
| 193 | `"SMTP_FROM": "a@example.test", "SMTP_TO": "b@example.test"}, clear=True):` | Supply otherwise sufficient sender and recipient settings so the mode restriction is the reason for failure. |
| 194 | `with self.assertRaises(ValueError):` | Require configuration validation to raise ValueError for remote plaintext SMTP. |
| 195 | `server.smtp_settings()` | Call only settings validation; do not attempt a network connection to that hostname. |
| 197 | `def test_starttls_and_login_are_used(self):` | Define the test_starttls_and_login_are_used function: test starttls and login are used |
| 198 | `event, raw, subtype = server.validate_event(EVENT)` | Validate the shared fixture for direct testing of the SMTP sender's secure-mode calls. |
| 199 | `with patch.dict(os.environ, {"SMTP_HOST": "example.test", "SMTP_FROM": "a@example.test",` | Provide synthetic SMTP host/sender settings inside an isolated temporary environment. |
| 200 | `"SMTP_TO": "b@example.test", "SMTP_USER": "test-user",` | Add a synthetic recipient and username for authentication testing. |
| 201 | `"SMTP_PASSWORD": "test-secret"}, clear=True), patch.object(server.smtplib, "SMTP") as smtp:` | Add a dummy test password and replace the SMTP class with a mock so no external connection occurs. |
| 202 | `server.send_email(server.analyze(event, raw), raw, subtype)` | Build the report and invoke the actual email-construction/sending function against the mocked client. |
| 203 | `client = smtp.return_value.__enter__.return_value` | Access the SMTP instance returned by the mocked context manager for method assertions. |
| 204 | `client.starttls.assert_called_once()` | Require STARTTLS to have been invoked exactly once. |
| 205 | `client.login.assert_called_once_with("test-user", "test-secret")` | Require login exactly once with the dummy username and password, verifying credential forwarding. |
| 206 | `client.send_message.assert_called_once()` | Require one send_message call, verifying that secure setup is followed by sending. |
| 209 | `if __name__ == "__main__":` | Run unittest only when this test file is executed directly; importing it merely defines fixtures and tests. |
| 210 | `unittest.main()` | Start unittest discovery/execution for this module under the direct-execution guard. |

## start_local.py

This later addition loads the user-authorized local Gmail settings. It changes no line in `server.py` or `test_pipeline.py`, and preserves manual startup. Blank lines only separate definitions. The credential value is never included in this walkthrough.

| Line | Explanation |
| --- | --- |
| 1 | Document that this launcher reads ignored SMTP settings and that starting it does not send email. |
| 3 | Import argparse to support a validation-only command-line option. |
| 4 | Import json to decode the local configuration object. |
| 5 | Import os to supply configuration through the environment expected by the existing server. |
| 6 | Import secrets to generate an unpredictable API token when one is not already configured. |
| 7 | Import Path to locate configuration beside this script regardless of the working directory. |
| 9 | Import the existing server implementation; its direct-execution guard prevents startup during import. |
| 12 | Define the launcher entry point, with no arguments and no return value. |
| 13 | Document that the function loads settings, validates them and optionally runs the API. |
| 15 | Document that the local JSON file is read and the password is plaintext on disk. |
| 16 | Document that the password is never printed and validation-only mode makes no network connection. |
| 17 | End the function's documentation string. |
| 18 | Build a command-line parser whose description comes from the module documentation. |
| 19 | Add the boolean --check-config flag to check settings without starting the API. |
| 20 | Parse the supplied command-line arguments, rejecting unknown options. |
| 21 | Resolve this script's absolute path and select its sibling .env.smtp.json file. |
| 22 | Read the JSON with utf-8-sig so files written with PowerShell's UTF-8 byte-order mark work too. |
| 23 | Begin mapping SMTP environment-variable suffixes to local JSON keys, covering host, port, mode and username. |
| 24 | Complete the mapping with sender, recipient and password. |
| 25 | Iterate the mapping to populate all seven settings consistently. |
| 26 | Convert each setting to a string and place it in this Python process's SMTP environment. |
| 27 | Begin a protected block whose cleanup removes the password from the process environment. |
| 28 | Reuse the server's existing SMTP validation without connecting to Gmail. |
| 29 | Check the saved password length against Gmail's normal 16-character app password format. |
| 30 | Print a length warning without displaying the password or guessing a correction. |
| 31 | Select validation-only mode when --check-config was supplied. |
| 32 | Explain that only format was checked; no provider authentication or sending occurred. |
| 33 | Return from validation-only mode before token generation or server startup, while still running cleanup. |
| 34 | Keep a supplied API token or generate a new 32-byte URL-safe random token for this launch. |
| 35 | Print the local request-authentication token for the client terminal and flush the output before serving; this is separate from the Gmail password. |
| 36 | Run the existing server entry point using the configured process environment. |
| 37 | Ensure cleanup runs on normal exit, Ctrl+C or an exception in the protected block. |
| 38 | Remove SMTP_PASSWORD from this process's environment; this does not erase the local configuration file. |
| 41 | Invoke the launcher only when executed directly, leaving imports free of startup side effects. |
| 42 | Call main under that direct-execution guard. |

`.env.smtp.json` is private configuration, not application source: host/port/mode select Gmail STARTTLS; user/sender select the authorized sending account; recipient selects the requested destination; password stores the exact supplied test credential with spaces removed. No executable code is loaded from this file. Its contents are intentionally omitted here. The PowerShell launcher briefly created during implementation was removed after execution policy prevented its use; no execution policy was changed.

## Sample image example update

The README's `$imagePath` assignment now points to `prototype/samples/demo-meal.png` in this workspace rather than the nonexistent `C:\path\to\meal.jpg`. This changes only the input file read by the documented client example. The existing byte-reading and base64 conversion lines are unchanged. `samples/README.md` records synthetic provenance, the exact generation prompt and limitations. No Python implementation or test fixture was changed; server startup still does not submit any image automatically.

The README's later TLS example adds two commands: assigning `$env:SSL_CERT_FILE` selects the resolved local Windows-root certificate bundle for child processes of that PowerShell terminal; `python start_local.py` then launches the existing API with that trust bundle inherited. This does not change application source, Windows trust settings or certificate-verification behavior. `.env.smtp-ca.pem` contains public certificates exported from existing Windows trusted root stores, not a private key or SMTP credential.

## Other files

`.gitignore` line 1 excludes Python bytecode cache directories; line 2 excludes individual bytecode files; lines 3 and 4 exclude local environment-secret files; line 5 would allow a future secret-free example environment file; line 6 excludes a common saved input-event filename containing patient information; line 7 excludes exported raw emails. These exclusions help prevent accidental sharing if this folder is later placed under Git.

`README.md` explains startup, environment variables, the request schema, preview/sending commands, output meaning, limitations and verification. Its PowerShell examples set process-local configuration, read an existing image, serialize its bytes and optional reading as JSON, then explicitly choose preview or actual sending. They are instructions, not commands automatically run during development.

`PROGRESS.md` is the single project progress record: it distinguishes implemented functionality, observed checks and remaining provider/deployment verification. This walkthrough is explanatory documentation rather than a second progress log.
