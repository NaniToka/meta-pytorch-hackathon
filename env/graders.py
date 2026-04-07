def grade_labels(emails: list, agent_labels: dict) -> float:
    if not emails:
        return 0.5
    correct = sum(
        1 for e in emails
        if agent_labels.get(e["id"], "").lower().strip() == e["true_label"]
    )
    raw = correct / len(emails)
    # Must be strictly between 0 and 1 (not 0.0, not 1.0)
    return round(min(max(raw, 0.001), 0.999), 4)


def grade_actions(emails: list, agent_actions: dict) -> float:
    if not emails:
        return 0.5
    correct = sum(
        1 for e in emails
        if agent_actions.get(e["id"], "").lower().strip() == e["true_action"]
    )
    raw = correct / len(emails)
    return round(min(max(raw, 0.001), 0.999), 4)


def grade_summary(emails: list, agent_summary: str) -> float:
    urgent_emails = [e for e in emails if e["true_label"] == "urgent"]
    if not urgent_emails:
        return 0.999
    if not agent_summary or not agent_summary.strip():
        return 0.001
    summary_lower = agent_summary.lower()
    hits = 0
    for e in urgent_emails:
        words = [w for w in e["subject"].lower().split() if len(w) > 3]
        if any(w in summary_lower for w in words):
            hits += 1
    raw = hits / len(urgent_emails)
    return round(min(max(raw, 0.001), 0.999), 4)


def get_per_email_feedback(emails: list, agent_labels: dict, agent_actions: dict) -> list:
    feedback = []
    for e in emails:
        agent_label  = agent_labels.get(e["id"], "").lower().strip()
        agent_action = agent_actions.get(e["id"], "").lower().strip()
        feedback.append({
            "id":             e["id"],
            "label_correct":  agent_label  == e["true_label"],
            "action_correct": agent_action == e["true_action"],
            "true_label":     e["true_label"],
            "true_action":    e["true_action"],
            "your_label":     agent_label,
            "your_action":    agent_action,
        })
    return feedback


def compute_reward(task_id: str, emails: list, agent_response: dict) -> dict:
    labels  = agent_response.get("labels",  {})
    actions = agent_response.get("actions", {})
    summary = agent_response.get("summary", "")

    label_score   = grade_labels(emails, labels)
    action_score  = grade_actions(emails, actions)
    summary_score = grade_summary(emails, summary)
    feedback      = get_per_email_feedback(emails, labels, actions)

    if task_id == "task1":
        final = label_score
    elif task_id == "task2":
        final = round(0.5 * label_score + 0.5 * action_score, 4)
    elif task_id == "task3":
        final = round(0.4 * label_score + 0.4 * action_score + 0.2 * summary_score, 4)
    else:
        final = 0.5

    # Ensure final is strictly between 0 and 1
    final = round(min(max(final, 0.001), 0.999), 4)

    return {
        "value":         final,
        "label_score":   label_score,
        "action_score":  action_score,
        "summary_score": summary_score,
        "feedback":      feedback,
    }
