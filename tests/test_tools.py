import unittest

from src.catalog import Catalog
from src.tools import registry

CATALOG = Catalog(
    [
        {"id": "mat_premium", "name": "高端定制素材", "cost": 9, "hours": 6},
        {"id": "mat_standard", "name": "标准素材", "cost": 5, "hours": 4},
    ],
    [
        {"id": "tool_script", "name": "脚本生成", "cost": 1, "hours": 1},
        {"id": "tool_design", "name": "视觉设计", "cost": 2, "hours": 2},
    ],
)


class ToolTests(unittest.TestCase):
    def test_search(self):
        r = registry.execute("search_material", {"topic": "t"}, CATALOG, [], {})
        self.assertTrue(r["ok"])
        self.assertEqual(len(r["data"]["materials"]), 2)

    def test_estimate_premium_over_budget(self):
        r = registry.execute("estimate_cost", {
            "material_ids": ["mat_premium"], "tool_ids": ["tool_script", "tool_design"],
            "budget": 10, "deadline_hours": 20,
        }, CATALOG, [], {})
        self.assertTrue(r["ok"])
        self.assertEqual(r["data"]["total_cost"], 12)
        self.assertTrue(r["data"]["over_budget"])

    def test_estimate_standard_within_budget(self):
        r = registry.execute("estimate_cost", {
            "material_ids": ["mat_standard"], "tool_ids": ["tool_script", "tool_design"],
            "budget": 10, "deadline_hours": 20,
        }, CATALOG, [], {})
        self.assertEqual(r["data"]["total_cost"], 8)
        self.assertFalse(r["data"]["over_budget"])

    def test_estimate_unknown_id(self):
        r = registry.execute("estimate_cost", {
            "material_ids": ["nope"], "tool_ids": ["tool_script"],
            "budget": 10, "deadline_hours": 20,
        }, CATALOG, [], {})
        self.assertFalse(r["ok"])
        self.assertFalse(r["retryable"])

    def test_save_idempotent(self):
        plan = {"topic": "t", "material_ids": ["mat_standard"], "tool_ids": ["tool_script", "tool_design"]}
        r1 = registry.execute("save_plan", {"plan": plan}, CATALOG, [], {})
        r2 = registry.execute("save_plan", {"plan": plan}, CATALOG, [], {})
        self.assertEqual(r1["data"]["plan_id"], r2["data"]["plan_id"])

    def test_injection_failure_then_success(self):
        inj = [{"tool": "generate_script", "on_call": 1, "retryable": True}]
        counts = {}
        r1 = registry.execute("generate_script", {"topic": "t", "material_ids": ["mat_premium"]}, CATALOG, inj, counts)
        r2 = registry.execute("generate_script", {"topic": "t", "material_ids": ["mat_premium"]}, CATALOG, inj, counts)
        self.assertFalse(r1["ok"])
        self.assertTrue(r1["retryable"])
        self.assertTrue(r2["ok"])


if __name__ == "__main__":
    unittest.main()