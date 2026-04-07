def _clamp_score(x: float) -> float:
    eps = 1e-6
    return max(eps, min(float(x), 1.0 - eps))


def grade_labels(emails: list, agent_labels: dict) -> float:
    if not emails:
        return 0.5

    correct = sum(
        1
        for e in emails
        if str(agent_labels.get(e["id"], "")).strip().lower() == e["true_label"]
    )
    raw = correct / len(emails)
    return _clamp_score(raw)


def grade_actions(emails: list, agent_actions: dict) -> float:
    if not emails:
        return 0.5

    correct = sum(
        1
        for e in emails
        if str(agent_actions.get(e["id"], "")).strip().lower() == e["true_action"]
    )
    raw = correct / len(emails)
    return _clamp_score(raw)


def grade_summary(emails: list, agent_summary: str) -> float:
    urgent_emails = [e for e in emails if e["true_label"] == "urgent"]

    if not urgent_emails:
        return _clamp_score(0.999)

    if not agent_summary or not str(agent_summary).strip():
        return _clamp_score(0.001)

    summary_lower = str(agent_summary).lower()
    hits = 0

    for e in urgent_emails:
        words = [w for w in e["subject"].lower().split() if len(w) > 3]
        if any(w in summary_lower for w in words):
            hits += 1

    raw = hits / len(urgent_emails)
    return _clamp_score(raw)


def get_per_email_feedback(emails: list, agent_labels: dict, agent_actions: dict) -> list:
    feedback = []

    for e in emails:
        agent_label = str(agent_labels.get(e["id"], "")).strip().lower()
        agent_action = str(agent_actions.get(e["id"], "")).strip().lower()

        feedback.append({
            "id": e["id"],
            "label_correct": agent_label == e["true_label"],
            "action_correct": agent_action == e["true_action"],
            "true_label": e["true_label"],
            "true_action": e["true_action"],
            "your_label": agent_label,
            "your_action": agent_action,
        })

    return feedback


def compute_reward(task_id: str, emails: list, agent_response: dict) -> dict:
    labels = agent_response.get("labels", {}) or {}
    actions = agent_response.get("actions", {}) or {}
    summary = agent_response.get("summary", "") or ""

    label_score = grade_labels(emails, labels)
    action_score = grade_actions(emails, actions)
    summary_score = grade_summary(emails, summary)
    feedback = get_per_email_feedback(emails, labels, actions)

    if task_id == "task1":
        final = label_score
    elif task_id == "task2":
        final = 0.5 * label_score + 0.5 * action_score
    elif task_id == "task3":
        final = 0.4 * label_score + 0.4 * action_score + 0.2 * summary_score
    else:
        final = 0.5

    final = _clamp_score(final)

    return {
        "value": final,
        "label_score": _clamp_score(label_score),
        "action_score": _clamp_score(action_score),
        "summary_score": _clamp_score(summary_score),
        "feedback": feedback,
    }