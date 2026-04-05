# env/email_env.py
from pydantic import BaseModel
from env.tasks import TASKS, get_task_emails
from env.graders import compute_reward

# ── Typed Models (required by OpenEnv spec) ──────────────────────────────────

class EmailAction(BaseModel):
    task_id: str
    labels:  dict  # {email_id: "urgent" | "normal" | "spam"}
    actions: dict = {}  # {email_id: "reply" | "archive" | "delete"}
    summary: str  = ""  # only needed for task3

class EmailObservation(BaseModel):
    task_id:     str
    task_name:   str
    description: str
    emails:      list  # inbox shown to agent (no true labels)
    step:        int
    done:        bool

class EmailReward(BaseModel):
    value:         float  # final score 0.0 - 1.0
    label_score:   float
    action_score:  float
    summary_score: float

# ── Main Environment Class ────────────────────────────────────────────────────

class EmailTriageEnv:

    def __init__(self, task_id: str = "task1"):
        assert task_id in TASKS, f"Unknown task '{task_id}'. Choose: task1, task2, task3"
        self.task_id  = task_id
        self._emails  = []
        self._step    = 0
        self._done    = False

    def _hide_answers(self, emails: list) -> list:
        """Remove true_label and true_action before showing emails to agent"""
        return [
            {k: v for k, v in e.items() if k not in ("true_label", "true_action")}
            for e in emails
        ]

    def reset(self) -> EmailObservation:
        """Start a fresh episode — returns the inbox to the agent"""
        self._emails = get_task_emails(self.task_id)
        self._step   = 0
        self._done   = False
        task         = TASKS[self.task_id]

        return EmailObservation(
            task_id     = self.task_id,
            task_name   = task["name"],
            description = task["description"],
            emails      = self._hide_answers(self._emails),
            step        = self._step,
            done        = False,
        )

    def step(self, action: EmailAction):
        """
        Agent submits its answers.
        Returns: observation, reward, done, info
        """
        if self._done:
            raise RuntimeError("Episode already done. Call reset() first.")

        self._step += 1
        self._done  = True  # single-turn task — one shot per episode

        # Score the agent's response
        scores = compute_reward(
            self.task_id,
            self._emails,
            {
                "labels":  action.labels,
                "actions": action.actions,
                "summary": action.summary,
            }
        )

        task = TASKS[self.task_id]

        observation = EmailObservation(
            task_id     = self.task_id,
            task_name   = task["name"],
            description = task["description"],
            emails      = self._hide_answers(self._emails),
            step        = self._step,
            done        = True,
        )

        reward = EmailReward(
            value         = scores["value"],
            label_score   = scores["label_score"],
            action_score  = scores["action_score"],
            summary_score = scores["summary_score"],
        )

        info = {
            "task_id":     self.task_id,
            "steps":       self._step,
            "email_count": len(self._emails),
        }

        return observation, reward, True, info

    def state(self) -> dict:
        """Returns current state of the environment"""
        return {
            "task_id":     self.task_id,
            "step":        self._step,
            "done":        self._done,
            "email_count": len(self._emails),
        }
