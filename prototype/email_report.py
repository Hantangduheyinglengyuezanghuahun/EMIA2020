"""Turn the internal demo report into a readable plain-text caregiver email."""

from datetime import datetime
from textwrap import fill


def format_email_report(report):
    """Validated analysis dict -> plain-text email body; no files, network or mutations.

    Preserve measured values and units; label every predicted value as simulated.
    Format timezone-qualified ISO timestamps with their original UTC offsets.
    """
    def display_time(value):
        """ISO timestamp string -> readable date/time with its numeric UTC offset."""
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%d %b %Y, %H:%M (UTC%z)")

    def estimate_line(label, item, unit):
        """Label, estimate/range dict and unit string -> one readable estimate line."""
        low, high = item["illustrative_range"]
        return f"{label}: {item['estimate']:g} {unit} (illustrative range: {low:g} to {high:g} {unit})"

    original = report["original_information"]
    reading = original["glucose"]
    measured = "No measured glucose reading was provided."
    if reading is not None:
        measured = (f"Measured glucose: {reading['value']:g} {reading['unit']}\n"
                    f"Measurement time: {display_time(reading['measured_at'])}")
    food = report["food"]
    glucose = report["estimated_current_glucose"]
    sections = [
        "MEAL AND GLUCOSE REPORT\nSIMULATED DEMONSTRATION",
        f"Patient: {original['patient_id']}\nMeal recorded at: {display_time(original['meal_captured_at'])}",
        "RECORDED GLUCOSE\n" + measured,
        "SIMULATED FOOD ESTIMATES\n" + estimate_line("Sugar", food["sugar_g"], "g") + "\n"
        + estimate_line("Total carbohydrates", food["carbohydrate_g"], "g"),
        "SIMULATED CURRENT GLUCOSE\n" + estimate_line("Estimated glucose", glucose, glucose["unit"])
        + "\nThis is a fixed demo example, not a measured reading or a validated prediction.",
        "CAREGIVER NOTES\n" + fill(report["suggestions"], width=78),
        "MEAL PHOTO\nSee the attached meal image.",
        "IMPORTANT LIMITATIONS\n" + fill(report["warning"], width=78),
    ]
    if "caregiver_action" in report:
        action = report["caregiver_action"]
        sections.insert(1, f"CAREGIVER ACTION: {action['title']}\n{action['detail']}\nSugar: {action['sugar']}\nMedical help: {action['doctor']}")
    return "\n\n".join(sections) + "\n"
