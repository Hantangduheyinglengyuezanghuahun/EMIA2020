# Advice-first layout and complete numeric display

This update moves advice above readings and fills an empty visual display with explicitly labelled example numbers. It preserves every supplied measurement and leaves original missing measurements null. Demo display numbers never enter caregiver_summary, original_information or the action calculation. Blank lines only separate code. Every added/replaced nonblank source line relative to the preceding visual-email walkthrough appears below.

Removed behaviour: the tall branding header and lower duplicate advice block are replaced by a compact header and an opening advice card. The visual missing-value text and empty chart are replaced by labelled numeric examples. Actual source-data absence remains visible in the report and text alternative. The previous fixed measured-series legend is replaced by a source-aware label.

## visual_email.py

| Line | Source | Explanation |
| --- | --- | --- |
| 19 | `def display_readings(report):` | Define display_readings: Return (display readings, example flag); fill an empty display with labelled demo values. |
| 20 | `"""Return (display readings, example flag); fill an empty display with labelled demo values.` | Document that the display helper returns readings and a demo flag, preserves the original report and cannot create clinical input. |
| 22 | `This never mutates original_information or caregiver_action. Synthetic display` | Document that the display helper returns readings and a demo flag, preserves the original report and cannot create clinical input. |
| 23 | `values cannot become clinical input, a measured reading or a reassuring alert.` | Document that the display helper returns readings and a demo flag, preserves the original report and cannot create clinical input. |
| 24 | `"""` | Document that the display helper returns readings and a demo flag, preserves the original report and cannot create clinical input. |
| 29 | `if readings:` | Use supplied readings whenever any exist; the numeric fill is restricted to a wholly empty display. |
| 30 | `return readings, original.get("synthetic", False)` | Return supplied values unchanged, carrying their existing synthetic flag for accurate labelling. |
| 31 | `now = as_time(report["caregiver_action"]["generated_at"])` | Anchor display-only example times to report generation, keeping them aligned with the future demo chart. |
| 32 | `return [{"value": value, "unit": "mg/dL", "measured_at": (now + timedelta(minutes=minutes)).isoformat()}` | Build the display-only dictionaries with numeric mg/dL values and timezone-qualified timestamps; none is added to original measurements or action input. |
| 33 | `for minutes, value in ((-120, 108), (-90, 116), (-60, 128), (-30, 145), (0, 138))], True` | Provide exactly five display-only pairs: -120/108, -90/116, -60/128, -30/145 and 0/138 minutes/mg-dL, and mark the sequence as an example. |
| 36 | `def chart_data(report):` | Define chart_data: Report dict -> JSON drawing specification, converting measured units to mg/dL. |
| 37 | `"""Report dict -> JSON drawing specification, converting measured units to mg/dL."""` | Document that the display helper returns readings and a demo flag, preserves the original report and cannot create clinical input. |
| 38 | `readings, example = display_readings(report)` | Use the same supplied-or-demo display readings in the chart and HTML card to keep their values and provenance consistent. |
| 53 | `"food": food, "food_max": max(item["high"] for item in food),` | Continue the displayed report-field expression, preserving existing measured-data and demo-source separation. |
| 54 | `"reading_label": "DEMO example readings" if example else "Measured / latest"}` | Attach a DEMO or measured label to the chart payload, using the helper source flag. |
| 78 | `history, example = display_readings(report)` | Use the same supplied-or-demo display readings in the chart and HTML card to keep their values and provenance consistent. |
| 79 | `reading = history[-1]` | Use the final point of the display sequence for the current numeric card, leaving original_information untouched. |
| 85 | `"current": f"{reading['value']:g} {reading['unit']}",` | Render the selected display value and unit as a number instead of an empty/unavailable visual metric. |
| 86 | `"current_label": "ILLUSTRATIVE GLUCOSE (DEMO)" if example else "LATEST RECORDED GLUCOSE",` | Label demo numeric values as illustrative rather than recorded patient glucose. |
| 87 | `"measured_at": readable(reading["measured_at"]),` | Display the selected value timestamp; demo provenance is shown on the same card. |
| 88 | `"freshness": "DEMO value; not a patient measurement" if example else ("Recent supplied reading" if action["fresh"] else "Reading is old or future-dated; check again"),` | Explicitly identify a demo value; actual readings retain their freshness explanation. |
| 89 | `"history_note": f"{len(history)} DEMO example values; not patient measurements" if example else f"{len(history)} supplied readings",` | State the displayed sequence count and identify synthetic examples directly above the chart. |
| 90 | `"history_values": " &#124; ".join(f"{readable(r['measured_at'])}: {r['value']:g} {r['unit']}" for r in history[-6:]),` | List numeric values, original units and readable timestamps from the same display sequence. |

## caregiver_view.py

| Line | Source | Explanation |
| --- | --- | --- |
| 25 | `result = {"level": "review", "title": "Check glucose now", "color": "#AD6600",` | Supply practical missing-data/synthetic advice: check a real reading before sugar changes, follow the care plan and seek help for severe symptoms. Screening thresholds and measured values are unchanged. |
| 26 | `"background": "#FFF5DE", "sugar": "Check a current meter or CGM reading before changing sugar intake; follow the patient's care plan.",` | Supply practical missing-data/synthetic advice: check a real reading before sugar changes, follow the care plan and seek help for severe symptoms. Screening thresholds and measured values are unchanged. |
| 27 | `"doctor": "Get urgent help for severe symptoms. Otherwise follow the care plan and contact the care team if concerned.",` | Supply practical missing-data/synthetic advice: check a real reading before sugar changes, follow the care plan and seek help for severe symptoms. Screening thresholds and measured values are unchanged. |
| 28 | `"detail": "Demo numbers below complete the display when measurements are missing; they do not determine this advice.",` | Supply practical missing-data/synthetic advice: check a real reading before sugar changes, follow the care plan and seek help for severe symptoms. Screening thresholds and measured values are unchanged. |
| 31 | `result["title"] = "Demo: check glucose and follow the care plan"` | Supply practical missing-data/synthetic advice: check a real reading before sugar changes, follow the care plan and seek help for severe symptoms. Screening thresholds and measured values are unchanged. |
| 32 | `result["detail"] = "All example readings are synthetic. Use actual measurements and the prescribed plan for patient care."` | Supply practical missing-data/synthetic advice: check a real reading before sugar changes, follow the care plan and seek help for severe symptoms. Screening thresholds and measured values are unchanged. |

## chart_renderer.ps1

| Line | Source | Explanation |
| --- | --- | --- |
| 77 | `Text $payload.reading_label 90 435 21 '#167D8D'` | Draw the source-aware legend from the payload, so synthetic timeline values say DEMO example readings instead of being labelled measured. |

## email_template.html

| Line | Source | Explanation |
| --- | --- | --- |
| 5 | `<table role="presentation" width="700" cellspacing="0" cellpadding="0" style="width:100%;max-width:700px;table-layout:fixed;background:#FFFFFF;border-radius:14px">` | Keep the main email table within its available width so nested images/cards cannot force horizontal scrolling on a phone. |
| 6 | `<tr><td style="padding:12px 28px;background:#142D48;color:#FFFFFF;border-radius:14px 14px 0 0">` | Reduce header/top padding and branding height so the action instructions appear sooner; preserve the patient identifier and prepared time. |
| 7 | `<p style="margin:0;font-size:12px;color:#D7E3EE">CARE COMPANION · PROTOTYPE · $patient</p>` | Reduce header/top padding and branding height so the action instructions appear sooner; preserve the patient identifier and prepared time. |
| 8 | `<p style="margin:4px 0 0;font-size:11px;color:#D7E3EE">Prepared $prepared</p></td></tr>` | Reduce header/top padding and branding height so the action instructions appear sooner; preserve the patient identifier and prepared time. |
| 9 | `<tr><td style="padding:14px 28px 0">` | Reduce header/top padding and branding height so the action instructions appear sooner; preserve the patient identifier and prepared time. |
| 11 | `<p style="margin:0 0 8px;font-size:12px;font-weight:bold;color:$color">CAREGIVER ACTION · DO THIS FIRST · $level</p>` | Label the opening panel as the first caregiver action while retaining its review/urgent/monitor severity. |
| 12 | `<h1 style="margin:0 0 14px;font-size:25px;color:$color">$action_title</h1>` | Use the action itself as the main heading, with severity colour and enough spacing before its instructions. |
| 13 | `<p style="margin:0 0 14px;font-size:17px;line-height:1.5"><b>Sugar: more or less?</b><br>$sugar_action</p>` | Show the sugar advice inside the opening action card, before all measurements and charts, using readable 17-pixel text and a bold label. |
| 14 | `<p style="margin:0;font-size:17px;line-height:1.5"><b>Medical help</b><br>$doctor_action</p>` | Show medical-help advice immediately below sugar advice in the opening card, making both available on the first phone screen. |
| 15 | `<p style="margin:14px 0 0;font-size:12px;line-height:1.5;color:#64748B">$action_detail</p></td></tr></table>` | Keep supporting context below the actual instructions, with smaller type so it does not displace the advice. |
| 20 | `<td width="50%" valign="top" style="padding:16px;background:#F3F7FB"><p style="margin:0;color:#64748B;font-size:12px">$current_label</p><p style="margin:10px 0;font-size:30px;font-weight:bold;color:#142D48">$current</p><p style="margin:0;font-size:12px;line-height:1.6">$measured_at<br>$freshness</p></td>` | Select a real-reading label or an explicit DEMO label for the numeric card; show value, time and provenance below it. |
| 27 | `<p style="font-size:12px;color:#64748B;line-height:1.6">The dashed forecast and shaded range are fixed demo values. They do not drive alerts. Horizontal 70/180 reference lines are illustrative; individual targets vary. When no readings are supplied, labelled DEMO values fill this display and are excluded from advice.</p>` | Explain beside the chart that absent-input numeric examples only fill the display and never determine advice. |

## test_visual_email.py

| Line | Source | Explanation |
| --- | --- | --- |
| 82 | `self.assertIn("&lt;script&gt;", html)` | Assert the displayed property: advice ordering, numeric fill, explicit demo provenance, no mutation, review status, or preservation of actual values. A mismatch fails the regression. |
| 94 | `def test_missing_values_filled_only_in_display_and_advice_is_first(self):` | Define test_missing_values_filled_only_in_display_and_advice_is_first: verify the new display/advice behaviour |
| 95 | `event = self.event()` | Prepare or render the isolated fixture through the actual helper, then inspect its displayed readings, labels and unchanged clinical data. |
| 96 | `event["glucose"] = None` | Remove the actual reading in this isolated test fixture so the visual fill path is exercised. |
| 97 | `report = server.analyze(event, PNG)` | Prepare or render the isolated fixture through the actual helper, then inspect its displayed readings, labels and unchanged clinical data. |
| 98 | `before = copy.deepcopy(report)` | Deep-copy the complete original report before rendering to detect any mutation caused by the display fill. |
| 99 | `html = visual_email.html_body(report, {"glucose_image": "cid:g", "food_image": "cid:f", "meal_image": "cid:m"})` | Prepare or render the isolated fixture through the actual helper, then inspect its displayed readings, labels and unchanged clinical data. |
| 100 | `self.assertIn("138 mg/dL", html)` | Assert the displayed property: advice ordering, numeric fill, explicit demo provenance, no mutation, review status, or preservation of actual values. A mismatch fails the regression. |
| 101 | `self.assertIn("ILLUSTRATIVE GLUCOSE (DEMO)", html)` | Assert the displayed property: advice ordering, numeric fill, explicit demo provenance, no mutation, review status, or preservation of actual values. A mismatch fails the regression. |
| 102 | `self.assertIn("not a patient measurement", html)` | Assert the displayed property: advice ordering, numeric fill, explicit demo provenance, no mutation, review status, or preservation of actual values. A mismatch fails the regression. |
| 103 | `self.assertNotIn("Unavailable", html)` | Assert the displayed property: advice ordering, numeric fill, explicit demo provenance, no mutation, review status, or preservation of actual values. A mismatch fails the regression. |
| 104 | `self.assertEqual(len(visual_email.chart_data(report)["measured"]), 5)` | Assert the displayed property: advice ordering, numeric fill, explicit demo provenance, no mutation, review status, or preservation of actual values. A mismatch fails the regression. |
| 105 | `self.assertEqual(visual_email.chart_data(report)["reading_label"], "DEMO example readings")` | Assert the displayed property: advice ordering, numeric fill, explicit demo provenance, no mutation, review status, or preservation of actual values. A mismatch fails the regression. |
| 106 | `self.assertLess(html.index("Sugar: more or less?"), html.index("138 mg/dL"))` | Assert the displayed property: advice ordering, numeric fill, explicit demo provenance, no mutation, review status, or preservation of actual values. A mismatch fails the regression. |
| 107 | `self.assertLess(html.index("Medical help"), html.index("138 mg/dL"))` | Assert the displayed property: advice ordering, numeric fill, explicit demo provenance, no mutation, review status, or preservation of actual values. A mismatch fails the regression. |
| 108 | `self.assertEqual(report, before)` | Assert the displayed property: advice ordering, numeric fill, explicit demo provenance, no mutation, review status, or preservation of actual values. A mismatch fails the regression. |
| 109 | `self.assertEqual(report["caregiver_action"]["level"], "review")` | Assert the displayed property: advice ordering, numeric fill, explicit demo provenance, no mutation, review status, or preservation of actual values. A mismatch fails the regression. |
| 111 | `def test_real_values_not_replaced_by_demo_numbers(self):` | Define test_real_values_not_replaced_by_demo_numbers: verify the new display/advice behaviour |
| 112 | `event = self.event(7.2, unit="mmol/L")` | Prepare or render the isolated fixture through the actual helper, then inspect its displayed readings, labels and unchanged clinical data. |
| 113 | `report = server.analyze(event, PNG)` | Prepare or render the isolated fixture through the actual helper, then inspect its displayed readings, labels and unchanged clinical data. |
| 114 | `readings, example = visual_email.display_readings(report)` | Prepare or render the isolated fixture through the actual helper, then inspect its displayed readings, labels and unchanged clinical data. |
| 115 | `self.assertFalse(example)` | Assert the displayed property: advice ordering, numeric fill, explicit demo provenance, no mutation, review status, or preservation of actual values. A mismatch fails the regression. |
| 116 | `self.assertEqual(readings, [event["glucose"]])` | Assert the displayed property: advice ordering, numeric fill, explicit demo provenance, no mutation, review status, or preservation of actual values. A mismatch fails the regression. |

## Review artifacts and verification

README and the main walkthrough link this change and explain the numeric display fill. PROGRESS records the scope and evidence. The generated self-contained HTML, desktop image, 390x844 phone image and offline .eml are under ignored output/. They contain a synthetic demo, and no network email was sent.

The combined suite passed 32 tests. New regressions check that advice precedes the numeric card, missing displays have five numeric examples, example labels are present, the report/action remain unchanged and actual readings are preserved. Actual PNG/MIME transport tests continue passing. Browser inspection confirmed both advice blocks on the first phone screen; CDP reported a 390-pixel viewport and 390-pixel document width. No new dependencies, clinical thresholds, medication rules, commits or pushes were added.
