# EMIA 2020 meal-to-caregiver prototype

This local Python server accepts a meal image and an optional measured blood glucose reading, runs fixed computer-vision (CV), glucose-model and language-model (LLM) placeholders, and sends a real email with the original image attached. No AI API, third-party package or installation is required. Python 3.10 or later is recommended; verification used Python 3.10.11.

All food estimates, estimated current glucose and suggestions are **simulated**. The ranges are illustrative and have no validated 90% coverage. Original measurements retain their value, unit and timestamp in a separate field. Missing measurements stay null. The demo does not decide insulin timing/doses or detect emergencies, even if an input reading is concerning. Use synthetic data for demonstrations.

## Automatic demo: one command

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

`uncertainty.intended_coverage` records the future target of 0.90, while `validated=false` and `confidence_level=null` explicitly deny a statistical confidence claim. `suggestions` is a template using the patient identifier and whether a measurement was supplied. It performs no actual personalized medical reasoning. The email contains the warning, full report as readable JSON, and original meal image as an attachment.

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
