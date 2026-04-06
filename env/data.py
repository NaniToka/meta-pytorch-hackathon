import random

# ── Easy emails (obvious) ─────────────────────────────────────────────────────

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

# ── Tricky emails (look urgent but are spam) ──────────────────────────────────

TRICKY_SPAM_SUBJECTS = [
    "URGENT: Your password expires today",
    "Action required: Verify your account NOW",
    "Critical: Your payment method failed",
    "Important: Security alert for your account",
    "Immediate action needed: Account suspended",
    "WARNING: Unusual activity detected",
]

TRICKY_SPAM_SENDERS = [
    "security@accounts-google.ru",
    "noreply@paypal-security.net",
    "alert@amazon-accounts.biz",
    "support@microsoft-verify.co",
    "admin@apple-id-verify.xyz",
    "security@bank-alert.net",
]

TRICKY_SPAM_BODIES = [
    "We detected unusual activity. Click here immediately to secure your account or it will be locked.",
    "Your subscription has expired. Renew now to avoid losing access to your premium benefits.",
    "We noticed a sign-in attempt from an unknown device. Verify your identity to continue.",
    "Your payment of $299.99 was declined. Update your billing information immediately.",
]

# ── Senders ───────────────────────────────────────────────────────────────────

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

URGENT_BODIES = [
    "This is a critical issue that requires your immediate attention. Please respond as soon as possible.",
    "We have detected a serious problem that needs to be resolved urgently. Please act now.",
    "Immediate action required. This cannot wait. Please respond within the hour.",
    "This is time-sensitive. The team is blocked until this is resolved. Need your input now.",
]

NORMAL_BODIES = [
    "Just wanted to keep you in the loop. No rush on this one, review when you get a chance.",
    "Please find the attached information for your review. Let me know if you have questions.",
    "Following up on our last conversation. Happy to discuss further at your convenience.",
    "Sharing this update with the team. No action needed unless you have concerns.",
]

SPAM_BODIES = [
    "Click the link below to claim your reward. Limited time offer! Don't miss out!!!",
    "You have been specially selected. Act now before this offer expires tonight!!!",
    "Congratulations! You are our lucky winner. Send your details to claim your prize.",
    "Make money from home guaranteed. Thousands already earning. Join now for free!!!",
]

def generate_emails(count: int, seed: int = 42, tricky: bool = False) -> list:
    """
    Generate emails for agent to classify.

    Args:
        count:  Number of emails
        seed:   Random seed for reproducibility
        tricky: If True, mix in phishing/tricky spam emails
    """
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
        # For task3 (tricky=True), replace some spam with tricky spam
        if tricky and label == "spam" and random.random() < 0.4:
            emails.append({
                "id":          f"email_{i}",
                "subject":     random.choice(TRICKY_SPAM_SUBJECTS),
                "sender":      random.choice(TRICKY_SPAM_SENDERS),
                "body":        random.choice(TRICKY_SPAM_BODIES),
                "true_label":  "spam",
                "true_action": "delete",
            })
        else:
            bodies = URGENT_BODIES if label == "urgent" else \
                     NORMAL_BODIES if label == "normal" else SPAM_BODIES
            emails.append({
                "id":          f"email_{i}",
                "subject":     random.choice(
                                   URGENT_SUBJECTS if label == "urgent" else
                                   NORMAL_SUBJECTS if label == "normal" else
                                   SPAM_SUBJECTS
                               ),
                "sender":      random.choice(SENDERS[label]),
                "body":        random.choice(bodies),
                "true_label":  label,
                "true_action": CORRECT_ACTIONS[label],
            })

    return emails
