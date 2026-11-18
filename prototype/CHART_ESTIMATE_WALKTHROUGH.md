# Larger chart and visible current estimate

The existing server already returned a fixed current estimate of 140 mg/dL with an illustrative range of 100 to 190 mg/dL. The HTML omitted that field. This update displays the existing result in its own card and at NOW on the chart. Original measurements, the fixed model and clinical screening rules are unchanged.

Removed behavior: the HTML no longer omits the current estimate, the glucose raster is no longer constrained to 1200 by 480, and the narrow 700-pixel email is replaced by an 800-pixel maximum. Food rendering retains its previous raster dimensions. Advice remains first.

Every added or replaced nonblank source line is listed below; blank lines only separate code. Existing unchanged lines remain explained in the earlier walkthroughs.

## visual_email.py

| Line | Source | What it does and why |
| --- | --- | --- |
| 52 | `"max_y": math.ceil(max([p["y"] for p in points] + [p["high"] for p in forecast] + report["estimated_current_glucose"]["illustrative_range"] + [240])/40)*40,` | Include the current estimate range when choosing the glucose axis ceiling, so the estimate and its uncertainty cannot be clipped. |
| 53 | `"current_estimate": {"x": now, "y": report["estimated_current_glucose"]["estimate"],` | Add a separate plotting record at the report generation time; its y coordinate comes from the existing current-glucose model output. |
| 54 | `"low": report["estimated_current_glucose"]["illustrative_range"][0],` | Pass the model current-estimate lower illustrative bound in mg/dL to the drawing layer. |
| 55 | `"high": report["estimated_current_glucose"]["illustrative_range"][1]},` | Pass the upper illustrative bound in mg/dL, completing the current-estimate plotting record. |
| 96 | `estimate = report["estimated_current_glucose"]` | Read the existing estimated_current_glucose object; this restores the missing HTML output without changing the estimation model. |
| 97 | `values.update(estimated_current=f"{estimate['estimate']:g} {estimate['unit']}",` | Format the actual report estimate and unit as the new card value; this is separate from supplied measurements and future forecasts. |
| 98 | `estimated_range=f"{estimate['illustrative_range'][0]:g} to {estimate['illustrative_range'][1]:g} {estimate['unit']}")` | Format the lower and upper illustrative bounds with units for the estimate card. |

## email_template.html

| Line | Source | What it does and why |
| --- | --- | --- |
| 5 | `<table role="presentation" width="800" cellspacing="0" cellpadding="0" style="width:100%;max-width:800px;table-layout:fixed;background:#FFFFFF;border-radius:14px">` | Widen the email maximum from 700 to 800 pixels while retaining fluid width and fixed table layout for narrow clients. |
| 18 | `<tr><td style="padding:4px 28px 16px"><table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr><td style="padding:20px;background:#F4EFFF;border-left:6px solid #8055CF"><p style="margin:0;font-size:14px;font-weight:bold;color:#7050A5">ESTIMATED CURRENT GLUCOSE (SIMULATED)</p><p style="margin:10px 0;font-size:38px;font-weight:bold;color:#7050A5">$estimated_current</p><p style="margin:0;font-size:14px;line-height:1.6">Illustrative range: $estimated_range<br>Fixed demo estimate; not a measured reading or a validated prediction.</p></td></tr></table></td></tr>` | Insert a full-width purple current-estimate card below the advice and before the measured/forecast cards. It renders the estimate and illustrative range, labels both simulated and explains their provenance. |
| 22 | `<td width="50%" valign="top" style="padding:16px;background:#F4EFFF"><p style="margin:0;color:#7050A5;font-size:12px">+30 MIN DEMO FORECAST</p><p style="margin:10px 0;font-size:30px;font-weight:bold;color:#7050A5">$forecast_value</p><p style="margin:0;font-size:12px;line-height:1.6">Illustrative range: $forecast_range mg/dL<br>Fixed example · unvalidated</p></td>` | Use the report-derived forecast_range placeholder with mg/dL instead of hard-coded range text; preserve the distinct future-value card. |
| 25 | `<tr><td style="padding:0 12px 22px"><h2 style="margin:0 0 8px;font-size:21px">Glucose: previous, latest and future</h2>` | Reduce glucose-section side padding from 28 to 12 pixels, giving the chart 776 pixels of display width in the enlarged email. |
| 27 | `<img src="$glucose_image" alt="Glucose history, current simulated estimate and dashed future forecast, with illustrative ranges." width="776" style="display:block;width:100%;height:auto;border:1px solid #E2E8F0">` | Give the glucose PNG a matching 776-pixel width with fluid scaling, and describe the newly plotted current estimate in its alternative text. |
| 28 | `<p style="font-size:12px;color:#64748B;line-height:1.6">The purple NOW marker is the estimated current glucose. The dashed forecast and shaded range are fixed demo values. They do not drive alerts. Horizontal 70/180 reference lines are illustrative; individual targets vary. When no readings are supplied, labelled DEMO values fill this display and are excluded from advice.</p>` | Explain the purple current-estimate marker, dashed future forecast and uncertainty shading so viewers can distinguish the displayed quantities. |
| 33 | `<img src="$food_image" alt="Simulated total carbohydrates 60 grams, range 40–85; sugar 12 grams, range 6–20. Sugar is part of total carbohydrates." width="776" style="display:block;width:100%;height:auto;border:1px solid #E2E8F0">` | Update the food PNG fallback width to 776 pixels to match the wider template; fluid width still fits its padded section. |

## chart_renderer.ps1

| Line | Source | What it does and why |
| --- | --- | --- |
| 25 | `$height = if ($kind -eq 'glucose') { 720 } else { 480 }` | Select a 720-pixel canvas for glucose and retain the existing 480-pixel canvas for food. |
| 26 | `$bitmap = [System.Drawing.Bitmap]::new(1200, $height)` | Allocate the chart PNG using the chosen height and unchanged 1200-pixel raster width. |
| 33 | `Text 'GLUCOSE HISTORY + CURRENT ESTIMATE + FORECAST' 30 12 30 '#142D48'` | Enlarge the chart heading and explicitly name the current estimate alongside history and forecast. |
| 39 | `function Py($value) { 500 - 390 * [double]$value / $maxY }` | Expand the plot to a 390-pixel vertical scale ending at y=500, making the glucose trend taller. |
| 44 | `Text ([math]::Round($value)) 24 ($y - 18) 28` | Increase glucose y-axis numbers to 28 raster pixels for readability after email scaling. |
| 73 | `foreach ($point in $forecast) { Text ([string]$point.y) ((Px $point.x)-16) ((Py $point.y)-40) 30 '#8055CF' }` | Increase the future point labels to 30 pixels and move them above their points to keep the line visible. |
| 74 | `$estimate = $payload.current_estimate` | Read the separate current_estimate drawing record created from the report model output. |
| 75 | `$estimateX = Px $estimate.x` | Convert the estimate timestamp into its horizontal plot coordinate. |
| 76 | `Line $estimateX (Py $estimate.low) $estimateX (Py $estimate.high) '#8055CF' 4` | Draw a purple vertical whisker spanning the current-estimate illustrative bounds. |
| 77 | `Line ($estimateX-12) (Py $estimate.low) ($estimateX+12) (Py $estimate.low) '#8055CF' 4` | Draw the lower horizontal cap of the estimate range whisker. |
| 78 | `Line ($estimateX-12) (Py $estimate.high) ($estimateX+12) (Py $estimate.high) '#8055CF' 4` | Draw the upper horizontal cap, making the range endpoints explicit. |
| 79 | `$brush = [System.Drawing.SolidBrush]::new((Colour '#8055CF'))` | Create a purple drawing brush specifically for the current-estimate point. |
| 80 | `try { $g.FillEllipse($brush, [single]($estimateX-8), [single]((Py $estimate.y)-8), 16, 16) } finally { $brush.Dispose() }` | Paint a 16-pixel current-estimate marker at NOW and dispose the brush even if drawing fails. |
| 81 | `Line $estimateX (Py $estimate.y) (Px $forecast[0].x) (Py $forecast[0].y) '#8055CF' 4 $true` | Connect the current model estimate to the first future demo point using the dashed purple forecast style. |
| 82 | `Text ('Estimate now: ' + $estimate.y) ([math]::Max(95, $estimateX-250)) 80 28 '#8055CF'` | Print the numeric current estimate near the top of the plot in purple so it is explicitly visible on the chart. |
| 84 | `Line $nowX 78 $nowX 500 '#64748B' 2 $true` | Extend the existing NOW time guide to the bottom of the taller plot. |
| 86 | `foreach ($tick in $payload.ticks) { Text $tick.label ([math]::Min(1000, [math]::Max(70, (Px $tick.x)-58))) 520 28 }` | Move time labels beneath the taller plot and enlarge them to 28 raster pixels. |
| 87 | `Text $payload.reading_label 90 605 28 '#167D8D'` | Move the measured/demo history legend beneath the time axis and enlarge it. |
| 88 | `Text 'Dashed: demo future forecast' 600 605 28 '#8055CF'` | Place the future-forecast legend next to the history legend in larger type. |
| 89 | `Text 'Shading / whisker: illustrative ranges (not validated)' 90 655 28 '#8055CF'` | Use a second legend row to identify both forecast shading and the new current-range whisker as unvalidated illustrative uncertainty. |

## test_visual_email.py

| Line | Source | What it does and why |
| --- | --- | --- |
| 90 | `for name, png in visual_email.render_charts(report).items():` | Keep chart names alongside PNG bytes so each chart can be checked against its own intended raster size. |
| 92 | `self.assertEqual(struct.unpack(">II", png[16:24]), (1200, 720 if name == "glucose" else 480))` | Check the PNG header: glucose must now be 1200 by 720, while food remains 1200 by 480. |
| 111 | `def test_current_estimate_visible_separately_from_measured_and_future(self):` | Define a regression proving the current estimate is independently displayed rather than confused with the latest measurement or future forecast. |
| 112 | `report = server.analyze(self.event(125), PNG)` | Build a report with an actual supplied test measurement of 125 mg/dL. |
| 113 | `report["estimated_current_glucose"].update(estimate=147, illustrative_range=[102, 195])` | Set a distinctive model estimate and bounds, proving the template and chart use report data rather than hard-coded display values. |
| 114 | `html = visual_email.html_body(report, {"glucose_image": "cid:g", "food_image": "cid:f", "meal_image": "cid:m"})` | Render HTML locally with content-ID placeholders; no message is sent. |
| 115 | `self.assertIn("ESTIMATED CURRENT GLUCOSE (SIMULATED)", html)` | Assert that the rendered HTML includes this required label or distinct numerical value, preventing the estimate, range, measurement or forecast from disappearing. |
| 116 | `self.assertIn("147 mg/dL", html)` | Assert that the rendered HTML includes this required label or distinct numerical value, preventing the estimate, range, measurement or forecast from disappearing. |
| 117 | `self.assertIn("102 to 195 mg/dL", html)` | Assert that the rendered HTML includes this required label or distinct numerical value, preventing the estimate, range, measurement or forecast from disappearing. |
| 118 | `self.assertIn("125 mg/dL", html)` | Assert that the rendered HTML includes this required label or distinct numerical value, preventing the estimate, range, measurement or forecast from disappearing. |
| 119 | `self.assertIn("160 mg/dL", html)` | Assert that the rendered HTML includes this required label or distinct numerical value, preventing the estimate, range, measurement or forecast from disappearing. |
| 120 | `self.assertLess(html.index("Medical help"), html.index("147 mg/dL"))` | Assert that medical-help advice remains above the newly added current-estimate card. |
| 121 | `data = visual_email.chart_data(report)` | Build the chart specification to inspect its separate current-estimate and measured series. |
| 122 | `self.assertEqual(data["current_estimate"], {"x": data["now"], "y": 147, "low": 102, "high": 195})` | Assert that the new chart marker contains the report estimate, its bounds and the generation timestamp. |
| 123 | `self.assertEqual(data["measured"][0]["y"], 125)` | Assert that the original measured series still holds 125 mg/dL, independently of the model estimate. |
