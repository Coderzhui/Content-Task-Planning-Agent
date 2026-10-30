import unittest

from src.catalog import Catalog
from src.agent import run_agent, summarize
from src.state import State
from src.models.base import Action, Model
from src.models.offline_mock import OfflineMockModel

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


def req(**kw):
    base = {"topic": "新品上线", "budget": 10, "deadline_hours": 20, "fail_injections": []}
    base.update(kw)
    return base


class AgentTests(unittest.TestCase):
    def test_normal_within_budget(self):
        r = run_agent(req(budget=15), OfflineMockModel(), CATALOG)
        self.assertEqual(r["status"], "completed")
        self.assertEqual(r["total_cost"], 12)
        self.assertEqual(r["saved_plan"]["material_ids"], ["mat_premium"])

    def test_budget_overrun_switches(self):
        r = run_agent(req(budget=10), OfflineMockModel(), CATALOG)
        self.assertEqual(r["status"], "completed")
        self.assertEqual(r["total_cost"], 8)
        self.assertEqual(r["saved_plan"]["material_ids"], ["mat_standard"])

    def test_over_deadline_switches(self):
        r = run_agent(req(budget=20, deadline_hours=8), OfflineMockModel(), CATALOG)
        self.assertEqual(r["status"], "completed")
        self.assertEqual(r["total_hours"], 7)
        self.assertEqual(r["saved_plan"]["material_ids"], ["mat_standard"])

    def test_tool_failure_retry_keeps_success(self):
        r = run_agent(req(budget=15, fail_injections=[{"tool": "generate_script", "on_call": 1, "retryable": True}]),
                      OfflineMockModel(), CATALOG)
        self.assertEqual(r["status"], "completed")
        # 检索成功被保留
        search_status = [s["status"] for s in r["plan"]["steps"] if s["tool"] == "search_material"]
        self.assertEqual(search_status, ["success"])
        # 存在一次失败步骤
        self.assertIn("failed", [s["status"] for s in r["plan"]["steps"]])

    def test_non_retryable_failure_stops(self):
        r = run_agent(req(budget=15, fail_injections=[{"tool": "generate_script", "on_call": 1, "retryable": False}]),
                      OfflineMockModel(), CATALOG)
        self.assertEqual(r["status"], "incomplete")
        self.assertEqual(r["reason"], "tool_error")

    def test_no_feasible_plan(self):
        r = run_agent(req(budget=5), OfflineMockModel(), CATALOG)
        self.assertEqual(r["status"], "incomplete")
        self.assertEqual(r["reason"], "no_feasible_plan")
        self.assertIsNone(r["saved_plan"])

    def test_step_limit(self):
        r = run_agent(req(budget=15), OfflineMockModel(), CATALOG, max_steps=2)
        self.assertEqual(r["status"], "incomplete")
        self.assertEqual(r["reason"], "step_limit_reached")

    def test_resume_skips_success_and_completes(self):
        s = State(req(budget=15))
        s.record(Action("tool", "search_material", {"topic": "新品上线"}),
                 {"ok": True, "data": {"materials": []}, "error": None, "retryable": None})
        s.record(Action("tool", "generate_script", {"topic": "新品上线", "material_ids": ["mat_premium"]}),
                 {"ok": True, "data": {"script": "x", "material_ids": ["mat_premium"]}, "error": None, "retryable": None})
        r = run_agent(req(budget=15), OfflineMockModel(), CATALOG, resume_state=s)
        self.assertEqual(r["status"], "completed")
        self.assertEqual(r["total_cost"], 12)
        self.assertEqual(r["saved_plan"]["material_ids"], ["mat_premium"])
        tools = [st["tool"] for st in r["plan"]["steps"]]
        self.assertEqual(tools.count("search_material"), 1)
        self.assertEqual(tools.count("generate_script"), 1)

    def test_summarize_hides_fail_injections(self):
        s = State(req(budget=15, fail_injections=[{"tool": "generate_script", "on_call": 1}]))
        obs = summarize(s)
        self.assertNotIn("fail_injections", obs["input"])
        self.assertEqual(sorted(obs["input"].keys()), ["budget", "deadline_hours", "topic"])

    def test_save_plan_missing_topic_no_crash(self):
        r = run_agent(req(budget=15), SavePlanNoTopicModel(), CATALOG)
        self.assertEqual(r["status"], "completed")
        self.assertEqual(r["saved_plan"]["topic"], "新品上线")


class SavePlanNoTopicModel(Model):
    def decide(self, observation, tools_schema):
        if not any(s["tool"] == "save_plan" for s in observation["steps"]):
            return Action("tool", "save_plan", {"plan": {
                "material_ids": ["mat_standard"],
                "tool_ids": ["tool_script", "tool_design"],
            }})
        return Action("stop", reason="done")


if __name__ == "__main__":
    unittest.main()