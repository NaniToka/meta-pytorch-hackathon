import random

URGENT_SUBJECTS = [
    "URGENT: Server is down",
    "Critical bug in production",
    "Payment failed - action needed",
    "Legal notice received",
    "Security breach detected",
    "Board meeting moved to TODAY",
    "CRITICAL: Database corrupted",
    "Your account will be suspended",
]

NORMAL_SUBJECTS = [
    "Team lunch this Friday",
    "Q3 report attached",
    "Feedback on your pull request",
    "Meeting notes from Monday",
    "Project status update",
    "Welcome to the team!",
    "New policy update from HR",
    "Reminder: performance review next week",
]

SPAM_SUBJECTS = [
    "You WON $1,000,000!!!",
    "FREE iPhone - click here NOW",
    "Lose 20kg in 1 week guaranteed",
    "Hot singles in your area",
    "Nigerian prince needs your help",
    "Claim your prize before midnight",
    "Congratulations! You are selected",
    "Make $5000 from home daily",
]

SENDERS = {
    "urgent": ["cto@company.com", "legal@company.com", "ceo@company.com", "security@company.com"],
    "normal": ["colleague@company.com", "hr@company.com", "manager@company.com", "team@company.com"],
    "spam":   ["noreply@win-prizes.ru", "deals@free-stuff.biz", "prince@nigeria.net", "offers@click-here.xyz"],
}

CORRECT_ACTIONS = {
    "urgent": "reply",
    "normal": "archive",
    "spam":   "delete",
}

BODIES = {
    "urgent": "This is a critical issue that requires your immediate attention. Please respond as soon as possible.",
    "normal": "Just wanted to keep you in the loop. No rush on this one, but please review when you get a chance.",
    "spam":   "Click the link below to claim your reward. Limited time offer! Don't miss out!!!",
}

def generate_emails(count: int, seed: int = 42) -> list:
    random.seed(seed)
    each = count // 3
    labels = (
        ["urgent"] * each +
        ["normal"] * each +
        ["spam"]   * (count - 2 * each)
    )
    random.shuffle(labels)
    emails = []
    for i, label in enumerate(labels):
        emails.append({
            "id":          f"email_{i}",
            "subject":     random.choice(
                               URGENT_SUBJECTS if label == "urgent" else
                               NORMAL_SUBJECTS if label == "normal" else
                               SPAM_SUBJECTS
                           ),
            "sender":      random.choice(SENDERS[label]),
            "body":        BODIES[label],
            "true_label":  label,
            "true_action": CORRECT_ACTIONS[label],
        })
    return emails
