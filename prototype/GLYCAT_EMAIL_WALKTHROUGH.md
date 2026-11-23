# GlyCat email reference design: changed-line walkthrough

This update implements the four supplied image roles in both email languages. The logo JPEG is embedded unchanged; the meal JPEG becomes the file runner default. The two layout screenshots are design references: generated chart values, timestamps and summary fields remain data-driven. No screenshot replaces the live chart. Missing measurements remain null and supplied measurements remain unchanged.

The supplied design changes the fixed demo current estimate from 140 to 168 mg/dL and its illustrative range from 100-190 to 135-190. The display-only missing-data series now descends through 250, 240, 220, 195 and the current estimate; 220/195 represent unlabelled intermediate points in the reference. The yellow Slightly High badge is fixed demo display metadata, not a computed clinical classification. Neither it nor these example numbers affect the existing measured-data screening rules.

Removed/repositioned behavior: the old purple-only estimate card is replaced by the blue meal-summary card immediately below advice and above the chart. The standalone duplicated meal photo is removed, as the photo is now in the summary. Existing latest-reading/future cards are retained below the chart. English/Chinese alternatives and prior meal assets remain available. The new --recipient option changes the current send process only and still uses existing address validation.

Every added/replaced nonblank source line relative to the pre-change source snapshot is explained below. Blank lines only separate code.

## visual_email.py

| Line | Source | Explanation |
| --- | --- | --- |
| 17 | `LOGO = ROOT / "samples" / "8c067082-8ffa-479f-9531-aeddc01b81f8.JPG"` | Resolve the supplied logo JPEG relative to this module, so composing mail works independently of the terminal working directory. |
| 34 | `for minutes, value in ((-120, 250), (-90, 240), (-60, 220), (-30, 195),` | Replace the empty-display example history with the descending reference sequence, anchored at -120, -90, -60 and -30 minutes. |
| 35 | `(0, report["estimated_current_glucose"]["estimate"]))], True` | Use the current report estimate at generation time as the final explicitly simulated display point; this does not create a source measurement. |
| 54 | `"max_y": math.ceil(max([p["y"] for p in points] + [p["high"] for p in forecast] + report["estimated_current_glucose"]["illustrative_range"] + [240])/20)*20,` | Round the vertical ceiling up to a multiple of 20 mg/dL, keeping the 250 example point and all estimate bounds visible while supporting 60-unit tick spacing. |
| 104 | `estimated_range=f"{estimate['illustrative_range'][0]:g} to {estimate['illustrative_range'][1]:g} {estimate['unit']}",` | Keep the report-derived lower and upper bounds with units on the new card; the comma allows the additional summary entries. |
| 105 | `summary_status="Slightly High" if estimate.get("display_status") == "slightly_high" else "Simulation only",` | Map the model display_status metadata to the screenshot badge text; an absent status displays Simulation only rather than inventing a clinical category. |
| 106 | `logo_image="cid:glycat-logo")` | Provide an embedded logo source by default for MIME HTML; local preview sources can override it with a self-contained data URL. |
| 125 | `"""Report/image/addresses -> MIME email with charts, supplied meal bytes and local GlyCat logo."""` | Document the MIME builder inputs/output and the addition of the local logo alongside charts and original meal bytes. |
| 139 | `part.add_related(LOGO.read_bytes(), maintype="image", subtype="jpeg", cid="<glycat-logo>", filename="glycat-logo.jpg", disposition="inline")` | Read and embed the unchanged logo JPEG bytes under the glycat-logo content ID with an inline filename, creating the fourth embedded image. |
| 148 | `sources["logo_image"] = "data:image/jpeg;base64," + base64.b64encode(LOGO.read_bytes()).decode("ascii")` | Read and base64-encode the logo into the explicit local preview, so no remote image request or unresolved CID is needed. |

## email_template.html

| Line | Source | Explanation |
| --- | --- | --- |
| 4 | `<style>@media screen and (max-width:600px){.summary-cell{display:block!important;width:auto!important}.summary-number{font-size:38px!important}.summary-title{font-size:25px!important}}</style>` | Stack summary photo and number on narrow screens and reduce large typography; table cells remain side by side in desktop email clients. |
| 7 | `<tr><td style="padding:12px 28px;background:#111111;color:#FFFFFF;border-radius:14px 14px 0 0">` | Use a black header to fit the supplied logo without altering its pixels. |
| 8 | `<table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr><td width="160"><img src="$logo_image" alt="GlyCat — See what matters. Control what doesn't." width="150" style="display:block;width:150px;max-width:100%;height:auto"></td><td style="padding-left:16px"><p style="margin:0;font-size:23px;font-weight:bold">GlyCat</p><p style="margin:6px 0;font-size:12px;color:#D7E3EE">PROTOTYPE · $patient</p><p style="margin:0;font-size:11px;color:#D7E3EE">Prepared $prepared</p></td></tr></table></td></tr>` | Display the supplied GlyCat logo beside compact branding, patient ID and prepared timestamp using an inline email-safe table. |
| 18 | `<tr><td style="padding:4px 16px 24px"><table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#C4DCFC;border-radius:22px"><tr><td colspan="2" style="padding:24px 22px 16px"><h2 class="summary-title" style="margin:0;font-family:'Trebuchet MS',Arial,sans-serif;font-size:34px;font-weight:900;letter-spacing:1px;color:#920000">GLYCAT MEAL SUMMARY</h2></td></tr>` | Open the rounded pale-blue summary card and show the large red GlyCat meal-summary heading from the reference. |
| 19 | `<tr><td class="summary-cell" width="49%" valign="middle" style="padding:10px 14px 20px 22px"><img src="$meal_image" alt="Original supplied meal photograph" width="330" style="display:block;box-sizing:border-box;width:100%;height:auto;border:5px solid #DD7046"></td>` | Show the full supplied meal photo inside the summary with the orange border from the reference, preserving aspect ratio. |
| 20 | `<td class="summary-cell" width="51%" valign="middle" style="padding:10px 22px 20px 14px"><p style="margin:0 0 12px;font-size:12px;font-weight:bold">ESTIMATED CURRENT GLUCOSE (SIMULATED)</p><p style="margin:0;font-size:28px;font-weight:900;color:#000000">Glucose (est.):</p><p class="summary-number" style="margin:12px 0 20px;font-size:48px;font-weight:900;color:#000000">$estimated_current</p>` | Show a separate simulated-estimate label and the report-derived current glucose value in large black type beside the photo. |
| 21 | `<p style="margin:0;padding:16px 10px;background:#FFEB9C;border-radius:22px;font-size:30px;font-weight:900;text-align:center;color:#000000">$summary_status</p><p style="margin:10px 0 0;font-size:12px;line-height:1.6">Illustrative status label only; not a clinical classification.</p></td></tr>` | Render the yellow rounded demo badge and state that the text is illustrative rather than a clinical classification. |
| 22 | `<tr><td colspan="2" style="padding:0 22px 22px"><p style="margin:0;font-size:12px;line-height:1.7">Illustrative range: $estimated_range. Fixed demo estimate, not a measured reading or validated prediction.<br>Meal time: $meal_time · $food_source</p></td></tr></table></td></tr>` | Show the report-derived illustrative range and meal timestamp below the card, retaining simulation and image-analysis limitations. |
| 23 | `<tr><td style="padding:0 12px 22px"><h2 style="margin:0 0 8px;font-size:21px">Glucose: previous, latest and future</h2>` | Retain the email-safe table wrappers needed to position the latest/future cards below the chart and keep the remaining food-analysis section intact. |
| 24 | `<p style="font-size:13px;line-height:1.6;color:#64748B">$history_note. All chart values use mg/dL; times use Hong Kong time (UTC+08:00).</p>` | Retain the email-safe table wrappers needed to position the latest/future cards below the chart and keep the remaining food-analysis section intact. |
| 25 | `<img src="$glucose_image" alt="Glucose history, current simulated estimate and dashed future forecast, with illustrative ranges." width="776" style="display:block;width:100%;height:auto;border:1px solid #E2E8F0">` | Retain the email-safe table wrappers needed to position the latest/future cards below the chart and keep the remaining food-analysis section intact. |
| 26 | `<p style="font-size:12px;color:#64748B;line-height:1.6">The purple NOW marker is the estimated current glucose. The dashed forecast and shaded range are fixed demo values. They do not drive alerts. Horizontal 70/180 reference lines are illustrative; individual targets vary. When no readings are supplied, labelled DEMO values fill this display and are excluded from advice.</p>` | Retain the email-safe table wrappers needed to position the latest/future cards below the chart and keep the remaining food-analysis section intact. |
| 27 | `<p style="font-size:13px;line-height:1.6">$history_values</p></td></tr>` | Retain the email-safe table wrappers needed to position the latest/future cards below the chart and keep the remaining food-analysis section intact. |

## email_template_zh.html

| Line | Source | Explanation |
| --- | --- | --- |
| 4 | `<style>@media screen and (max-width:600px){.summary-cell{display:block!important;width:auto!important}.summary-number{font-size:38px!important}.summary-title{font-size:25px!important}}</style>` | Stack summary photo and number on narrow screens and reduce large typography; table cells remain side by side in desktop email clients. |
| 7 | `<tr><td style="padding:12px 28px;background:#111111;color:white"><table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr><td width="160"><img src="$logo_image" alt="GlyCat 品牌标志" width="150" style="display:block;width:150px;max-width:100%;height:auto"></td><td style="padding-left:16px"><p style="margin:0;font-size:23px;font-weight:bold">GlyCat</p><p style="margin:6px 0;font-size:12px">原型演示 · $patient</p><p style="margin:0;font-size:11px">生成时间：$prepared</p></td></tr></table></td></tr>` | Display the supplied GlyCat logo beside compact branding, patient ID and prepared timestamp using an inline email-safe table. |
| 16 | `<tr><td style="padding:4px 16px 24px"><table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#C4DCFC;border-radius:22px"><tr><td colspan="2" style="padding:24px 22px 16px"><h2 class="summary-title" style="margin:0;font-size:34px;font-weight:900;letter-spacing:1px;color:#920000">GLYCAT 用餐摘要</h2></td></tr>` | Open the rounded pale-blue summary card and show the large red GlyCat meal-summary heading from the reference. |
| 17 | `<tr><td class="summary-cell" width="49%" valign="middle" style="padding:10px 14px 20px 22px"><img src="$meal_image" alt="提供的用餐照片" width="330" style="display:block;box-sizing:border-box;width:100%;height:auto;border:5px solid #DD7046"></td>` | Show the full supplied meal photo inside the summary with the orange border from the reference, preserving aspect ratio. |
| 18 | `<td class="summary-cell" width="51%" valign="middle" style="padding:10px 22px 20px 14px"><p style="margin:0 0 12px;font-size:12px;font-weight:bold">当前血糖估算（模拟）</p><p style="margin:0;font-size:28px;font-weight:900;color:#000000">血糖估算：</p><p class="summary-number" style="margin:12px 0 20px;font-size:48px;font-weight:900;color:#000000">$estimated_current</p>` | Show a separate simulated-estimate label and the report-derived current glucose value in large black type beside the photo. |
| 19 | `<p style="margin:0;padding:16px 10px;background:#FFEB9C;border-radius:22px;font-size:30px;font-weight:900;text-align:center;color:#000000">$summary_status</p><p style="margin:10px 0 0;font-size:12px;line-height:1.7">仅为演示状态标签，并非临床判断。</p></td></tr>` | Render the yellow rounded demo badge and state that the text is illustrative rather than a clinical classification. |
| 20 | `<tr><td colspan="2" style="padding:0 22px 22px"><p style="margin:0;font-size:12px;line-height:1.7">演示范围：$estimated_range。固定演示估算，并非实测值或经过验证的预测。<br>用餐记录时间：$meal_time · $food_source</p></td></tr></table></td></tr>` | Show the report-derived illustrative range and meal timestamp below the card, retaining simulation and image-analysis limitations. |
| 26 | `<tr><td style="padding:4px 28px 20px"><table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr>` | Retain the email-safe table wrappers needed to position the latest/future cards below the chart and keep the remaining food-analysis section intact. |
| 27 | `<td width="50%" valign="top" style="padding:16px;background:#F3F7FB"><p style="margin:0;font-size:12px">$current_label</p><p style="margin:10px 0;font-size:30px;font-weight:bold">$current</p><p style="margin:0;font-size:12px;line-height:1.7">$measured_at<br>$freshness</p></td>` | Retain the latest recorded or clearly labelled demo value card below the chart, with original units, timestamp and freshness. |
| 28 | `<td width="50%" valign="top" style="padding:16px;background:#F4EFFF"><p style="margin:0;font-size:12px;color:#7050A5">30 分钟后预测（模拟）</p><p style="margin:10px 0;font-size:30px;font-weight:bold;color:#7050A5">$forecast_value</p><p style="margin:0;font-size:12px;line-height:1.7">演示范围：$forecast_range mg/dL<br>固定示例，未经验证</p></td>` | Retain the distinct +30-minute simulated future card and its report-derived range below the chart. |
| 29 | `</tr></table></td></tr>` | Retain the email-safe table wrappers needed to position the latest/future cards below the chart and keep the remaining food-analysis section intact. |

## server.py

| Line | Source | Explanation |
| --- | --- | --- |
| 115 | `return {"source": "fixed_demo_stub", "estimate": 168, "unit": "mg/dL",` | Set the fixed prototype estimate to the reference value 168 mg/dL; no real model or image analysis is introduced. |
| 116 | `"illustrative_range": [135, 190], "uses_measured_glucose": False,` | Set the fixed illustrative range to 135-190 mg/dL and preserve the flag that the mock ignores supplied measurements. |
| 117 | `"display_status": "slightly_high"}` | Add slightly_high as the screenshot status metadata for presentation only; measured-data screening never reads this field. |

## run_demo.py

| Line | Source | Explanation |
| --- | --- | --- |
| 62 | `parser.add_argument("--image", type=Path, default=ROOT / "samples" / "86bf78fb-207b-4f61-9428-e7dba996d03d.JPG")` | Select the supplied meal JPEG as the automatic demo default. The existing --image option still selects all older or custom images. |
| 69 | `parser.add_argument("--recipient", help="Override the recipient for this send only; private SMTP settings are unchanged.")` | Add an explicit one-time recipient option; omitting it preserves the address loaded from private configuration. |
| 87 | `if args.recipient:` | Apply the recipient override only for an actual send after local mail settings are loaded; preview paths return before this block. |
| 88 | `os.environ["SMTP_TO"] = args.recipient` | Set SMTP_TO in the current process without rewriting the JSON file; server.send_email still validates the address before any SMTP connection. |

## chart_renderer.ps1

| Line | Source | Explanation |
| --- | --- | --- |
| 45 | `for ($value = 0; $value -le $maxY; $value += 60) {` | Place y-axis ticks at 0, 60, 120, 180 and 240 mg/dL (and higher multiples when needed), matching the reference scale. |
| 72 | `if ($point.x -ne $payload.now -or $point.y -ne $payload.current_estimate.y) {` | Suppress a duplicate last-reading label when the displayed demo endpoint exactly matches the estimate at NOW. |
| 73 | `Text ([string]$point.y) ([math]::Min(1040, (Px $point.x)+8)) ([math]::Max(65, (Py $point.y)-32)) 24 '#245FE8'` | Preserve the numeric label for a distinct last supplied reading rather than hiding it behind the model estimate. |
| 74 | `}` | Close the duplicate-label guard; drawing continues with the unchanged historical series and future forecast. |
| 75 | `Text ([string]$points[0].y) ((Px $points[0].x)+8) ([math]::Max(65, (Py $points[0].y)-32)) 26 '#167D8D'` | Label the first history value, exposing the reference starting value of 250; clamp the label above the plotting line. |
| 88 | `Text ([string]$estimate.y) ($estimateX+14) ((Py $estimate.y)-28) 30 '#8055CF'` | Label the purple current-estimate marker explicitly to the right, matching the reference NOW value. |

## chinese_email.py

| Line | Source | Explanation |
| --- | --- | --- |
| 58 | `result["summary_status"] = "略高" if report["estimated_current_glucose"].get("display_status") == "slightly_high" else "仅供模拟演示"` | Translate the new demo badge metadata to Chinese while retaining a neutral simulation-only fallback and leaving source records unchanged. |

## test_visual_email.py

| Line | Source | Explanation |
| --- | --- | --- |
| 100 | `self.assertIn("168 mg/dL", html)` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 106 | `self.assertLess(html.index("Sugar: more or less?"), html.index("168 mg/dL"))` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 107 | `self.assertLess(html.index("Medical help"), html.index("168 mg/dL"))` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 132 | `def test_glycat_reference_layout_and_embedded_logo(self):` | Document a regression for the logo, summary placement, exact photo bytes, reference history and separation from patient measurements. |
| 133 | `"""Check image roles, summary placement and demo-only history against the new references."""` | Document a regression for the logo, summary placement, exact photo bytes, reference history and separation from patient measurements. |
| 134 | `event = self.event()` | Prepare the missing-reading demo fixture and generated HTML for the new layout regression; no real patient data or email transport is used. |
| 135 | `event["glucose"] = None` | Prepare the missing-reading demo fixture and generated HTML for the new layout regression; no real patient data or email transport is used. |
| 136 | `report = server.analyze(event, PNG)` | Prepare the missing-reading demo fixture and generated HTML for the new layout regression; no real patient data or email transport is used. |
| 137 | `before = copy.deepcopy(report)` | Copy the report before rendering so the test can prove the presentation does not mutate measurements or screening. |
| 138 | `message = visual_email.compose_email(report, PNG, "png", "sender@example.test", "caregiver@example.test")` | Build the real MIME structure using test addresses and a test photo, exercising embedded logo and chart creation without SMTP. |
| 139 | `html = message.get_body(preferencelist=("html",)).get_content()` | Prepare the missing-reading demo fixture and generated HTML for the new layout regression; no real patient data or email transport is used. |
| 140 | `self.assertLess(html.index("Medical help"), html.index("GLYCAT MEAL SUMMARY"))` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 141 | `self.assertLess(html.index("GLYCAT MEAL SUMMARY"), html.index("Glucose: previous, latest and future"))` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 142 | `self.assertIn("Slightly High", html)` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 143 | `self.assertIn("not a clinical classification", html)` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 144 | `self.assertEqual(html.count('src="cid:meal-photo"'), 1)` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 145 | `self.assertIn('src="cid:glycat-logo"', html)` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 146 | `images = {part.get("Content-ID"): part.get_payload(decode=True) for part in message.walk() if part.get_content_maintype() == "image"}` | Index embedded image bytes by their content IDs for exact logo/photo byte comparison. |
| 147 | `self.assertEqual(images["<glycat-logo>"], visual_email.LOGO.read_bytes())` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 148 | `self.assertEqual(images["<meal-photo>"], PNG)` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 149 | `self.assertEqual([p["y"] for p in visual_email.chart_data(report)["measured"]], [250, 240, 220, 195, 168])` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 150 | `self.assertEqual(report, before)` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 151 | `self.assertIsNone(report["original_information"]["glucose"])` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 152 | `self.assertEqual(report["caregiver_action"]["level"], "review")` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |

## test_chinese_email.py

| Line | Source | Explanation |
| --- | --- | --- |
| 26 | `self.assertIn("168 mg/dL", body)` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 30 | `self.assertLess(html.index("是否需要就医"), html.index("168 mg/dL"))` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 36 | `self.assertEqual(len(images), 4)` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |

## test_demo.py

| Line | Source | Explanation |
| --- | --- | --- |
| 53 | `def test_one_time_recipient_override_does_not_write_configuration(self):` | Document a regression proving a one-time recipient override selects the requested address without writing configuration. |
| 54 | `"""Override delivery in process only; retain the default recipient on the next configured run."""` | Document a regression proving a one-time recipient override selects the requested address without writing configuration. |
| 55 | `with patch.object(run_demo, "load_mail_settings"), patch.object(run_demo.server, "send_email") as send, patch.dict(os.environ, {"SMTP_TO": "original@example.test"}), contextlib.redirect_stdout(io.StringIO()):` | Mock SMTP configuration and delivery, isolating this recipient test from real external mail while preserving the environment outside the test. |
| 56 | `self.assertEqual(run_demo.main(self.args + ["--recipient", "requested@example.test"]), 0)` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 57 | `self.assertEqual(os.environ["SMTP_TO"], "requested@example.test")` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 58 | `send.assert_called_once()` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 59 | `self.assertFalse((self.root / ".env.smtp.json").exists())` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |

## test_pipeline.py

| Line | Source | Explanation |
| --- | --- | --- |
| 100 | `self.assertEqual(report["estimated_current_glucose"]["estimate"], 168)` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
| 190 | `self.assertIn("Estimated glucose: 168 mg/dL", body)` | Verify this required output, source-data invariant, ordering or send-count expectation; reference values change from the former 140/138 demo to 168 and the logo adds a fourth image. |
