---
title: Meta Pytorch Hackathon
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
port: 7860
---

# 📧 Email Triage OpenEnv

> A real-world reinforcement learning environment where AI agents learn to manage email inboxes — built for the Meta PyTorch OpenEnv Hackathon.

## 🎯 What Is This?

Every company on Earth has the same problem — too many emails, too little time. This OpenEnv environment trains AI agents to:

1. **Label** emails as `urgent`, `normal`, or `spam`
2. **Decide actions** — `reply`, `archive`, or `delete`
3. **Summarize** urgent emails for human review
4. **Detect phishing** — tricky spam that looks urgent!

## 🎮 Live Demo

👉 **[Try it yourself here](https://tokanani786-meta-pytorch-hackathon.hf.space)**

- 🎮 Label real emails and see your score instantly
- ✅❌ Green/red feedback on every single email
- 🏆 Compete on the leaderboard
- ⚡ Test API endpoints live in the browser

## 📊 Baseline Scores

| Task | Difficulty | Emails | Score | Notes |
|------|-----------|--------|-------|-------|
| task1 | 🟢 Easy | 10 | **1.0** | Pure classification |
| task2 | 🟡 Medium | 20 | **1.0** | Label + action |
| task3 | 🔴 Hard | 30 | **0.79** | Includes tricky phishing! |
| **Average** | | | **0.93** | |

Model: `meta-llama/Llama-3.1-8B-Instruct`

## 🏗️ Environment Design

### Observation Space
```json
{
  "task_id": "task1",
  "task_name": "Email Labeling (Easy)",
  "description": "You have 10 emails. Label each one.",
  "emails": [
    {
      "id": "email_0",
      "subject": "URGENT: Server is down",
      "sender": "cto@company.com",
      "body": "This is a critical issue..."
    }
  ],
  "step": 0,
  "done": false
}
```

### Action Space
```json
{
  "task_id": "task1",
  "labels":  {"email_0": "urgent", "email_1": "spam"},
  "actions": {"email_0": "reply",  "email_1": "delete"},
  "summary": "Urgent: server down, database corrupted."
}
```

### Reward Response
```json
{
  "reward": {
    "value": 0.9,
    "label_score": 0.9,
    "action_score": 0.9,
    "summary_score": 0.6,
    "feedback": [
      {
        "id": "email_0",
        "label_correct": true,
        "action_correct": true,
        "true_label": "urgent",
        "true_action": "reply",
        "your_label": "urgent",
        "your_action": "reply"
      }
    ]
  }
}
```

### Reward Function

| Task | Formula |
|------|---------|
| task1 | `label_accuracy` |
| task2 | `0.5 × label_accuracy + 0.5 × action_accuracy` |
| task3 | `0.4 × labels + 0.4 × actions + 0.2 × summary_quality` |

✅ **Partial credit on every email — never binary win/loss**
✅ **Per-email feedback showing exactly what was right/wrong**

## ⚠️ Tricky Phishing Emails (Task 3)

Task 3 includes phishing emails that **look urgent but are spam:**
