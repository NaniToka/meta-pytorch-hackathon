from env.data import generate_emails

TASKS = {
    "task1": {
        "id":               "task1",
        "name":             "Email Labeling (Easy)",
        "description":      "You have 10 emails. Label each one as: urgent, normal, or spam.",
        "email_count":      10,
        "requires_actions": False,
        "requires_summary": False,
        "seed":             1,
        "tricky":           False,
    },
    "task2": {
        "id":               "task2",
        "name":             "Email Triage (Medium)",
        "description":      "You have 20 emails. Label each one AND decide the action: reply, archive, or delete.",
        "email_count":      20,
        "requires_actions": True,
        "requires_summary": False,
        "seed":             2,
        "tricky":           False,
    },
    "task3": {
        "id":               "task3",
        "name":             "Full Inbox Management (Hard)",
        "description":      "You have 30 emails including tricky phishing attempts. Label each one, decide the action, AND write a short summary of all urgent emails. Watch out for emails that look urgent but are actually spam!",
        "email_count":      30,
        "requires_actions": True,
        "requires_summary": True,
        "seed":             3,
        "tricky":           True,
    },
}

def get_task_emails(task_id: str) -> list:
    task = TASKS[task_id]
    return generate_emails(
        task["email_count"],
        seed=task["seed"],
        tricky=task.get("tricky", False)
    )
