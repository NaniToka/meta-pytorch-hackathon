import unittest
from env.graders import _clamp_score, compute_reward

class TestScoreRange(unittest.TestCase):
    def test_clamp_range(self):
        # Test values that should be clamped
        self.assertEqual(_clamp_score(1.0), 0.999)
        self.assertEqual(_clamp_score(1.1), 0.999)
        self.assertEqual(_clamp_score(0.0), 0.001)
        self.assertEqual(_clamp_score(-0.1), 0.001)
        self.assertEqual(_clamp_score(0.5), 0.5)
        
    def test_compute_reward_range(self):
        # Mock emails and response to get perfect score
        emails = [{"id": "1", "true_label": "urgent", "true_action": "reply", "subject": "Test"}]
        agent_response = {"labels": {"1": "urgent"}, "actions": {"1": "reply"}, "summary": "Test"}
        
        for task_id in ["task1", "task2", "task3"]:
            reward = compute_reward(task_id, emails, agent_response)
            self.assertTrue(0.0 < reward["value"] < 1.0, f"Value {reward['value']} out of range for {task_id}")
            self.assertTrue(0.0 < reward["label_score"] < 1.0)
            self.assertTrue(0.0 < reward["action_score"] < 1.0)
            self.assertTrue(0.0 < reward["summary_score"] < 1.0)
            
            # Specifically check they are not 1.0 or 0.0
            self.assertNotEqual(reward["value"], 1.0)
            self.assertNotEqual(reward["value"], 0.0)

if __name__ == "__main__":
    unittest.main()
