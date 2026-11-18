"""Exercise Chinese MIME output, model separation and all existing screening branches."""

import copy
import unittest

import chinese_email
import server
import visual_email
from caregiver_view import caregiver_summary
import test_visual_email as fixtures
from test_pipeline import PNG


class ChineseEmailTests(unittest.TestCase):
    def test_translated_mime_and_embedded_photo(self):
        event = fixtures.VisualEmailTests().event(7.2, unit="mmol/L")
        report = server.analyze(event, PNG)
        report["language"] = "zh-CN"
        before = copy.deepcopy(report)
        message = visual_email.compose_email(report, PNG, "png", "sender@example.test", "caregiver@example.test")
        self.assertIn("模拟演示", str(message["Subject"]))
        html = message.get_body(preferencelist=("html",)).get_content()
        plain = message.get_body(preferencelist=("plain",)).get_content()
        for body in (html, plain):
            self.assertIn("当前血糖估算", body)
            self.assertIn("140 mg/dL", body)
            self.assertIn("7.2 mmol/L", body)
            self.assertIn("160 mg/dL", body)
            self.assertIn("未经", body)
        self.assertLess(html.index("是否需要就医"), html.index("140 mg/dL"))
        self.assertIn('lang="zh-CN"', html)
        self.assertNotIn("CAREGIVER", html)
        self.assertIn("照护建议", plain)
        images = {p.get("Content-ID"): p.get_payload(decode=True) for p in message.walk() if p.get_content_maintype() == "image"}
        self.assertEqual(images["<meal-photo>"], PNG)
        self.assertEqual(len(images), 3)
        self.assertEqual(report, before)
        data = visual_email.chart_data(report)
        self.assertEqual(data["food"][0]["label"], "总碳水化合物")
        self.assertEqual(data["translations"]["NOW"], "现在")

    def test_all_screening_actions_have_chinese_advice(self):
        events = [fixtures.VisualEmailTests().event(value, minutes_old=age) for value, age in
                  ((50, 0), (60, 0), (120, 0), (190, 0), (260, 0), (120, 20))]
        base = fixtures.VisualEmailTests().event()
        events += [dict(base, glucose=None), dict(base, synthetic=True), dict(base, severe_symptoms=True)]
        high = fixtures.VisualEmailTests().event(310)
        high["glucose_history"] = [fixtures.VisualEmailTests().event(305, minutes_old=30)["glucose"]]
        events.append(high)
        for event in events:
            translated = chinese_email.action_text(caregiver_summary(event, fixtures.NOW))
            for value in translated.values():
                self.assertTrue(any("\u4e00" <= char <= "\u9fff" for char in value))


if __name__ == "__main__":
    unittest.main()
