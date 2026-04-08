import unittest
from env.graders import (
    _clamp_score,
    grade_labels,
    grade_actions,
    grade_summary,
    get_per_email_feedback,
    compute_reward,
)

class TestGraders(unittest.TestCase):

    def test_clamp_score(self):
        self.assertAlmostEqual(_clamp_score(0.5), 0.5)
        self.assertAlmostEqual(_clamp_score(-1.0), 1e-6)
        self.assertAlmostEqual(_clamp_score(2.0), 1.0 - 1e-6)
        self.assertAlmostEqual(_clamp_score(0.0), 1e-6)
        self.assertAlmostEqual(_clamp_score(1.0), 1.0 - 1e-6)

    def test_grade_labels(self):
        emails = [
            {"id": "1", "true_label": "urgent"},
            {"id": "2", "true_label": "normal"},
        ]
        # All correct
        agent_labels = {"1": "urgent", "2": "normal"}
        self.assertAlmostEqual(grade_labels(emails, agent_labels), 1.0 - 1e-6)
        
        # Some correct (case and space test)
        agent_labels = {"1": " URgent ", "2": "wrong"}
        self.assertAlmostEqual(grade_labels(emails, agent_labels), 0.5)
        
        # None correct
        agent_labels = {"1": "x", "2": "y"}
        self.assertAlmostEqual(grade_labels(emails, agent_labels), 1e-6)

        # Empty emails
        self.assertEqual(grade_labels([], {}), 0.5)

    def test_grade_actions(self):
        emails = [
            {"id": "1", "true_action": "reply"},
            {"id": "2", "true_action": "delete"},
        ]
        # All correct
        agent_actions = {"1": "reply", "2": "delete"}
        self.assertAlmostEqual(grade_actions(emails, agent_actions), 1.0 - 1e-6)
        
        # Some correct
        agent_actions = {"1": "reply", "2": "forward"}
        self.assertAlmostEqual(grade_actions(emails, agent_actions), 0.5)
        
        # None correct
        agent_actions = {"1": "x", "2": "y"}
        self.assertAlmostEqual(grade_actions(emails, agent_actions), 1e-6)

        # Empty emails
        self.assertEqual(grade_actions([], {}), 0.5)

    def test_grade_summary(self):
        emails = [
            {"id": "1", "true_label": "urgent", "subject": "Meeting with CEO about Budget"},
            {"id": "2", "true_label": "normal", "subject": "Lunch menu"},
        ]
        
        # Hits: words > 3 chars (Meeting, about, Budget)
        # Match "Meeting"
        self.assertAlmostEqual(grade_summary(emails, "Meeting tomorrow"), 1.0 - 1e-6)
        
        # Match "Budget" (case insensitive)
        self.assertAlmostEqual(grade_summary(emails, "check the budget"), 1.0 - 1e-6)
        
        # No hits
        self.assertAlmostEqual(grade_summary(emails, "hello world"), 1e-6)
        
        # Empty summary
        self.assertAlmostEqual(grade_summary(emails, ""), 0.001)
        
        # No urgent emails
        no_urgent = [{"id": "2", "true_label": "normal", "subject": "Lunch menu"}]
        self.assertAlmostEqual(grade_summary(no_urgent, "anything"), 0.999)

    def test_get_per_email_feedback(self):
        emails = [
            {"id": "1", "true_label": "urgent", "true_action": "reply"},
        ]
        agent_labels = {"1": "urgent"}
        agent_actions = {"1": "delete"}
        
        feedback = get_per_email_feedback(emails, agent_labels, agent_actions)
        self.assertEqual(len(feedback), 1)
        self.assertTrue(feedback[0]["label_correct"])
        self.assertFalse(feedback[0]["action_correct"])
        self.assertEqual(feedback[0]["true_label"], "urgent")
        self.assertEqual(feedback[0]["your_action"], "delete")

    def test_compute_reward(self):
        emails = [
            {"id": "1", "true_label": "urgent", "true_action": "reply", "subject": "Urgent Meeting"},
        ]
        agent_response = {
            "labels": {"1": "urgent"},
            "actions": {"1": "reply"},
            "summary": "Meeting"
        }
        
        # Task 1: label score only
        reward1 = compute_reward("task1", emails, agent_response)
        self.assertAlmostEqual(reward1["value"], 1.0 - 1e-6)
        
        # Task 2: 0.5 label + 0.5 action
        reward2 = compute_reward("task2", emails, agent_response)
        self.assertAlmostEqual(reward2["value"], 1.0 - 1e-6)
        
        # Task 3: 0.4 label + 0.4 action + 0.2 summary
        reward3 = compute_reward("task3", emails, agent_response)
        self.assertAlmostEqual(reward3["value"], 1.0 - 1e-6)
        
        # Unknown task
        reward_unk = compute_reward("unknown", emails, agent_response)
        self.assertEqual(reward_unk["value"], 0.5)

if __name__ == "__main__":
    unittest.main()
