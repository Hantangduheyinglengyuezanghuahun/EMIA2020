"""Simplified Chinese presentation helpers; preserve source values and screening rules."""

from datetime import datetime, timedelta, timezone
from caregiver_view import as_time


ACTION_TEXT = {
    "Check glucose now": "请现在测量血糖",
    "Check a current meter or CGM reading before changing sugar intake; follow the patient's care plan.": "请先用血糖仪或连续血糖监测设备确认当前血糖，再按患者既定照护方案调整糖分摄入。",
    "Get urgent help for severe symptoms. Otherwise follow the care plan and contact the care team if concerned.": "如有严重症状，请立即寻求紧急医疗帮助。其他情况请遵循既定照护方案；如有疑问，请联系医护团队。",
    "Demo numbers below complete the display when measurements are missing; they do not determine this advice.": "未提供实测值时，下方以演示数字补全图表；这些数字不用于判断患者状况或生成上述建议。",
    "Demo: check glucose and follow the care plan": "演示：请测量血糖并遵循照护方案",
    "All example readings are synthetic. Use actual measurements and the prescribed plan for patient care.": "示例读数均为模拟数据。实际照护必须依据真实测量结果及医生制定的方案。",
    "Seek emergency medical help": "请立即寻求紧急医疗帮助",
    "Severe symptoms were reported. Get emergency help now; do not wait for an email response.": "已报告严重症状。请立即寻求紧急医疗帮助，不要等待邮件回复。",
    "If unconscious or unable to swallow, do not give food or drink by mouth.": "如果患者失去意识或无法吞咽，请勿经口喂食或喂水。",
    "Emergency help now; follow the prescribed emergency plan.": "请立即寻求紧急医疗帮助，并遵循既定应急方案。",
    "The latest reading is old or future-dated. Obtain a current reading; the old value is shown below.": "最近读数已过时或时间在未来。请重新测量；原读数仍显示在下方。",
    "A measured glucose below 55 mg/dL needs immediate attention. Follow the emergency care plan.": "实测血糖低于 55 mg/dL，需要立即处理。请遵循既定应急照护方案。",
    "If awake and able to swallow, follow the prescribed low-glucose treatment plan. Otherwise give nothing by mouth.": "若患者清醒且能够吞咽，请按既定低血糖处理方案执行。否则请勿经口喂食或喂水。",
    "Seek urgent medical help; do not wait for this prototype.": "请立即寻求紧急医疗帮助，不要等待本原型系统。",
    "The measured reading is below 70 mg/dL. Check on the patient and follow their prescribed low-glucose plan.": "实测血糖低于 70 mg/dL。请查看患者情况，并执行其既定低血糖处理方案。",
    "More fast-acting carbohydrate may be needed under the low-glucose plan, if awake and able to swallow.": "若患者清醒且能够吞咽，可能需要按既定低血糖方案补充快速吸收的碳水化合物。",
    "Seek urgent help for severe symptoms or if the low reading does not improve.": "如有严重症状，或低血糖未改善，请立即寻求医疗帮助。",
    "A reading of at least 250 mg/dL needs the prescribed high-glucose/ketone plan and care-team advice.": "读数达到 250 mg/dL 或以上，请按既定高血糖／酮体处理方案执行，并联系医护团队。",
    "Extra sugar is not a correction for this high reading. Review future meal choices with the care team.": "额外补糖不能纠正这一高血糖读数。请与医护团队讨论后续饮食安排。",
    "Contact the care team. Emergency help if readings stay at 300 mg/dL or above, or severe symptoms occur.": "请联系医护团队。若血糖持续达到 300 mg/dL 或以上，或出现严重症状，请寻求紧急医疗帮助。",
    "Seek emergency medical help now.": "请立即寻求紧急医疗帮助。",
    "The latest and previous supplied readings are both at least 300 mg/dL. Follow the emergency plan.": "最近两次提供的读数均达到 300 mg/dL 或以上。请遵循应急方案。",
    "The reading is above the chart's example 180 mg/dL reference. Personal targets depend on meal timing and the care plan.": "读数高于图中 180 mg/dL 的示例参考线。个人目标取决于进餐时间及照护方案。",
    "Discuss meal portions and sugar choices with the care team; do not treat this as a low reading.": "请与医护团队讨论食物份量及糖分选择，不要将其按低血糖处理。",
    "No threshold alert in the latest reading": "最近读数未触发阈值提醒",
    "Continue prescribed monitoring. This reading alone cannot establish that the patient is safe.": "请继续按既定方案监测。仅凭此读数不能确认患者安全。",
    "No extra sugar or restriction is indicated by these prototype threshold checks.": "本原型的阈值检查未提示需要额外补糖或限糖。",
    "Continue the care plan. Seek help for symptoms or concerns, regardless of this colour.": "请继续遵循照护方案。无论显示何种颜色，如有症状或担忧都应寻求帮助。",
}


def action_text(action):
    """Screening dict -> four translated display strings; no clinical recalculation."""
    title = action["title"]
    for prefix, translated in (("Very low reading", "血糖明显偏低：请立即求助"),
                               ("Low reading", "血糖偏低：请执行低血糖方案"),
                               ("High reading", "血糖偏高：请联系医护团队"),
                               ("Repeated very high", "连续出现明显高血糖：请紧急求助"),
                               ("Above example", "高于示例参考值：请复核照护方案")):
        if title.startswith(prefix):
            title = translated
            break
    return {"action_title": ACTION_TEXT.get(title, title),
            **{target: ACTION_TEXT[action[source]] for target, source in
               (("action_detail", "detail"), ("sugar_action", "sugar"), ("doctor_action", "doctor"))}}


def display_values(report, values, history, example):
    """Report + English value dict -> Chinese copy; source records remain unchanged."""
    result = dict(values)
    result["summary_status"] = "略高" if report["estimated_current_glucose"].get("display_status") == "slightly_high" else "仅供模拟演示"
    result.update(action_text(report["caregiver_action"]))
    readable = lambda value: as_time(value).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M") + "（香港时间）"
    result.update(level={"urgent": "紧急求助", "review": "需要检查", "monitor": "继续监测"}[report["caregiver_action"]["level"]],
                  prepared=readable(report["caregiver_action"]["generated_at"]),
                  measured_at=readable(history[-1]["measured_at"]),
                  meal_time=readable(report["original_information"]["meal_captured_at"]),
                  current_label="演示血糖读数（非实测）" if example else "最近记录的血糖",
                  freshness="演示数值，并非患者实测结果" if example else ("近期提供的读数" if report["caregiver_action"]["fresh"] else "读数已过时或时间在未来，请重新测量"),
                  history_note=f"共 {len(history)} 个演示读数，并非患者测量结果" if example else f"共 {len(history)} 个提供的读数",
                  history_values="；".join(f"{readable(r['measured_at'])}：{r['value']:g} {r['unit']}" for r in history[-6:]),
                  food_source="模拟估算；尚未实现图像识别",
                  suggestions="请查看用餐照片，并核对实测血糖及测量时间。食物和血糖估算均为固定演示值，不代表患者的实际情况。请遵循既定照护方案，治疗问题请咨询医生。",
                  warning="这是原型演示。营养估算、当前血糖估算及未来预测均为模拟数据，与照片内容无关。所有区间仅用于演示，未经统计验证，不是有效的 90% 置信区间。请勿据此决定治疗。")
    for name in ("estimated_range", "forecast_range", "carbs_range", "sugar_range"):
        result[name] = result[name].replace(" to ", " 至 ")
    return result


def chart_labels(data):
    """Chart payload -> Chinese presentation in place; numbers and units are preserved."""
    data["font"] = "Microsoft YaHei"
    for tick in data["ticks"]:
        tick["label"] = datetime.fromtimestamp(tick["x"], timezone(timedelta(hours=8))).strftime("%m-%d\n%H:%M")
    data["reading_label"] = "演示历史读数" if data["reading_label"].startswith("DEMO") else "实测／最近读数"
    for item, label in zip(data["food"], ("总碳水化合物", "糖")):
        item["label"] = label
    data["translations"] = {
        "GLUCOSE HISTORY + CURRENT ESTIMATE + FORECAST": "血糖历史、当前估算与未来预测（模拟）",
        "NOW": "现在", "No measured history supplied": "未提供实测历史数据",
        "Estimate now: " + str(data["current_estimate"]["y"]): "当前估算：" + str(data["current_estimate"]["y"]),
        "Dashed: demo future forecast": "虚线：模拟未来血糖",
        "Shading / whisker: illustrative ranges (not validated)": "阴影／误差线：演示范围（未经验证）",
        "FOOD ESTIMATES - SIMULATED": "食物营养估算（模拟）",
        "Estimated grams and illustrative uncertainty ranges": "估算克数与演示范围",
        "Sugar is included in total carbohydrates; do not add the two bars.": "糖已包含在总碳水化合物中，请勿将两者相加。",
    }
    return data


def text_body(report, values):
    """Report + Chinese display values -> readable UTF-8 text alternative with advice first."""
    measured = report["original_information"]["glucose"]
    reading = f"{measured['value']:g} {measured['unit']}（{measured['measured_at']}）" if measured else "未提供实测血糖"
    return (f"用餐与血糖报告【模拟演示】\n患者：{values['patient']}\n生成时间：{values['prepared']}\n\n"
            f"照护建议：{values['action_title']}\n糖分摄入：{values['sugar_action']}\n医疗帮助：{values['doctor_action']}\n{values['action_detail']}\n\n"
            f"当前血糖估算（模拟）：{values['estimated_current']}；演示范围：{values['estimated_range']}\n实测血糖：{reading}\n"
            f"30 分钟后预测（模拟）：{values['forecast_value']}；演示范围：{values['forecast_range']} mg/dL\n\n"
            f"总碳水化合物（模拟）：{values['carbs_value']} g（{values['carbs_range']} g）\n糖（模拟）：{values['sugar_value']} g（{values['sugar_range']} g）\n糖已包含在总碳水化合物中。\n\n"
            f"{values['suggestions']}\n\n{values['warning']}\n不提供胰岛素用药时间或剂量建议。邮件不是紧急监护渠道。\n用餐照片和图表见邮件内嵌图片。\n")
