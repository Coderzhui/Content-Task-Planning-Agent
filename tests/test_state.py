import unittest

from src.state import State
from src.models.base import Action


class StateTests(unittest.TestCase):
    def test_record_success_and_failed(self):
        s = State({"topic": "t", "budget": 10, "deadline_hours": 20, "fail_injections": []})
        s.record(Action("tool", "search_material", {"topic": "t"}),
                 {"ok": True, "data": {"materials": []}, "error": None, "retryable": None})
        s.record(Action("tool", "generate_script", {"topic": "t", "material_ids": ["mat_premium"]}),
                 {"ok": False, "data": None, "error": "boom", "retryable": True})
        self.assertEqual(len(s.steps), 2)
        self.assertEqual(s.steps[0]["status"], "success")
        self.assertEqual(s.steps[1]["status"], "failed")
        self.assertEqual(s.steps[1]["error"], "boom")

    def test_estimate_updates_step_cost(self):
        s = State({"topic": "t", "budget": 10, "deadline_hours": 20, "fail_injections": []})
        s.record(Action("tool", "estimate_cost", {"material_ids": ["mat_standard"]}),
                 {"ok": True, "data": {"total_cost": 8, "total_hours": 7}, "error": None, "retryable": None})
        self.assertEqual(s.steps[0]["cost"], 8)
        self.assertEqual(s.steps[0]["hours"], 7)

    def test_roundtrip(self):
        s = State({"topic": "t", "budget": 10, "deadline_hours": 20, "fail_injections": []})
        s.record(Action("tool", "estimate_cost", {"material_ids": ["mat_standard"]}),
                 {"ok": True, "data": {"total_cost": 8, "total_hours": 7}, "error": None, "retryable": None})
        s2 = State.from_dict(s.to_dict())
        self.assertEqual(s2.steps[0]["result"]["total_cost"], 8)
        self.assertEqual(s2.step_count, 1)


if __name__ == "__main__":
    unittest.main()