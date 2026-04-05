# env/graders.py

def grade_labels(emails: list, agent_labels: dict) -> float:
    """
    Score how many email labels the agent got correct.
    Example: 7 correct out of 10 = 0.7
    """
    if not emails:
        return 0.0
    correct = sum(
        1 for e in emails
        if agent_labels.get(e["id"], "").lower().strip() == e["true_label"]
    )
    return round(correct / len(emails), 4)


def grade_actions(emails: list, agent_actions: dict) -> float:
    """
    Score how many actions the agent got correct.
    Example: 6 correct out of 10 = 0.6
    """
    if not emails:
        return 0.0
    correct = sum(
        1 for e in emails
        if agent_actions.get(e["id"], "").lower().strip() == e["true_action"]
    )
    return round(correct / len(emails), 4)


def grade_summary(emails: list, agent_summary: str) -> float:
    """
    Score the summary by checking if urgent email subjects are mentioned.
    Example: 2 out of 3 urgent subjects mentioned = 0.666
    """
    urgent_emails = [e for e in emails if e["true_label"] == "urgent"]
    if not urgent_emails:
        return 1.0
    if not agent_summary or not agent_summary.strip():
        return 0.0
    hits = sum(
        1 for e in urgent_emails
        if e["subject"][:15].lower() in agent_summary.lower()
    )
    return round(hits / len(urgent_emails), 4)


def compute_reward(task_id: str, emails: list, agent_response: dict) -> dict:
    """
    Main reward function.

    task1: only labels matter         → score = label accuracy
    task2: labels + actions matter    → score = 50% labels + 50% actions
    task3: labels + actions + summary → score = 40% labels + 40% actions + 20% summary

    Always returns partial credit — never just 0 or 1.
    """
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
