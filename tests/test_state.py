import json
import os
import tempfile
import unittest

from src.state import State, save_checkpoint, load_checkpoint
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

    def test_checkpoint_roundtrip(self):
        s = State({"topic": "t", "budget": 10, "deadline_hours": 20, "fail_injections": []})
        s.record(Action("tool", "estimate_cost", {"material_ids": ["mat_standard"]}),
                 {"ok": True, "data": {"total_cost": 8, "total_hours": 7}, "error": None, "retryable": None})
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            path = f.name
        try:
            save_checkpoint(path, s.to_dict(), {"generate_script": 1})
            s2, cc = load_checkpoint(path)
        finally:
            os.unlink(path)
        self.assertEqual(s2.step_count, 1)
        self.assertEqual(s2.steps[0]["result"]["total_cost"], 8)
        self.assertEqual(cc["generate_script"], 1)

    def test_load_checkpoint_missing_state(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump({"call_counts": {}}, f)
            path = f.name
        try:
            with self.assertRaises(ValueError):
                load_checkpoint(path)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()