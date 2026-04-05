def grade_labels(emails: list, agent_labels: dict) -> float:
    if not emails:
        return 0.0
    correct = sum(
        1 for e in emails
        if agent_labels.get(e["id"], "").lower().strip() == e["true_label"]
    )
    return round(correct / len(emails), 4)


def grade_actions(emails: list, agent_actions: dict) -> float:
    if not emails:
        return 0.0
    correct = sum(
        1 for e in emails
        if agent_actions.get(e["id"], "").lower().strip() == e["true_action"]
    )
    return round(correct / len(emails), 4)


def grade_summary(emails: list, agent_summary: str) -> float:
    urgent_emails = [e for e in emails if e["true_label"] == "urgent"]
    if not urgent_emails:
        return 1.0
    if not agent_summary or not agent_summary.strip():
        return 0.0
    summary_lower = agent_summary.lower()
    hits = 0
    for e in urgent_emails:
        words = [w for w in e["subject"].lower().split() if len(w) > 3]
        if any(w in summary_lower for w in words):
            hits += 1
    return round(hits / len(urgent_emails), 4)


def compute_reward(task_id: str, emails: list, agent_response: dict) -> dict:
    labels  = agent_response.get("labels",  {})
    actions = agent_response.get("actions", {})
    summary = agent_response.get("summary", "")

    label_score   = grade_labels(emails, labels)
    action_score  = grade_actions(emails, actions)
    summary_score = grade_summary(emails, summary)

    if task_id == "task1":
        final = label_score
    elif task_id == "task2":
        final = round(0.5 * label_score + 0.5 * action_score, 4)
    elif task_id == "task3":
        final = round(0.4 * label_score + 0.4 * action_score + 0.2 * summary_score, 4)
    else:
        final = 0.0

    return {
        "value":         final,
        "label_score":   label_score,
        "action_score":  action_score,
        "summary_score": summary_score,
    }
