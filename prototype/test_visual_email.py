"""Verify action screening, history inputs, HTML escaping and embedded chart rendering."""

import copy
import json
import struct
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import run_demo
import server
import visual_email
from caregiver_view import caregiver_summary
from test_pipeline import EVENT, PNG

NOW = datetime(2026, 11, 13, 8, 0, tzinfo=timezone.utc)


class VisualEmailTests(unittest.TestCase):
    """Check the measured-data/forecast boundary before any email is sent."""

    def event(self, value=120, minutes_old=0, unit="mg/dL"):
        """Build a valid synthetic test fixture without labelling it as a demo scenario."""
        payload = copy.deepcopy(EVENT)
        payload["glucose"] = {"value": value, "unit": unit, "measured_at": (NOW-timedelta(minutes=minutes_old)).isoformat()}
        return server.validate_event(payload)[0]

    def test_thresholds_use_fresh_measurements(self):
        for value, level in ((54, "urgent"), (55, "review"), (69, "review"), (70, "monitor"), (180, "monitor"), (181, "review"), (250, "review")):
            with self.subTest(value=value):
                self.assertEqual(caregiver_summary(self.event(value), NOW)["level"], level)

    def test_missing_stale_future_and_synthetic_cannot_be_monitor(self):
        events = [self.event(minutes_old=16), self.event(minutes_old=-1)]
        missing = self.event()
        missing["glucose"] = None
        events.append(missing)
        synthetic = self.event(50)
        synthetic["synthetic"] = True
        events.append(synthetic)
        for event in events:
            self.assertEqual(caregiver_summary(event, NOW)["level"], "review")

    def test_severe_symptoms_override_missing_reading(self):
        event = self.event()
        event.update(glucose=None, severe_symptoms=True)
        self.assertEqual(caregiver_summary(event, NOW)["level"], "urgent")

    def test_repeat_high_and_unit_conversion(self):
        event = self.event(305)
        event["glucose_history"] = [{"value": 310, "unit": "mg/dL", "measured_at": (NOW-timedelta(minutes=30)).isoformat()}]
        self.assertEqual(caregiver_summary(event, NOW)["level"], "urgent")
        self.assertEqual(caregiver_summary(self.event(3, unit="mmol/L"), NOW)["level"], "urgent")

    def test_history_file_and_legacy_input_both_work(self):
        with tempfile.TemporaryDirectory() as directory:
            image, glucose = Path(directory)/"meal.png", Path(directory)/"glucose.json"
            image.write_bytes(PNG)
            current = self.event()["glucose"]
            history = [self.event(110, minutes_old=30)["glucose"]]
            glucose.write_text(json.dumps({"current": current, "history": history, "synthetic": True}))
            event, raw, subtype = run_demo.read_event(image, glucose, "demo")
            self.assertEqual(event["glucose_history"], history)
            self.assertTrue(event["synthetic"])
            glucose.write_text(json.dumps(current))
            self.assertEqual(run_demo.read_event(image, glucose, "demo")[0]["glucose"], current)

    def test_bad_history_and_flags_rejected(self):
        for patch in ({"glucose_history": "wrong"}, {"glucose_history": [{}]}, {"severe_symptoms": "yes"}, {"synthetic": 1}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                server.validate_event(dict(EVENT, **patch))

    def test_forecast_is_not_used_for_alert_and_html_is_escaped(self):
        event = self.event()
        event["patient_id"] = '<script>alert("x")</script>'
        report = server.analyze(event, PNG)
        report["caregiver_action"] = caregiver_summary(event, NOW)
        report["estimated_current_glucose"]["estimate"] = 10
        html = visual_email.html_body(report, {"glucose_image": "cid:g", "food_image": "cid:f", "meal_image": "cid:m"})
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertEqual(report["caregiver_action"]["level"], "monitor")
        self.assertIn("No threshold alert", html)

    def test_actual_chart_pngs_and_mixed_units(self):
        event = self.event(7.2, unit="mmol/L")
        report = server.analyze(event, PNG)
        self.assertAlmostEqual(visual_email.chart_data(report)["measured"][0]["y"], 129.7, places=1)
        for name, png in visual_email.render_charts(report).items():
            self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertEqual(struct.unpack(">II", png[16:24]), (1200, 720 if name == "glucose" else 480))

    def test_missing_values_filled_only_in_display_and_advice_is_first(self):
        event = self.event()
        event["glucose"] = None
        report = server.analyze(event, PNG)
        before = copy.deepcopy(report)
        html = visual_email.html_body(report, {"glucose_image": "cid:g", "food_image": "cid:f", "meal_image": "cid:m"})
        self.assertIn("168 mg/dL", html)
        self.assertIn("ILLUSTRATIVE GLUCOSE (DEMO)", html)
        self.assertIn("not a patient measurement", html)
        self.assertNotIn("Unavailable", html)
        self.assertEqual(len(visual_email.chart_data(report)["measured"]), 5)
        self.assertEqual(visual_email.chart_data(report)["reading_label"], "DEMO example readings")
        self.assertLess(html.index("Sugar: more or less?"), html.index("168 mg/dL"))
        self.assertLess(html.index("Medical help"), html.index("168 mg/dL"))
        self.assertEqual(report, before)
        self.assertEqual(report["caregiver_action"]["level"], "review")

    def test_current_estimate_visible_separately_from_measured_and_future(self):
        report = server.analyze(self.event(125), PNG)
        report["estimated_current_glucose"].update(estimate=147, illustrative_range=[102, 195])
        html = visual_email.html_body(report, {"glucose_image": "cid:g", "food_image": "cid:f", "meal_image": "cid:m"})
        self.assertIn("ESTIMATED CURRENT GLUCOSE (SIMULATED)", html)
        self.assertIn("147 mg/dL", html)
        self.assertIn("102 to 195 mg/dL", html)
        self.assertIn("125 mg/dL", html)
        self.assertIn("160 mg/dL", html)
        self.assertLess(html.index("Medical help"), html.index("147 mg/dL"))
        data = visual_email.chart_data(report)
        self.assertEqual(data["current_estimate"], {"x": data["now"], "y": 147, "low": 102, "high": 195})
        self.assertEqual(data["measured"][0]["y"], 125)

    def test_real_values_not_replaced_by_demo_numbers(self):
        event = self.event(7.2, unit="mmol/L")
        report = server.analyze(event, PNG)
        readings, example = visual_email.display_readings(report)
        self.assertFalse(example)
        self.assertEqual(readings, [event["glucose"]])

    def test_glycat_reference_layout_and_embedded_logo(self):
        """Check image roles, summary placement and demo-only history against the new references."""
        event = self.event()
        event["glucose"] = None
        report = server.analyze(event, PNG)
        before = copy.deepcopy(report)
        message = visual_email.compose_email(report, PNG, "png", "sender@example.test", "caregiver@example.test")
        html = message.get_body(preferencelist=("html",)).get_content()
        self.assertLess(html.index("Medical help"), html.index("GLYCAT MEAL SUMMARY"))
        self.assertLess(html.index("GLYCAT MEAL SUMMARY"), html.index("Glucose: previous, latest and future"))
        self.assertIn("Slightly High", html)
        self.assertIn("not a clinical classification", html)
        self.assertEqual(html.count('src="cid:meal-photo"'), 1)
        self.assertIn('src="cid:glycat-logo"', html)
        images = {part.get("Content-ID"): part.get_payload(decode=True) for part in message.walk() if part.get_content_maintype() == "image"}
        self.assertEqual(images["<glycat-logo>"], visual_email.LOGO.read_bytes())
        self.assertEqual(images["<meal-photo>"], PNG)
        self.assertEqual([p["y"] for p in visual_email.chart_data(report)["measured"]], [250, 240, 220, 195, 168])
        self.assertEqual(report, before)
        self.assertIsNone(report["original_information"]["glucose"])
        self.assertEqual(report["caregiver_action"]["level"], "review")


if __name__ == "__main__":
    unittest.main()
