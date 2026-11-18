"""Create measured-reading screening cards and an explicitly simulated forecast."""

from datetime import datetime, timedelta, timezone


def as_time(value):
    """Timezone-qualified ISO string -> aware datetime; validation happens in server.py."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def mgdl(reading):
    """Reading dict -> glucose in mg/dL for plotting and threshold comparison only."""
    return reading["value"] * (18.0182 if reading["unit"] == "mmol/L" else 1)


def caregiver_summary(event, now=None):
    """Validated event + optional aware clock -> action cards; never uses AI estimates.

    Fresh means at most 15 minutes old; this is a prototype policy, not a clinical
    standard. Supplied severe symptoms override missing/stale readings. These
    generic screening rules do not determine insulin doses or certify safety.
    """
    now = now or datetime.now(timezone.utc)
    reading = event["glucose"]
    result = {"level": "review", "title": "Check glucose now", "color": "#AD6600",
              "background": "#FFF5DE", "sugar": "Check a current meter or CGM reading before changing sugar intake; follow the patient's care plan.",
              "doctor": "Get urgent help for severe symptoms. Otherwise follow the care plan and contact the care team if concerned.",
              "detail": "Demo numbers below complete the display when measurements are missing; they do not determine this advice.",
              "generated_at": now.isoformat(), "fresh": False}
    if event.get("synthetic", False):
        result["title"] = "Demo: check glucose and follow the care plan"
        result["detail"] = "All example readings are synthetic. Use actual measurements and the prescribed plan for patient care."
        return result
    severe = event.get("severe_symptoms", False)
    if severe:
        result.update(level="urgent", title="Seek emergency medical help", color="#B42318", background="#FEECE9",
                      detail="Severe symptoms were reported. Get emergency help now; do not wait for an email response.",
                      sugar="If unconscious or unable to swallow, do not give food or drink by mouth.",
                      doctor="Emergency help now; follow the prescribed emergency plan.")
        return result
    if reading is None:
        return result
    age = (now - as_time(reading["measured_at"])).total_seconds()
    if age < 0 or age > 900:
        result["detail"] = "The latest reading is old or future-dated. Obtain a current reading; the old value is shown below."
        return result
    result["fresh"] = True
    value = mgdl(reading)
    if value < 55:
        result.update(level="urgent", title="Very low reading — urgent help", color="#B42318", background="#FEECE9",
                      detail="A measured glucose below 55 mg/dL needs immediate attention. Follow the emergency care plan.",
                      sugar="If awake and able to swallow, follow the prescribed low-glucose treatment plan. Otherwise give nothing by mouth.",
                      doctor="Seek urgent medical help; do not wait for this prototype.")
    elif value < 70:
        result.update(title="Low reading — act on the low-glucose plan",
                      detail="The measured reading is below 70 mg/dL. Check on the patient and follow their prescribed low-glucose plan.",
                      sugar="More fast-acting carbohydrate may be needed under the low-glucose plan, if awake and able to swallow.",
                      doctor="Seek urgent help for severe symptoms or if the low reading does not improve.")
    elif value >= 250:
        result.update(title="High reading — contact the care team",
                      detail="A reading of at least 250 mg/dL needs the prescribed high-glucose/ketone plan and care-team advice.",
                      sugar="Extra sugar is not a correction for this high reading. Review future meal choices with the care team.",
                      doctor="Contact the care team. Emergency help if readings stay at 300 mg/dL or above, or severe symptoms occur.")
        recent = [r for r in event.get("glucose_history", [])
                  if 0 < (as_time(reading["measured_at"]) - as_time(r["measured_at"])).total_seconds() <= 7200]
        if value >= 300 and recent and mgdl(recent[-1]) >= 300:
            result.update(level="urgent", title="Repeated very high readings — emergency help", color="#B42318",
                          background="#FEECE9", doctor="Seek emergency medical help now.",
                          detail="The latest and previous supplied readings are both at least 300 mg/dL. Follow the emergency plan.")
    elif value > 180:
        result.update(title="Above example reference — review the care plan",
                      detail="The reading is above the chart's example 180 mg/dL reference. Personal targets depend on meal timing and the care plan.",
                      sugar="Discuss meal portions and sugar choices with the care team; do not treat this as a low reading.")
    else:
        result.update(level="monitor", title="No threshold alert in the latest reading", color="#087F73", background="#E8F7F3",
                      detail="Continue prescribed monitoring. This reading alone cannot establish that the patient is safe.",
                      sugar="No extra sugar or restriction is indicated by these prototype threshold checks.",
                      doctor="Continue the care plan. Seek help for symptoms or concerns, regardless of this colour.")
    return result


def demo_forecast(now):
    """Aware clock -> three fixed future demo points in mg/dL; no physiological model."""
    return [{"at": (now + timedelta(minutes=minutes)).isoformat(), "estimate": value,
             "low": low, "high": high, "unit": "mg/dL", "source": "fixed_demo_stub"}
            for minutes, value, low, high in ((30, 160, 110, 210), (60, 150, 95, 205), (120, 125, 85, 190))]
