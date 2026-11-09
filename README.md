# EMIA 2020 meal-monitoring prototype

Receives a meal photo and optional blood glucose information, runs replaceable mock analysis, and emails a report with the original image attached. Food/glucose estimates and suggestions are simulated; no real CV or LLM service is called. This demo does not provide insulin or emergency decisions.

Requires Python 3.10 or later and no third-party packages.

## Try the sample without sending email

From the repository root:

```powershell
python prototype/run_demo.py --preview
```

The runner reads `prototype/samples/demo-meal.png` and optionally `prototype/samples/glucose.json`. Missing glucose information stays unavailable. To choose files, use `--image` and `--glucose` with local paths.

## Send a report

For a new clone, copy `prototype/.env.example` to `prototype/.env.smtp.json` and fill in your sender, recipient and SMTP app password locally. Keep that file private; do not overwrite an existing working configuration. Then run:

```powershell
python prototype/run_demo.py
```

Each invocation sends one real email and exits. Gmail requires an eligible account with an app password. Certificates are verified; local machine certificate configuration may be needed for some Python installations. Credentials, local certificate bundles, glucose files and caches are excluded from Git.

The HTTP API remains available through `prototype/server.py`. See [setup and input formats](prototype/README.md), [original code walkthrough](prototype/CODE_WALKTHROUGH.md), [automatic-runner walkthrough](prototype/DEMO_WALKTHROUGH.md) and [progress record](prototype/PROGRESS.md).

## Tests

```powershell
cd prototype
python -m unittest -v test_demo test_pipeline
```

The tests use synthetic fixtures and local/mocked SMTP transport; they send no external email.
