# Automatic demo: complete line-by-line walkthrough

This addition supplies the file-path input and one-command operation requested by the user. It reuses the existing pipeline and preserves the HTTP server as an alternative. No existing code lines were removed or changed. Every nonblank line in the two new Python files is covered below; blank lines only separate definitions.

## run_demo.py

| Line | Source | Explanation |
| --- | --- | --- |
| 1 | `"""Read a meal photo and optional glucose JSON, analyze once, email once, then exit."""` | Document the module or callable: Read a meal photo and optional glucose JSON, analyze once, email once, then exit. |
| 3 | `import argparse` | Import argparse to parse image, glucose and preview options. |
| 4 | `import base64` | Import base64 to adapt file bytes to the existing event schema. |
| 5 | `import json` | Import json to read input/configuration files and print reports. |
| 6 | `import os` | Import os to supply process-local SMTP and certificate settings. |
| 7 | `import smtplib` | Import smtplib to recognize SMTP failures without logging raw exception contents. |
| 8 | `from datetime import datetime, timezone` | Import datetime, timezone to format the demo capture-time proxy with an explicit timezone. |
| 9 | `from pathlib import Path` | Import Path to work with local file paths. |
| 11 | `import server` | Import server to reuse the existing validation, mock analysis and SMTP implementation. |
| 13 | `ROOT = Path(__file__).resolve().parent` | Resolve the script's own directory, so default input files do not depend on the terminal's current folder. |
| 16 | `def read_event(image_path, glucose_path, patient_id, captured_at=None):` | Define read_event: Paths + patient string + optional ISO timestamp -> validated event, bytes, subtype.. |
| 17 | `"""Paths + patient string + optional ISO timestamp -> validated event, bytes, subtype.` | Document the module or callable: Paths + patient string + optional ISO timestamp -> validated event, bytes, subtype. |
| 19 | `Missing glucose files mean no measurement; malformed existing files fail.` | Document the module or callable: Missing glucose files mean no measurement; malformed existing files fail. |
| 20 | `Glucose JSON contains value, unit and measured_at. Units follow server.py.` | Document the module or callable: Glucose JSON contains value, unit and measured_at. Units follow server.py. |
| 21 | `Without captured_at, the image's file modification time is used as a demo proxy.` | Document the module or callable: Without captured_at, the image's file modification time is used as a demo proxy. |
| 22 | `Reads local files only and sends nothing.` | Document the module or callable: Reads local files only and sends nothing. |
| 23 | `"""` | Document the module or callable:  |
| 24 | `if image_path.stat().st_size > server.MAX_IMAGE:` | Check the image file size before reading the contents, using the existing server limit. |
| 25 | `raise ValueError("Image exceeds the 5 MiB limit.")` | Reject images exceeding 5 MiB before attempting analysis or SMTP. |
| 26 | `raw = image_path.read_bytes()` | Read the selected image file into bytes; this is the explicit file-path input the original server lacked. |
| 27 | `glucose = None` | Initialize measured glucose to None so absent files never fabricate a reading. |
| 28 | `if glucose_path.is_file():` | Check whether the selected optional glucose path points to a file. |
| 29 | `glucose = json.loads(glucose_path.read_text(encoding="utf-8-sig"))` | Read and parse the existing glucose JSON; utf-8-sig accepts PowerShell's UTF-8 byte-order mark. Invalid JSON raises an error. |
| 30 | `captured_at = captured_at or datetime.fromtimestamp(image_path.stat().st_mtime, timezone.utc).isoformat()` | Use the supplied capture timestamp, or convert the image's modification time into a timezone-qualified UTC demo proxy. |
| 31 | `data = {"patient_id": patient_id, "meal_captured_at": captured_at,` | Begin the existing server's event schema with patient identifier and capture timestamp. |
| 32 | `"image": {"content_base64": base64.b64encode(raw).decode("ascii")}, "glucose": glucose}` | Encode the image bytes into the server's base64 field and include the optional measured glucose object. |
| 33 | `return server.validate_event(data)` | Reuse all existing event validation and return the normalized event, original bytes and image subtype. |
| 36 | `def load_mail_settings():` | Define load_mail_settings: Read ignored SMTP JSON and optional CA bundle into this process; never print secrets.. |
| 37 | `"""Read ignored SMTP JSON and optional CA bundle into this process; never print secrets."""` | Document the module or callable: Read ignored SMTP JSON and optional CA bundle into this process; never print secrets. |
| 38 | `config = json.loads((ROOT / ".env.smtp.json").read_text(encoding="utf-8-sig"))` | Read the private SMTP JSON beside the script without logging its contents. |
| 39 | `fields = {"HOST": "host", "PORT": "port", "MODE": "mode", "USER": "user",` | Map SMTP host, port, encryption mode and user environment suffixes to their configuration keys. |
| 40 | `"FROM": "sender", "TO": "recipient", "PASSWORD": "password"}` | Complete the mapping with sender, recipient and password so the existing SMTP sender can be reused. |
| 41 | `for suffix, key in fields.items():` | Iterate the field mapping without copying credential values into source code. |
| 42 | `os.environ["SMTP_" + suffix] = str(config[key])` | Set each SMTP variable only in this Python process, converting the numeric port to text. |
| 43 | `bundle = ROOT / ".env.smtp-ca.pem"` | Locate the previously exported Windows trusted-root certificate bundle beside the script. |
| 44 | `if bundle.is_file() and not os.environ.get("SSL_CERT_FILE"):` | Use that bundle only when it exists and the caller has not already selected SSL_CERT_FILE. |
| 45 | `os.environ["SSL_CERT_FILE"] = str(bundle)` | Set SSL_CERT_FILE for this process's verified TLS connections; certificate verification is not disabled. |
| 46 | `server.smtp_settings()` | Validate SMTP configuration through the existing server helper before any sending. |
| 49 | `def main(argv=None):` | Define main: CLI arguments -> exit code. Default sends one real email; --preview sends none.. |
| 50 | `"""CLI arguments -> exit code. Default sends one real email; --preview sends none.` | Document the module or callable: CLI arguments -> exit code. Default sends one real email; --preview sends none. |
| 52 | `Optional argv is a list of argument strings for testing. Local SMTP settings` | Document the module or callable: Optional argv is a list of argument strings for testing. Local SMTP settings |
| 53 | `and public CA certificates are loaded only for a send. No HTTP server starts.` | Document the module or callable: and public CA certificates are loaded only for a send. No HTTP server starts. |
| 54 | `"""` | Document the module or callable:  |
| 55 | `parser = argparse.ArgumentParser(description=__doc__)` | Create a command-line parser with the module's explanation as its description. |
| 56 | `parser.add_argument("--image", type=Path, default=ROOT / "samples" / "demo-meal.png")` | Accept an image path, defaulting to the bundled generated meal image. |
| 57 | `parser.add_argument("--glucose", type=Path, default=ROOT / "samples" / "glucose.json")` | Accept an optional glucose JSON path, defaulting to samples/glucose.json; the file need not exist. |
| 58 | `parser.add_argument("--patient-id", default="demo-patient-001")` | Accept a patient identifier, using a clearly synthetic default for demonstrations. |
| 59 | `parser.add_argument("--captured-at", help="Actual ISO 8601 meal capture time with timezone, if known.")` | Accept an actual timezone-qualified meal capture time as an optional override. |
| 60 | `parser.add_argument("--preview", action="store_true", help="Print the report without sending email.")` | Add a boolean preview flag that prints analysis without email. |
| 61 | `args = parser.parse_args(argv)` | Parse the supplied argument list or the process command line when argv is None. |
| 62 | `try:` | Protect file loading, analysis and email operations so expected errors become a nonzero exit status. |
| 63 | `event, raw, subtype = read_event(args.image, args.glucose, args.patient_id, args.captured_at)` | Read the selected files and validate the assembled event before any SMTP configuration or sending. |
| 64 | `report = server.analyze(event, raw)` | Call the existing mock-analysis pipeline with that event and its decoded image bytes. |
| 65 | `print("Image:", args.image)` | Print the image path to make the chosen input visible to the user. |
| 66 | `print("Measured glucose:", "provided" if event["glucose"] is not None else "unavailable")` | Print whether a measured reading was provided, without confusing a missing reading with a synthetic estimate. |
| 67 | `if args.preview:` | Choose the non-sending branch when preview was requested. |
| 68 | `print(json.dumps(report, indent=2, ensure_ascii=False))` | Print the complete indented report, including original information and demo labels, for local inspection. |
| 69 | `print("Preview complete; no email sent.")` | Explicitly state that preview did not send an email. |
| 70 | `return 0` | Return success from preview before any mail configuration is loaded or network operation is attempted. |
| 71 | `load_mail_settings()` | Load the saved SMTP account and optional trust bundle automatically for a normal run. |
| 72 | `server.send_email(report, raw, subtype)` | Invoke the real existing SMTP sender once, passing the report and original image attachment. |
| 73 | `print("Email accepted by SMTP for", os.environ["SMTP_TO"], "(inbox delivery not confirmed).")` | Report the configured recipient and SMTP acceptance while explicitly withholding an inbox-delivery claim. |
| 74 | `return 0` | Return success after sending completes without a caught failure. |
| 75 | `except (OSError, ValueError, KeyError, TypeError, OverflowError, smtplib.SMTPException) as error:` | Catch expected filesystem, validation, configuration and SMTP/network errors without printing credential-bearing exception details. |
| 76 | `print("Failed or unconfirmed (" + type(error).__name__ + "). Check input files and local SMTP/TLS settings before retrying.")` | Print only the error class and a troubleshooting hint; failures after possible SMTP acceptance remain unconfirmed, not automatically retried. |
| 77 | `return 1` | Return exit status 1 to indicate a failed or uncertain run. |
| 78 | `finally:` | Ensure password cleanup occurs after preview, success or a caught/uncaught exception in the protected block. |
| 79 | `os.environ.pop("SMTP_PASSWORD", None)` | Remove SMTP_PASSWORD from the process environment; this does not erase the authorized local configuration file. |
| 82 | `if __name__ == "__main__":` | Run the command-line entry point only when executed directly, allowing tests to import the module safely. |
| 83 | `raise SystemExit(main())` | Convert main's numeric result into the operating-system exit status, with zero meaning success. |

## test_demo.py

| Line | Source | Explanation |
| --- | --- | --- |
| 1 | `"""Check file-based automation without contacting a real mail provider."""` | Document the module or callable: Check file-based automation without contacting a real mail provider. |
| 3 | `import contextlib` | Import contextlib to capture console output while tests inspect side effects. |
| 4 | `import io` | Import io to hold captured output in memory. |
| 5 | `import json` | Import json to read input/configuration files and print reports. |
| 6 | `import os` | Import os to supply process-local SMTP and certificate settings. |
| 7 | `import tempfile` | Import tempfile to isolate and clean up test input/configuration files. |
| 8 | `import unittest` | Import unittest to organize assertions and cleanup. |
| 9 | `from pathlib import Path` | Import Path to work with local file paths. |
| 10 | `from unittest.mock import patch` | Import patch to replace external side effects and isolate environment settings. |
| 12 | `import run_demo` | Import run_demo to test the actual file-based runner. |
| 13 | `from test_pipeline import PNG` | Import PNG to reuse the established tiny PNG fixture. |
| 16 | `class DemoTests(unittest.TestCase):` | Define DemoTests: Exercise optional JSON handling and the single-send versus preview boundary.. |
| 17 | `"""Exercise optional JSON handling and the single-send versus preview boundary."""` | Document the module or callable: Exercise optional JSON handling and the single-send versus preview boundary. |
| 19 | `def setUp(self):` | Define setUp: prepare independent test files. |
| 20 | `self.directory = tempfile.TemporaryDirectory()` | Create a temporary directory for independent synthetic test files; no actual patient input is used. |
| 21 | `self.addCleanup(self.directory.cleanup)` | Register directory cleanup with unittest, including when a test fails. |
| 22 | `self.root = Path(self.directory.name)` | Represent the temporary directory as a Path for portable file operations. |
| 23 | `self.image = self.root / "meal.png"` | Choose a temporary image filename for this individual test. |
| 24 | `self.image.write_bytes(PNG)` | Write the existing tiny PNG fixture to that file so the runner must read an actual path. |
| 25 | `self.glucose = self.root / "glucose.json"` | Choose the optional glucose path without creating the file, exercising absent-file behavior by default. |
| 26 | `self.args = ["--image", str(self.image), "--glucose", str(self.glucose)]` | Build explicit CLI arguments pointing to these isolated test files, avoiding project images or credentials. |
| 28 | `def test_absent_glucose_remains_null(self):` | Define test_absent_glucose_remains_null: check absent glucose remains null. |
| 29 | `event, raw, subtype = run_demo.read_event(self.image, self.glucose, "demo")` | Read the temporary image while the glucose JSON file is absent. |
| 30 | `self.assertIsNone(event["glucose"])` | Require absent measured glucose to remain None rather than becoming a synthetic measurement. |
| 31 | `self.assertEqual((raw, subtype), (PNG, "png"))` | Require exact image-byte preservation and PNG subtype detection. |
| 33 | `def test_existing_glucose_preserved(self):` | Define test_existing_glucose_preserved: check existing glucose preserved. |
| 34 | `measurement = {"value": 7.2, "unit": "mmol/L", "measured_at": "2026-11-09T12:00:00+08:00"}` | Define one synthetic mmol/L reading with a timezone-qualified measurement timestamp. |
| 35 | `self.glucose.write_text(json.dumps(measurement), encoding="utf-8-sig")` | Write the reading as UTF-8 JSON with a byte-order mark to test compatibility with PowerShell-created files. |
| 36 | `event, raw, subtype = run_demo.read_event(self.image, self.glucose, "demo")` | Load both files through the actual runner's file adapter. |
| 37 | `self.assertEqual(event["glucose"], measurement)` | Require the original value, unit and time to survive unchanged. |
| 39 | `def test_preview_never_loads_mail_or_sends(self):` | Define test_preview_never_loads_mail_or_sends: check preview never loads mail or sends. |
| 40 | `with patch.object(run_demo, "load_mail_settings") as load, patch.object(run_demo.server, "send_email") as send, contextlib.redirect_stdout(io.StringIO()):` | Mock mail configuration loading and SMTP sending, and capture output, so the preview boundary can be inspected without side effects. |
| 41 | `self.assertEqual(run_demo.main(self.args + ["--preview"]), 0)` | Run preview and require success. |
| 42 | `load.assert_not_called()` | Require preview never to load SMTP settings. |
| 43 | `send.assert_not_called()` | Require preview never to call the mail sender. |
| 45 | `def test_normal_run_sends_once(self):` | Define test_normal_run_sends_once: check normal run sends once. |
| 46 | `with patch.object(run_demo, "load_mail_settings"), patch.object(run_demo.server, "send_email") as send, patch.dict(os.environ, {"SMTP_TO": "test@example.test"}), contextlib.redirect_stdout(io.StringIO()):` | Mock configuration and the sender, supply a synthetic recipient in a temporary environment and suppress console output for a normal-run test. |
| 47 | `self.assertEqual(run_demo.main(self.args), 0)` | Run the default sending branch and require successful completion against the mock sender. |
| 48 | `send.assert_called_once()` | Require exactly one send call, rejecting accidental duplicate invocations. |
| 49 | `report, attachment, subtype = send.call_args.args` | Extract the arguments passed to that send call for payload inspection. |
| 50 | `self.assertIsNone(report["original_information"]["glucose"])` | Require a missing original glucose reading to remain null in the emailed report. |
| 51 | `self.assertEqual(attachment, PNG)` | Require the attachment to contain the exact input PNG bytes. |
| 53 | `def test_invalid_existing_json_prevents_send(self):` | Define test_invalid_existing_json_prevents_send: check invalid existing json prevents send. |
| 54 | `self.glucose.write_text("{", encoding="utf-8")` | Write incomplete JSON into an existing glucose file, distinguishing malformed from absent input. |
| 55 | `with patch.object(run_demo.server, "send_email") as send, contextlib.redirect_stdout(io.StringIO()):` | Intercept the sender and capture output so an invalid-input test cannot send email. |
| 56 | `self.assertEqual(run_demo.main(self.args), 1)` | Require a nonzero failure result for malformed JSON. |
| 57 | `send.assert_not_called()` | Require parsing failure to prevent any send call. |
| 59 | `def test_invalid_reading_prevents_send(self):` | Define test_invalid_reading_prevents_send: check invalid reading prevents send. |
| 60 | `self.glucose.write_text('{"value": -1, "unit": "mmol/L", "measured_at": "2026-11-09T12:00:00Z"}')` | Write syntactically valid JSON with a negative glucose value to exercise semantic validation. |
| 61 | `with patch.object(run_demo.server, "send_email") as send, contextlib.redirect_stdout(io.StringIO()):` | Intercept the mail sender and output for this invalid-measurement case. |
| 62 | `self.assertEqual(run_demo.main(self.args), 1)` | Require failure for an invalid reading instead of silently ignoring the present glucose file. |
| 63 | `send.assert_not_called()` | Require that no email send be attempted after measurement validation fails. |
| 65 | `def test_mail_configuration_and_ca_loaded(self):` | Define test_mail_configuration_and_ca_loaded: check mail configuration and ca loaded. |
| 66 | `settings = {"host": "smtp.example.test", "port": 587, "mode": "starttls", "user": "a@example.test",` | Begin an entirely synthetic SMTP configuration, including a test-only host and account. |
| 67 | `"sender": "a@example.test", "recipient": "b@example.test", "password": "dummy-test-secret"}` | Supply a synthetic recipient and dummy password; no actual credentials appear in the test source. |
| 68 | `(self.root / ".env.smtp.json").write_text(json.dumps(settings), encoding="utf-8-sig")` | Write that test configuration inside the temporary directory using PowerShell-compatible UTF-8 encoding. |
| 69 | `bundle = self.root / ".env.smtp-ca.pem"` | Choose a temporary CA-bundle filename for configuration selection testing. |
| 70 | `bundle.touch()` | Create an empty marker file; this test checks selection only and makes no TLS connection. |
| 71 | `with patch.object(run_demo, "ROOT", self.root), patch.dict(os.environ, {}, clear=True):` | Redirect the runner's root into the temporary directory and isolate all environment variables for this test. |
| 72 | `run_demo.load_mail_settings()` | Run the real configuration loader on the synthetic files. |
| 73 | `self.assertEqual(os.environ["SMTP_TO"], settings["recipient"])` | Require the recipient environment variable to match the temporary configuration. |
| 74 | `self.assertEqual(os.environ["SSL_CERT_FILE"], str(bundle))` | Require SSL_CERT_FILE to point to the temporary bundle automatically. |
| 77 | `if __name__ == "__main__":` | Start unittest only when the test file is run directly; imports merely define the test class. |
| 78 | `unittest.main()` | Invoke unittest's command-line entry point. |

## Documentation changes

The README now starts with `python prototype/run_demo.py`, which runs the new file-based entry point and sends once. Its `--preview` example adds the flag that returns before SMTP loading. Its `--image` and `--glucose` example selects user file paths instead of the bundled defaults. The JSON example defines a synthetic value, unit and measurement time; it is documentation, not a file automatically loaded as a patient reading. The original HTTP-server instructions remain below as an alternative. The main CODE_WALKTHROUGH links to this complete explanation, and PROGRESS records scope, results and limitations without copying credentials.
