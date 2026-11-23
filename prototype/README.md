# EMIA 2020 meal-to-caregiver prototype

This local Python server accepts a meal image and an optional measured blood glucose reading, runs fixed computer-vision (CV), glucose-model and language-model (LLM) placeholders, and sends a real email with the original image attached. No AI API, third-party package or installation is required. Python 3.10 or later is recommended; verification used Python 3.10.11.

All food estimates, estimated current glucose and suggestions are **simulated**. The ranges are illustrative and have no validated 90% coverage. Original measurements retain their value, unit and timestamp in a separate field. Missing measurements stay null. The demo does not decide insulin timing/doses or detect emergencies, even if an input reading is concerning. Use synthetic data for demonstrations.

## Automatic demo: one command

The current-glucose model estimate now has its own prominent card (demo: **168 mg/dL**, illustrative range **135 to 190 mg/dL**) and a purple NOW marker on the glucose chart. The email maximum width is 800 px and the glucose PNG is 1200 by 720, giving a wider and taller chart with larger labels. Advice still comes first. See [updated preview](output/caregiver-large-chart.html) and [complete changed-line explanation](CHART_ESTIMATE_WALKTHROUGH.md).

The opening colour card now shows the sugar advice and medical-help advice before any readings or charts, under a compact header. If the glucose display has no supplied readings, it shows a labelled 168 mg/dL demo value plus five example timeline points (250, 240, 220, 195, 168 mg/dL). These values only fill the visual display: original missing measurements remain null and the advice still asks for a current measured reading. Supplied patient values are never replaced. See [the advice-first preview](output/caregiver-advice-first.html), [phone screenshot](output/caregiver-advice-phone.png), and [line-by-line changes](ADVICE_LAYOUT_WALKTHROUGH.md) after generating the local previews.

Emails now use [`email_template.html`](email_template.html), with a prominent colour-coded caregiver action summary, a history/latest/forecast glucose chart, the original meal image and a carbohydrate/sugar chart. Red indicates an urgent screening alert, amber indicates check/review, and teal indicates no threshold alert in a fresh supplied reading. These generic checks do not certify safety. PNG charts are embedded directly in the message using content IDs, with a readable text alternative. The photo is delivered as an inline image with its original bytes and a downloadable filename.

This visual version requires Windows PowerShell and the built-in System.Drawing library. It installs no packages. Rendering is local, with no external image host. Gmail/QQ support HTML emails and embedded images, although exact appearance depends on the client; some clients may require enabling images. The existing SMTP sender and one-command workflow use the template automatically.

To inspect the email locally without sending, run from the repository root:

```powershell
python prototype/run_demo.py --html-preview prototype/output/caregiver-preview.html
```

Open the resulting HTML file in a browser. It includes the photo and both charts. To see example history, use the explicitly synthetic fixture:

```powershell
python prototype/run_demo.py --glucose prototype/samples/glucose-history.example.json --html-preview prototype/output/caregiver-history-preview.html
```

The example fixture's `synthetic: true` flag makes its action card show demonstration-only status. Never use invented readings as patient measurements. Preview HTML may contain health information when you supply real readings; generated previews are excluded from Git under `output/`.

A glucose file can still contain one reading. It can now also contain:

```json
{
  "current": {"value": 138, "unit": "mg/dL", "measured_at": "2026-11-13T20:00:00+08:00"},
  "history": [
    {"value": 115, "unit": "mg/dL", "measured_at": "2026-11-13T19:00:00+08:00"},
    {"value": 125, "unit": "mg/dL", "measured_at": "2026-11-13T19:30:00+08:00"}
  ],
  "synthetic": true,
  "severe_symptoms": false
}
```

For actual patient readings, use actual timestamps and set `synthetic` to false. `severe_symptoms` is a caregiver/device-supplied flag for severe symptoms such as unconsciousness or breathing difficulty; this prototype does not detect symptoms. Never assume its default false means symptoms are absent. The HTTP schema accepts the same history as `glucose_history` beside `glucose`, plus these two flags. Up to 288 history entries are accepted, sorted by timestamp. A current reading must not precede the latest history entry; if only history is supplied, the latest entry becomes the current recorded reading. No history is invented or persisted between runs; supply previous readings in the file/request.

Charts convert measured mmol/L readings to mg/dL for a consistent axis, while the latest-value card retains the original unit. Display times use Hong Kong time. Dashed forecasts at +30, +60 and +120 minutes are fixed examples with illustrative ranges; they never trigger action cards. Sugar is a subset of total carbohydrates, so the food bars must not be added.

The screening rules use supplied severe symptoms or a measurement at most 15 minutes old (a conservative prototype freshness policy). Synthetic/missing/stale/future-dated readings cannot produce a reassuring card. Below 55 mg/dL triggers urgent help; below 70 triggers the prescribed low-glucose plan; at least 250 triggers care-team/ketone-plan review. Repeated supplied readings at least 300 mg/dL within two hours trigger emergency help. Above the example 180 mg/dL chart reference triggers review, whose meaning depends on personal targets and meal timing. Other fresh readings show no threshold alert, with continued monitoring. No insulin dose/timing is calculated, and severe symptoms require help regardless of readings.

The underlying guidance is [CDC low-glucose treatment](https://www.cdc.gov/diabetes/treatment/treatment-low-blood-sugar-hypoglycemia.html) and [CDC DKA emergency signs](https://www.cdc.gov/diabetes/about/diabetic-ketoacidosis.html). The 15-minute freshness limit, 180 reference and two-hour history window are prototype policies, not validated clinical decision rules. These visual/action checks require clinical review before patient deployment. See the [complete visual-email walkthrough](VISUAL_EMAIL_WALKTHROUGH.md).

From the workspace root, run:

```powershell
python prototype/run_demo.py
```

This reads `prototype/samples/demo-meal.png`, reads `prototype/samples/glucose.json` if that file exists, runs the existing mock analysis, loads your saved Gmail configuration and certificate bundle, and sends one real email to the configured QQ recipient. It then exits. No server, second terminal, API token or manual JSON request is needed. Running the command again sends another email.

To preview without sending:

```powershell
python prototype/run_demo.py --preview
```

To choose your own files (paths are relative to your terminal's working directory, or can be absolute):

```powershell
python prototype/run_demo.py --image "C:\path\to\meal.jpg" --glucose "C:\path\to\glucose.json"
```

The glucose file is optional, including when you specify a path. If absent, the measured reading stays null. An existing malformed file or invalid reading stops the run before sending. A valid file contains one reading:

```json
{
  "value": 7.2,
  "unit": "mmol/L",
  "measured_at": "2026-11-09T12:00:00+08:00"
}
```

This is a synthetic example; no glucose file is created automatically. The default patient ID is `demo-patient-001`; override with `--patient-id`. The meal timestamp defaults to the image's file modification time as a demonstration proxy. Supply the true time with `--captured-at "2026-11-09T12:00:00+08:00"` when available. All analysis remains simulated.

This processes files once per invocation; it does not watch folders or run in the background. `server.py` and `start_local.py` keep their original HTTP-server behavior. See [the automatic-demo code walkthrough](DEMO_WALKTHROUGH.md).

## Run the server

For the automatic file-based demo, use the command below instead of starting the HTTP server. The server instructions remain available afterward for hardware/network integration.

Open PowerShell in this directory. Set environment variables in this terminal; the program does not load `.env` files.

```powershell
cd prototype
$env:API_TOKEN = python -c "import secrets; print(secrets.token_urlsafe(32))"
# Keep this token locally for the client terminal. Do not commit or share it.
$env:API_TOKEN
$env:SMTP_HOST = 'smtp.your-provider.example'
$env:SMTP_PORT = '587'
$env:SMTP_MODE = 'starttls'
$env:SMTP_USER = 'your-sender@example.com'
$secret = Read-Host 'SMTP password or provider app password' -AsSecureString
$env:SMTP_PASSWORD = [System.Net.NetworkCredential]::new('', $secret).Password
$env:SMTP_FROM = 'your-sender@example.com'
$env:SMTP_TO = 'your-caregiver@example.com'
python server.py
```

Replace all example addresses and hostnames. The provider must support SMTP and authorize the sender account. Use a provider app password if required. For implicit TLS use `SMTP_MODE=ssl` and port `465`. Both modes verify TLS certificates. Set both username and password, or neither for a relay that allows unauthenticated sending. `SMTP_MODE=plain` is allowed only with `localhost`, `127.0.0.1` or `::1` for local testing.

The default API address is `http://127.0.0.1:8000`. Set `PORT` before startup to choose another port. `/health` requires no token and returns only a health status. Startup does not verify SMTP credentials; sending verifies them. Press Ctrl+C to stop. Clear `$env:SMTP_PASSWORD` after use with `Remove-Item Env:SMTP_PASSWORD`.

## Submit a meal

The bundled `samples/demo-meal.png` is an AI-generated demonstration photo of rice, chicken, broccoli and carrots, not a patient record or dietary recommendation. The example below uses it. Replace `$imagePath` to use another photo. Starting the server does not submit a photo automatically. See [sample provenance and generation prompt](samples/README.md).

In a second PowerShell terminal, use the same API token from the server terminal and a local PNG/JPEG meal photo. The hardware team can use the same JSON schema. No image is fetched from a URL.

```powershell
$env:API_TOKEN = Read-Host 'API token from the server terminal'
$headers = @{ Authorization = "Bearer $env:API_TOKEN" }
$imagePath = 'samples\demo-meal.png'
$event = @{
    patient_id = 'demo-patient-001'
    meal_captured_at = '2026-11-09T12:00:00+08:00'
    image = @{
        content_base64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($imagePath))
    }
    glucose = @{
        value = 7.2
        unit = 'mmol/L'
        measured_at = '2026-11-09T11:55:00+08:00'
    }
}
$body = $event | ConvertTo-Json -Depth 5

# Inspect the result without email; SMTP configuration is optional for preview.
$preview = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/preview' -Method Post -Headers $headers -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($body))
$preview | ConvertTo-Json -Depth 10

# This request sends a real email to SMTP_TO.
$sent = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/events' -Method Post -Headers $headers -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($body))
$sent.email_status
```

Use the actual capture/measurement times; the dates above are examples. Timestamps must include a timezone (`Z` or an offset). `patient_id` is a nonempty string of at most 100 characters. `image.content_base64` is plain base64, without a data-URL prefix. Maximum decoded image size is 5 MiB; maximum JSON body size is 7 MiB. PNG/JPEG signatures are checked, without full image decoding. The attachment gets the safe server-assigned name `meal.png` or `meal.jpeg`.

Glucose is optional: omit `glucose` or set it to null. If supplied, include all three fields: a finite positive numeric `value`, `unit` equal to `mg/dL` or `mmol/L`, and `measured_at`. Values are retained in their original unit and are not converted or clinically interpreted. Extra JSON fields are ignored, so send only this documented schema. Recipient addresses are configured on the server, never chosen by an incoming request.

## What comes back and what is emailed

`report.original_information` contains the patient identifier, meal time and original glucose information. `food` contains separate sugar and total carbohydrate estimates in grams. `estimated_current_glucose` is always the same synthetic 140 mg/dL example, with an illustrative range of 100–190 mg/dL, regardless of the meal or measured reading. This is deliberately a placeholder, not a patient model. Sugar is fixed at 12 g (6–20 g); carbohydrates at 60 g (40–85 g).

`uncertainty.intended_coverage` records the future target of 0.90, while `validated=false` and `confidence_level=null` explicitly deny a statistical confidence claim. `suggestions` is a template using the patient identifier and whether a measurement was supplied. It performs no actual personalized medical reasoning. The email is a readable plain-text report with patient and meal details, the original glucose reading (or an explicit missing-reading message), separately labelled simulated food/current-glucose estimates, illustrative ranges, caregiver notes and demo limitations. Dates are displayed with their UTC offset. The original meal image remains attached. Internal API responses and terminal previews remain JSON. See [a synthetic example email](samples/demo-email.txt) and [the formatting code walkthrough](EMAIL_WALKTHROUGH.md).

| Result | Meaning |
| --- | --- |
| HTTP 200, `not_sent_preview` | Analysis preview only; no email attempted. |
| HTTP 200, `accepted_by_smtp` | SMTP server accepted the message; inbox delivery is not guaranteed. |
| HTTP 400 | Invalid JSON/schema/image/measurement/timestamp. |
| HTTP 401 | Incorrect or missing Bearer token. |
| HTTP 404 | Unknown path. |
| HTTP 408 | Request body read timeout/failure. |
| HTTP 413 | Body length missing, zero, negative or over limit. |
| HTTP 415 | Content type must be `application/json`. |
| HTTP 502, `failed_or_unconfirmed` | SMTP configuration/connection/authentication/delivery failed or final acceptance is uncertain. Report is returned, but success is not claimed. |

There is no queue, persistence, delivery retry or duplicate suppression. Repeating `/events` can send another email. A connection failure after SMTP acceptance can produce an uncertain result; inspect the provider's status before retrying. Patient events and images are held in memory during processing and are not written to files by the application. Email providers and mailboxes will retain transmitted data according to their own settings. Avoid sharing saved reports, photos or credentials in version control.

## Replace the placeholders later

In `server.py`, replace `mock_food_analysis(image_bytes)` with a CV implementation, `mock_glucose_analysis(event, food)` with a validated predictive model, and `mock_llm_analysis(event, food, glucose)` with an LLM integration. Keep measured and predicted information separate. Only a calibrated, evaluated model can justify a 90% interval. Any clinical escalation or insulin feature needs a separately designed and validated clinical workflow.

The API binds to loopback, so a separate physical pet cannot contact it directly. This prototype establishes the payload contract. Hardware access later needs an explicitly configured network endpoint with HTTPS, authentication, access controls and suitable handling of patient data. The built-in HTTP server is for local demonstration, with sequential request processing; it is not a production service. Video/audio ingestion is outside this prototype; the hardware supplies a selected still image and optional reading.

## Verify

```powershell
python -m unittest -v test_pipeline
```

Tests use temporary loopback HTTP and SMTP servers, with in-memory test data only. They verify the actual HTTP-to-SMTP path, image attachment integrity, original measurement preservation, demo labels, optional glucose, invalid input, authentication, body limits and SMTP rejection/configuration failure. STARTTLS/login calls are checked with a mock; the automated tests contact no external provider. A separate user-authorized demonstration send successfully authenticated to Gmail over verified STARTTLS and was accepted for the configured QQ recipient. Final inbox delivery has not been independently confirmed.

## TLS certificates for this Python installation

The installed MSYS2 Python initially had no trusted certificates. For the successful demonstration send, existing Windows trusted root certificates were copied to the ignored `.env.smtp-ca.pem`; certificate verification stayed enabled. No certificates were installed and no system settings were changed. To use this same bundle for a future launch, run from `prototype`:

```powershell
$env:SSL_CERT_FILE = (Resolve-Path -LiteralPath '.env.smtp-ca.pem').Path
python start_local.py
```

The first command selects the local CA bundle for this terminal's child Python processes; the second starts the existing launcher. This bundle is a snapshot of Windows trust at export time and may need refreshing if that trust changes. The launcher does not select it automatically. Do not disable TLS certificate verification to work around certificate errors.

See [PROGRESS.md](PROGRESS.md) for the verification record and [CODE_WALKTHROUGH.md](CODE_WALKTHROUGH.md) for the complete line-by-line explanation. No previous code or behavior was removed.


## Chinese email

Use `python prototype/run_demo.py --language zh-CN` to send one Simplified Chinese email using the same configured SMTP recipient and current default meal photo. To preview without sending: `python prototype/run_demo.py --language zh-CN --html-preview prototype/output/caregiver-chinese.html`. The Chinese subject, text fallback, HTML and charts retain all simulation labels. English remains the default (`--language en`). See [complete changed-line explanation](CHINESE_EMAIL_WALKTHROUGH.md).


## GlyCat reference design (23 November 2026)

The HTML email now uses the supplied GlyCat logo and a blue meal-summary card with the meal photo, a prominent current estimate and yellow illustrative status badge. The card sits below the caregiver advice and directly above the glucose chart. English and Chinese templates share this structure; the photo appears only once. The newest demo estimate is 168 mg/dL, with illustrative range 135-190 mg/dL. The status badge is the reference design's fixed demo label, not a clinical classification or an input to alerts.

The runner's default meal is now `samples/86bf78fb-207b-4f61-9428-e7dba996d03d.JPG`. Existing generated meal alternatives are preserved and remain selectable through `--image`. The logo uses the original JPEG bytes from `samples/8c067082-8ffa-479f-9531-aeddc01b81f8.JPG`; it is embedded in the email with a content ID, together with the meal photo and generated PNG charts. Reference layout images `907644a2-4f51-4dbb-8cc0-9c27a9f91279.JPG` and `b6829823-c955-493b-acfe-3df7ff7846da.JPG` guide the chart/card design; they are not patient measurements or screenshots attached in place of live output.

When no readings are supplied, the display-only example series is 250, 240, 220, 195 and the current model estimate, anchored to report generation time. The unlabelled intermediate values in the reference are represented by 220 and 195 for this demonstration. Original missing readings remain null; actual supplied readings are preserved. Shaded ranges are unvalidated illustrative ranges, not statistically validated confidence intervals.

Preview commands:

```powershell
python prototype/run_demo.py --html-preview prototype/output/glycat-reference-en.html
python prototype/run_demo.py --language zh-CN --html-preview prototype/output/glycat-reference-zh.html
```

For a one-time recipient change, append `--recipient caregiver@example.test` to the send command with the actual authorized address. It changes this process's SMTP_TO after loading settings and does not rewrite the private SMTP JSON. The normal address checks still run before SMTP connection. Omitting this option uses the saved caregiver address.

See [GlyCat source walkthrough](GLYCAT_EMAIL_WALKTHROUGH.md) for every changed code line and [the current project status](../PROJECT_STATUS.md). Earlier design walkthroughs describe their historical versions.
