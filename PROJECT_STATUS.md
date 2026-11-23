# EMIA2020 project status

This is the current progress record, following the user's updated instructions. Earlier work and verification remain in [prototype/PROGRESS.md](prototype/PROGRESS.md); that historical log is preserved.

## Completed — 23 November 2026: GlyCat email design

- Read and visually inspected all four supplied JPEGs. Embedded the original GlyCat logo (`8c067082-8ffa-479f-9531-aeddc01b81f8.JPG`) and selected the supplied meal (`86bf78fb-207b-4f61-9428-e7dba996d03d.JPG`) as the file runner's new default. Earlier meal assets remain available through `--image`.
- Recreated the summary-card reference (`b6829823-c955-493b-acfe-3df7ff7846da.JPG`) as dynamic HTML: pale blue background, red heading, orange photo border, large current estimate and yellow status badge. Advice precedes the summary, which directly precedes the glucose chart. The separate latest-reading/future cards remain below the chart. The meal photo appears once. English and Chinese templates are supported.
- Recreated the history/forecast reference (`907644a2-4f51-4dbb-8cc0-9c27a9f91279.JPG`) using generated PNG charts. New fixed demo current estimate: 168 mg/dL, illustrative range 135–190. Display-only missing-data history: 250, 240, 220, 195, 168; the unlabelled intermediate values 220/195 are a demonstration interpretation. Actual supplied measurements are preserved, missing original values remain null, and no demo values or status badges drive clinical screening. The “Slightly High” badge is fixed illustrative display metadata; shaded ranges are unvalidated, not statistical confidence intervals.
- Added `--recipient` for one-time delivery without rewriting private SMTP configuration. Existing address validation still runs before connection. No credentials or global environment settings changed.
- Complete line-by-line explanation: [prototype/GLYCAT_EMAIL_WALKTHROUGH.md](prototype/GLYCAT_EMAIL_WALKTHROUGH.md). Usage and design decisions are in the prototype README.

## Verification

- Final run: `python -m unittest -v test_chinese_email test_visual_email test_demo test_pipeline` passed **37 tests**. New tests verify summary placement, byte-identical embedded logo/photo, no repeated photo, demo-history/source-data separation and one-time recipient override. Tests use local or mocked SMTP only.
- Preserved failure evidence: an initial assertion still expected 140 mg/dL and was updated to the requested 168 demo. A subsequent complete run encountered a Windows `ConnectionAbortedError` (10053) in the unchanged HTTP request-size rejection test. The final full rerun passed, including that test; no HTTP behavior was changed to hide the failure.
- Generated self-contained previews: `prototype/output/glycat-reference-en.html` and `prototype/output/glycat-reference-zh.html`.
- Isolated headless Chrome checks at 1100px and 390px for both languages confirmed all four images loaded and no horizontal overflow. Screenshots: `prototype/output/glycat-reference-{en,zh}-{1100,390}.png`. Visually inspected English desktop/phone and Chinese desktop screenshots. Temporary browser profile removed; no existing user browser or server was changed.
- `git diff --check` passed. No commit or push performed for this update.

## Completed — authorized email send

Sent one updated English email (matching the English reference) using `python prototype/run_demo.py --recipient <requested-address>`. The runner exited successfully and reported SMTP acceptance for the exact recipient specified by the user. Inbox delivery has not been independently confirmed. No retry or duplicate send was made. The supplied meal was used, measured glucose was unavailable and all estimates/history examples were labelled simulated. The saved caregiver address was not changed. Chinese remains available with `--language zh-CN`.

No remaining implementation or send steps are pending for the email request. Publication was subsequently authorized as recorded below.

## Authorized publication — 23 November 2026

- User requested pushing the current work to the existing EMIA2020 repository, `origin/main`.
- Reviewed all 22 changed/new publication candidates under `prototype/` plus this status file. Checked for configured password forms, private sender/recipient addresses, the one-time delivery address, private-key markers and common GitHub token patterns: no findings. No private SMTP configuration, CA bundle, optional patient input or preview output is tracked.
- Remote and local `main` both matched `ef12a35c8d8d775ba92f3776304c6bbd635c39ab` before publication. `git diff --check` passed. The immediately preceding final 37-test run remains applicable; no application source changed afterward.
- Publication scope includes the GlyCat design, original supplied image assets, separate overhead alternative, tests and documentation. Unrelated checkpoint directories remain untracked. Commit/push verification will be recorded after completion.
