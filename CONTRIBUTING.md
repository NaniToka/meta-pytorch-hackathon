# Contributing to Email Triage OpenEnv

Thank you for your interest in contributing!

## Adding New Email Categories

Edit `env/data.py` and add new subject/sender/body lists.

## Adding New Tasks

Edit `env/tasks.py` and add a new task definition:
```python
"task4": {
    "id":               "task4",
    "name":             "Your Task Name",
    "difficulty":       "expert",
    "description":      "Task description here.",
    "email_count":      50,
    "requires_actions": True,
    "requires_summary": True,
    "seed":             4,
    "tricky":           True,
}
```

## Running Tests
```bash
python -c "from env.data import generate_emails; print(generate_emails(10, seed=1))"
python inference.py
```

## API Testing
```bash
curl http://localhost:7860/health
curl -X POST http://localhost:7860/reset -H "Content-Type: application/json" -d '{"task_id":"task1"}'
```
