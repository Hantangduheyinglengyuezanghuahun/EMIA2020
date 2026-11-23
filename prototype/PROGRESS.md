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
- Publication succeeded: pushed initial prototype commit `9824fdd28d8887a02c3a95c210ccacb7e6faf90f` to `origin/main`. GitHub's remote tree was independently checked and contains exactly the 14 intended files, including the synthetic image and secret-free template; no working credentials, CA bundle, caches or checkpoint directories are present.
- The staged-content scan checked all 14 files for the configured SMTP password (compact and spaced forms) and private-key markers before the commit. Neither credential form nor private-key material was found. Unrelated checkpoint folders remain untracked locally.

## Readable email content — 2026-11-11

- User requested readable email content instead of the raw JSON report. Added `email_report.py` and changed `server.send_email` to use its formatter. The body now has patient/meal details, recorded glucose or an unavailable message, separately labelled simulated sugar/carbohydrate/current-glucose estimates with illustrative ranges, caregiver notes, an attachment note and existing demo limitations. Dates display readable text and their original numeric UTC offset.
- Removed the JSON dump only from email bodies. Internal analysis results, HTTP responses, terminal previews, SMTP configuration, image attachment bytes and the existing server/file-runner entry points retain their prior behavior. No treatment rules, real AI analysis or dependencies were added.
- Updated the local SMTP integration test to inspect readable content; added missing-reading and mg/dL-preservation checks. `python -m unittest -v test_demo test_pipeline` passed **22 tests**, including the unchanged image-byte attachment check. All email transport tests remain local or mocked.
- Updated README and current line references in CODE_WALKTHROUGH, added a complete changed-line walkthrough in EMAIL_WALKTHROUGH, and generated a synthetic `samples/demo-email.txt` for review without sending. The sample contains no measured glucose or credentials.
- No external email was sent, running service changed, or commit/push performed in this update. Next invocation of the existing `python prototype/run_demo.py` sends the readable report using the configured account.

## Visual HTML caregiver email — 2026-11-13

- User requested an HTML template, emergency colours, a prominent caregiver action summary, glucose history/latest/forecast charts and food-analysis visualization. Added `email_template.html`, `caregiver_view.py`, `visual_email.py` and `chart_renderer.ps1`. `send_email` now builds a MIME alternative with the existing readable text body, the HTML template, two embedded PNG charts and the original photo as an inline downloadable MIME image. All images are sent as bytes with content IDs; no external image hosting is used.
- Action colours are red for urgent screening, amber for check/review, and teal for no threshold alert. Actual fresh measured readings and reported severe symptoms drive screening; fixed AI estimates and forecasts never do. Missing, synthetic, stale or future-dated readings cannot yield a reassuring card. A 15-minute freshness policy, example 180 mg/dL reference and two-hour repeated-high lookback are explicitly prototype policies requiring clinical review. No insulin timing or dosing was implemented. CDC low-glucose and DKA guidance sources are linked in README and the email footer.
- Added history validation (up to 288 readings) and a backward-compatible glucose JSON envelope with current/history, synthetic and severe_symptoms fields. Existing single-reading files remain supported. History is supplied by the caller, sorted chronologically and not persisted or invented. Charts convert readings to mg/dL; the latest-value card retains the supplied unit. Email display times use Hong Kong time.
- Added fixed, visibly labelled forecast points at +30/+60/+120 minutes with illustrative ranges. Sugar and total carbohydrate bars share a gram scale and show uncertainty whiskers; labels explain that sugar is already included in carbohydrates. Food estimates remain fixed and independent of image content.
- Added `--html-preview PATH` to `run_demo.py`; it saves a self-contained local preview without loading SMTP settings. Added an explicitly synthetic history example. Generated `output/caregiver-history-preview.html`, an inspected browser screenshot `output/caregiver-history-preview.png`, and offline MIME example `output/caregiver-demo.eml` with synthetic addresses. Generated output is Git-ignored because real-input previews could contain health data.
- PNG rendering uses the available Windows System.Drawing library in a hidden PowerShell child process, requiring Windows and installing no dependencies. The renderer receives data through stdin; the PowerShell source is fixed. No execution policy or system settings were changed. First browser capture failed due to the automation context's graphics-process sandbox; an isolated headless Chrome process successfully rendered the synthetic local HTML after a process-only sandbox flag. Its private temporary browser profile was generated under ignored output, separate from user browser profiles.
- Verification: initial combined run found two test-environment failures because existing tests cleared PATH/SystemRoot before launching the renderer. Updated those tests to isolate all SMTP fields while preserving required OS environment. `python -m unittest -v test_demo test_pipeline test_visual_email` then passed **30 tests**. Checks include thresholds, missing/stale/future/synthetic readings, severe symptoms, repeated high readings, units/history parsing, HTML escaping, actual 1200x480 PNG rendering and real loopback SMTP with all embedded images and exact original photo bytes. The HTML rendering/escaping test was rerun after converting display times to Hong Kong time and passed.
- The browser screenshot was inspected: action panel, metrics, line/forecast chart, meal image and food bars render without clipping. The saved .eml contains a plain-text alternative plus HTML and all three CID image parts. Actual Gmail/QQ inbox rendering has not been checked for this new template. No external email, Git commit or push occurred, and no user workload/server was stopped or restarted.
- README/root README explain the new template, command, optional history schema, Windows requirement and clinical limits. VISUAL_EMAIL_WALKTHROUGH provides a line-by-line explanation of every new/modified code line. Earlier walkthroughs are retained with a pointer to the current visual implementation.
- Removed only the isolated browser scratch profile created for this rendering check, after verifying its exact workspace path. Retained the HTML, screenshot, offline email and rendering log as review artifacts. `git diff --check` passed; working edits remain uncommitted.

## Advice-first layout and complete numeric display — 2026-11-13

- User requested immediately visible advice and numbers in blank parts. Moved sugar and medical-help advice inside the first colour-coded card, before metrics and charts, reduced the header height and removed the duplicate lower advice block. Added fixed table layout to keep the email within narrow viewports.
- Added display_readings in visual_email.py: when there are no supplied readings, only the visual display receives five explicitly labelled demo values (108/116/128/145/138 mg/dL) anchored to report time. The current card shows 138 mg/dL with a DEMO label and the chart legend identifies example readings. Actual supplied values are preserved; original_information and caregiver_action are never mutated. Missing clinical data remains missing and cannot produce a reassuring status.
- Replaced vague missing-data/synthetic advice with actionable instructions to check a current meter/CGM reading before sugar changes, follow the prescribed care plan and get help for severe symptoms. These generic instructions are displayed at the top. No clinical thresholds, medication advice or real models were added.
- Added two meaningful regressions for numeric display fill without data/action mutation, advice ordering before metrics, and preservation of supplied readings. `python -m unittest -v test_visual_email test_demo test_pipeline` passed **32 tests**. Renderer/MIME tests continue checking the actual embedded chart PNGs and original image bytes.
- Generated output/caregiver-advice-first.html, desktop screenshot caregiver-advice-first.png, a true 390x844 phone screenshot caregiver-advice-phone.png, and offline MIME example caregiver-advice-first.eml. Inspected the desktop and phone screenshots. Initial CLI phone screenshots used Chrome's minimum desktop viewport and appeared clipped; a process-isolated CDP mobile viewport confirmed innerWidth=390 and scrollWidth=390, with both advice blocks visible in the first screen. Temporary browser profiles were removed after checking their workspace paths; no user browser profile was touched.
- README and the main walkthrough link ADVICE_LAYOUT_WALKTHROUGH for the complete changed-line explanation. No external email, Git commit or push was performed, and no existing service was stopped/restarted.


## Larger glucose chart and visible current estimate - 2026-11-16

- User requested a larger chart and an explicit current glucose estimate. Found that server.mock_glucose_analysis already returns 140 mg/dL with an illustrative 100-190 range, but the HTML template did not render estimated_current_glucose. Added a separate report-derived estimate card before the measured/future cards and after the advice. Added a purple NOW estimate marker, range whisker and dashed connection to the future forecast. Supplied measurements, model behavior, threshold screening and SMTP credentials were unchanged.
- Enlarged email maximum width from 700 to 800 px, reduced glucose-section padding to 12 px, and increased glucose PNG height from 480 to 720 with larger tick/legend labels. At maximum display size the chart is approximately 776 by 466 px instead of 644 by 258 px. Food PNG remains 1200 by 480. Future forecast range text now uses report values with units.
- Verification: python -m unittest -v test_visual_email test_demo test_pipeline passed 33 tests. Regression checks distinguish current estimate, measured glucose and future forecast; verify report-derived ranges, preserve advice order and confirm chart PNG dimensions. Generated output/caregiver-large-chart.html and visually inspected output/caregiver-large-chart.png using isolated headless Chrome (agent-browser CLI unavailable). New current estimate card and purple NOW marker are visible, and chart labels fit.
- Documentation: README and CODE_WALKTHROUGH link CHART_ESTIMATE_WALKTHROUGH.md for every changed source line. Local previews do not send email. No external email, Git commit/push or existing service change was performed.

## Authorized updated email send - 2026-11-16

- At the user's explicit request, ran python prototype/run_demo.py once using the bundled synthetic meal image and configured SMTP settings. The runner reported measured glucose unavailable and SMTP acceptance for the configured caregiver recipient. The message uses the enlarged chart and visible simulated current estimate. Inbox delivery has not been independently confirmed. No retry or duplicate send was made; no credentials were changed.



## Lower-angle, farther-away Chinese meal image - 2026-11-16

- User requested a lower-angle photo, then a farther viewpoint and a Chinese dish. Used the imagegen skill and built-in image editor, first lowering the viewpoint and then creating a medium-wide Chinese home-meal setting with chicken/vegetable stir-fry, separate rice bowl and chopsticks. Visually inspected both generated results; selected the final wider setting.
- Replaced samples/demo-meal.png (the runner's existing default), preserving the original overhead image as samples/demo-meal-overhead.png. Final asset: 1672 by 941 pixels, 2294563 bytes. Samples README records the prompt and provenance. No code or credentials changed.
- python prototype/run_demo.py --html-preview prototype/output/caregiver-chinese-meal.html successfully validated the replacement and generated an email preview without SMTP. Mock estimates remain unchanged. No external email sent, service changed or Git publication performed.


## Side-of-table camera with diner - 2026-11-16

- User clarified the camera should sit beside the table while a person eats, capturing table, dishes and food without their face. Used the imagegen skill and built-in editor to produce the revised synthetic scene. Visually confirmed full plate and bowl, table edge, eating gesture and no visible face. Replaced samples/demo-meal.png; prior generated variants remain in the generator output directory and the original overhead backup remains unchanged.
- Final PNG: 1672 by 941, 2369992 bytes. The file runner validated it and generated output/caregiver-table-side.html without SMTP. Samples README records the full prompt. No code, credentials or running service changed; no email sent or Git publication performed.


## Chinese version and authorized send - 2026-11-16

- User requested preparing and sending a Chinese version. Added --language en/zh-CN (English default), dedicated Simplified Chinese HTML template and chinese_email.py presentation helpers. Chinese subject, advice, plain-text fallback, dates, chart labels and Chinese-capable font preserve the existing colors, enlarged chart, separate current estimate, future forecast and simulation limitations. English remains available. No medical threshold, model, source measurement, SMTP credential or photo changed.
- Added regression tests for Chinese MIME content, measured/current/future separation, advice ordering, image bytes and every existing screening branch. Initial local preview/test exposed a Unicode strftime encoding failure and a shell-corrupted subject literal; fixed the date formatter by appending Chinese text after ASCII strftime, and wrote the subject through the patch tool. Both occurred before any SMTP send. Removed accidental duplicate fixture discovery from the new tests. Final full suite: python -m unittest -v test_chinese_email test_visual_email test_demo test_pipeline passed 35 tests. git diff --check passed.
- Generated output/caregiver-chinese.html with the latest side-of-table photo. Visually inspected output/caregiver-chinese.png: Chinese advice appears first, current estimate 140 mg/dL and range 100-190 are visible, chart labels render Chinese correctly, and the face remains outside the photo. Subsequently localized chart month/day ticks to numeric dates; regenerated HTML and reran the complete tests.
- At the user's explicit authorization, ran python prototype/run_demo.py --language zh-CN once. SMTP accepted the message for the configured caregiver recipient. Measured glucose was unavailable; the email clearly labels displayed estimates and sample history as simulated. Inbox receipt has not been independently verified. No retries or duplicate external sends were made. No service change or Git commit/push performed.
- README and CODE_WALKTHROUGH link CHINESE_EMAIL_WALKTHROUGH.md, which explains every added/replaced source line. To repeat the Chinese send use the command above; --html-preview prototype/output/caregiver-chinese.html previews without sending.


## Authorized publication preparation - 2026-11-18

- User requested pushing the completed prototype to the existing origin, Hantangduheyinglengyuezanghuahun/EMIA2020, main branch. Scope is the prototype and root README, including readable/HTML caregiver emails, larger charts, current-estimate display, Chinese version and side-of-table sample photo. Unrelated Checkpoint2 and Checkpoint3 folders remain untracked. No application code or running service changed for publication.
- Rechecked current state: all 35 tests passed with python -m unittest -v test_chinese_email test_visual_email test_demo test_pipeline. Scanned all 27 publication candidates for the configured password (compact/spaced forms), private email addresses, private-key material and common GitHub token patterns: no findings. No private SMTP configuration, CA bundle, optional patient glucose input or output previews are tracked.
- Remote main matched local c1ea94effb186e9869b8579d2b8bf633cf316570 before publication. Windows Schannel failed credential acquisition for read-only remote discovery; command-specific http.sslBackend=openssl succeeded without changing any global Git or TLS verification setting. Commit/push verification will be recorded after successful publication.

## Verified GitHub publication - 2026-11-18

- Pushed feature commit 053d999 (Add visual caregiver reports with Chinese email support) to origin/main. Independently queried the remote branch after the push and confirmed it matches the local feature commit. Publication contains only the 27 reviewed prototype/README files; all staged blobs passed the secret/private-address scan. The progress-record confirmation is committed separately. No email was sent or existing workload changed for this publication.


## Additional overhead meal view - 2026-11-18

- User requested a separate view from above of samples/demo-meal.png without replacing it. Used the imagegen skill and built-in editor to generate samples/demo-meal-top-view.png, retaining the meal, Chinese porcelain, rice bowl and diner hands, with the face outside the frame. Visually inspected the overhead result. Samples README records the complete prompt.
- Verified the new PNG signature and dimensions and confirmed the original demo-meal.png SHA-256 is unchanged (1b35f9fc2b4c37774e2f8f663f9963fd174d90e112c788b3a43b196fed3aeb00). No code, default input, service or SMTP setting changed. No email sent or Git commit/push performed.

