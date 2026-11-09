# Prototype progress

## Decisions — 2026-11-09 (Asia/Hong_Kong)

- Authorized scope: Python prototype receiving a meal image and optional measured glucose, replaceable fixed CV/glucose/LLM stubs, real SMTP email to a caregiver.
- User chose SMTP through local environment variables and agreed to clearly labelled simulated outputs, illustrative ranges and no insulin/treatment decisions from mock data.
- Python 3.10.11 is available. Flask, FastAPI, Uvicorn and pytest are absent. Standard-library implementation avoids package/environment changes.
- The existing `prototype` directory was empty. Other checkpoint directories were not modified. The workspace is not a Git repository.

## Completed

- Added `server.py`: authenticated local JSON endpoints (`/preview`, `/events`), public minimal `/health`, schema checks, separate measured/simulated values, fixed gram and mg/dL examples, templated suggestions and real SMTP with original image attachment.
- Added `test_pipeline.py`, `README.md`, `.gitignore` and `CODE_WALKTHROUGH.md`. No existing code was removed.
- SMTP supports verified STARTTLS and implicit TLS; plaintext is restricted to local test hosts. Credentials and recipient addresses come from environment variables.
- The initial pipeline implementation created no patient files or credentials and used no third-party dependencies, AI calls or external messages. A subsequent user-authorized local SMTP configuration is recorded below.

## Verification

- Command from `prototype`: `python -m unittest -v test_pipeline`.
- Initial run: **13 tests passed** on Python 3.10.11.
- Real local HTTP-to-SMTP transport succeeded, and received image bytes matched the supplied PNG. A local SMTP rejection returned HTTP 502 rather than success.
- Checked optional glucose, preserved original mmol/L information, mg/dL/JPEG support, invalid numbers/units/timestamps/images, authentication, content type, body limits, malformed JSON, health response, missing SMTP configuration, remote plaintext restriction and STARTTLS/login invocation.
- Tests start their own temporary loopback servers and close them afterward. No persistent server is left running by the test suite.
- Standalone startup was also verified by launching `python -u server.py` with a generated token and `PORT=0`, reading the bound address, and requesting `/health`: HTTP 200 with `{"status": "ok", "demo": true}`. That temporary child process was then stopped; no application server is left running.
- The walkthrough accounts for all 224 nonblank lines of `server.py` and all 182 nonblank lines of `test_pipeline.py`, plus the ignore rules and documentation purpose.

## Incomplete / requires local configuration

- Gmail authentication, verified STARTTLS and SMTP acceptance were confirmed in the user-authorized sample-image send recorded below. Final delivery into the recipient's inbox is still unconfirmed; check the QQ inbox and spam folder before sending again.
- No calibrated model or validated confidence interval exists. No real CV/LLM analysis, insulin recommendation or emergency detection is implemented; these are explicitly outside the approved demo behavior.
- Physical hardware access requires a later network deployment. The current server binds only to `127.0.0.1`.
- No production deployment, queue, data store, automatic retry, deduplication or live monitoring is configured. None was started or published.

## Next authorized steps

- Run the local server using `python prototype/start_local.py` from the workspace root, or use the original manual environment-variable setup.
- Confirm the previously sent sample email in the QQ inbox or spam folder. Use the documented CA-bundle environment variable for future launches with this Python installation. No credentials should be pasted into chat or committed.

## Local Gmail configuration follow-up — 2026-11-09

- User explicitly authorized use of the supplied temporary test password and supplied sender/recipient addresses. Stored settings in `.env.smtp.json`, covered by the existing `.env.*` ignore rule. No password is copied into application code or documentation.
- Added `start_local.py`, which loads these settings into its own process, checks the SMTP format and starts the original server. The manual startup method and `server.py` are unchanged. Added launcher instructions and a line-by-line explanation.
- Attempted Windows user-bound encryption with `ConvertFrom-SecureString`; it failed because the automation context could not perform the data-protection operation. The initial unusable configuration was replaced with the authorized plaintext test configuration. The password is plaintext on disk; Git ignore does not prevent OneDrive synchronization.
- A PowerShell launcher was attempted but execution policy blocked it. Replaced that newly created launcher with Python; no execution policy or shared environment setting was changed.
- `python start_local.py --check-config` passed configuration-format validation and warned about the 15-character password. This does not verify Google authentication. The configuration filename was checked against the existing ignore pattern. Neither check made network connections or sent email.
- Configured launcher startup was verified in a temporary child process with a generated API token and `PORT=0`; `/health` returned HTTP 200 with the expected demo payload. No SMTP connection was made, and that temporary process was stopped afterward. No server was left running by this check.
- No external email was sent and no Gmail connection was attempted. Correct or revoke the temporary credential locally as needed; its value is deliberately omitted from this record.

## Test credential replacement — 2026-11-09

- At the user's explicit request, replaced only the password field in the ignored `.env.smtp.json` with the newly supplied test password, removing spaces. Sender, recipient and all other configuration fields were preserved. No application code was changed.
- `python start_local.py --check-config` passed without a password-length warning; the saved password now has 16 characters. This was a format check only: no Gmail connection, authentication attempt or email sending occurred.
- No server was started, stopped or restarted for this replacement. A launcher process already running would retain its prior environment until the user restarts it. Credential values are omitted from this record.

## Generated sample and authorized email send — 2026-11-09

- Found no bundled meal photo: automated tests used a one-pixel PNG, and README referred to a placeholder local path. Generated one fictional meal photo with the built-in image-generation tool, saved as `samples/demo-meal.png`, and recorded the full prompt in `samples/README.md`.
- Visually inspected the displayed result: a white plate of rice, chicken, broccoli and carrots, with no text or people. The copied PNG is 2,555,835 bytes, within the 5 MiB image limit. Existing `validate_event` accepted it; `analyze` produced the expected simulated report. README now uses this sample path and the walkthrough explains that changed example line. No application code or test fixtures changed.
- User explicitly requested sending the sample image with analysis to the configured recipient. Used `validate_event`, `analyze` and `send_email` directly, with patient ID `demo-patient-001`, a current UTC demonstration event timestamp and `glucose=null`; no measured reading was fabricated. The synthetic image is not an actual patient capture.
- First send failed at TLS certificate verification before login or message submission. Diagnosis found MSYS2 Python 3.10.11 with zero certificates in its default SSL context and no `ssl.enum_certificates` support. That first attempt did not submit a message.
- Exported 69 existing Windows trusted root certificates from the local-machine/current-user root stores into ignored `.env.smtp-ca.pem`. Selected it through `SSL_CERT_FILE` only for the send process; the resulting context loaded 69 certificates (67 marked CA). No download, installation, system trust change or disabling of verification occurred. README documents how to select this bundle for later launches.
- The subsequent verified-STARTTLS send successfully authenticated to Gmail and returned from `send_email`: **accepted_by_smtp**, sender `SMTP_FROM (local configuration)`, recipient `SMTP_TO (local configuration)`. Subject: `[SIMULATED DEMO] Meal and glucose caregiver report`. Original generated image attached as `meal.png`; report includes demo warnings, fixed sugar/carbohydrate/current-glucose estimates, illustrative ranges, original glucose null and templated suggestions.
- Exactly one send reached successful SMTP acceptance. No further retry was made. Inbox placement/receipt has not been independently confirmed. No HTTP server was started, stopped or restarted; no existing workloads were changed.

## Automatic file-based demo — 2026-11-09

- User requested automatic operation instead of manual request construction. Added `run_demo.py`: one invocation loads the default sample image, optionally reads `samples/glucose.json`, validates and analyzes the data, loads the existing private SMTP configuration and optional CA bundle, sends one email and exits. Defaults resolve beside the script, so it works from the workspace root. User-specified paths can be relative to the terminal or absolute.
- Optional flags select image/glucose paths, patient ID, actual capture time or preview-only operation. Missing glucose files yield null; malformed existing JSON or invalid readings stop before email sending. File modification time is only a demo capture-time proxy unless overridden. No glucose measurement file was fabricated.
- Original `server.py`, `start_local.py`, SMTP credentials and HTTP workflow were preserved. No background polling, duplicate suppression or automatic retry was added. Re-running the default command sends another email.
- Added `test_demo.py` and `DEMO_WALKTHROUGH.md`; placed one-command instructions first in README and linked the complete source explanation from the main walkthrough.
- Verification: `python -m unittest -v test_demo test_pipeline` passed **20 tests**. New checks cover optional/malformed glucose files, preserved readings, preview avoiding SMTP, one send invocation, and automatic SMTP/CA configuration. Actual sends in these tests are mocked; existing SMTP transport tests use only the local test receiver.
- `python prototype/run_demo.py --preview` successfully processed the bundled 2,555,835-byte meal image from the workspace root and reported measured glucose unavailable. No external email was sent during this change and no HTTP server or background process was started/stopped.
- Next use: `python prototype/run_demo.py` sends one real report using the configured Gmail account and QQ recipient; `--preview` prints it without sending. Provider acceptance for the underlying SMTP sender was already established in the preceding manual demonstration; the new runner's external send was not repeated.

## GitHub publication preparation — 2026-11-09

- User authorized pushing the prototype to `Hantangduheyinglengyuezanghuahun/EMIA2020`. Repository inspection found an empty public repository with default branch `main` and write access.
- Publication scope is the prototype, synthetic sample image and a new root README. Unrelated checkpoint directories are excluded. Added a secret-free `.env.example` for new clones, excluded optional `samples/glucose.json`, made client-example paths portable and replaced personal email addresses in this record with configuration-field references.
- Actual `.env.smtp.json`, exported `.env.smtp-ca.pem`, Python caches and optional patient input remain local. No SMTP settings or working credentials were changed. No Python code or running process was changed for publication; the last relevant verification remains the 20 passing tests and successful sample preview recorded above.
- Local Windows Git required a command-specific safe-directory setting because the automation user differs from the workspace owner. Git metadata writes required filesystem escalation. No global Git trust or TLS setting was changed.
