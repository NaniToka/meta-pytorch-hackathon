# Email Triage OpenEnv

A real-world OpenEnv environment where AI agents learn to manage email inboxes.

## Environment Description

Agents receive a batch of emails and must:
1. Label each email as `urgent`, `normal`, or `spam`
2. Decide an action: `reply`, `archive`, or `delete`
3. Write a summary of urgent emails (task3 only)

## Tasks

| Task | Difficulty | Emails | Description |
|------|-----------|--------|-------------|
| task1 | Easy | 10 | Label emails only |
| task2 | Medium | 20 | Label + action |
| task3 | Hard | 30 | Label + action + summary |

## Reward Function

- task1: label accuracy (0.0–1.0)
- task2: 50% label + 50% action accuracy
- task3: 40% label + 40% action + 20% summary quality

Partial credit on every step — never binary win/loss.

## Baseline Scores

| Task | Score |
|------|-------|
| task1 | 1.0 |
| task2 | 1.0 |
| task3 | 0.82 |
| Average | 0.94 |

Model: `meta-llama/Llama-3.1-8B-Instruct`

## Setup
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

## API Endpoints

- `POST /reset` — Start episode `{"task_id": "task1"}`
- `POST /step`  — Submit answers `{"task_id": "task1", "labels": {...}, "actions": {...}}`
- `GET  /state` — Current state
- `GET  /tasks` — List all tasks
- `GET  /health` — Health check

## Run Baseline Agent
```bash
export HF_TOKEN=your_token_here
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
export ENV_URL=http://localhost:7860
python inference.py
```

## Action Space
```json
{
  "task_id": "task1",
  "labels":  {"email_0": "urgent", "email_1": "spam"},
  "actions": {"email_0": "reply",  "email_1": "delete"},
  "summary": "Optional summary of urgent emails"
}
```

## Observation Space
```json
{
  "task_id": "task1",
  "task_name": "Email Labeling (Easy)",
  "description": "...",
  "emails": [{"id": "email_0", "subject": "...", "sender": "...", "body": "..."}],
  "step": 0,
  "done": false
}
```
