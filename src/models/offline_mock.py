"""离线确定性 Mock 决策。

只验证引擎循环与状态机制，不构成真实 ReAct 决策证据；真实 ReAct 由 LLMModel 体现。
"""
import json

from .base import Model, Action


class OfflineMockModel(Model):
    def __init__(self, material_choices=None):
        self._choices = material_choices or ["mat_premium", "mat_standard"]
        self._idx = 0
        self._retried = set()

    def decide(self, observation, tools_schema):
        steps = observation["steps"]
        last = observation.get("last")
        inp = observation["input"]
        topic = inp["topic"]

        # 已保存 -> 完成
        if any(s["tool"] == "save_plan" and s["status"] == "success" for s in steps):
            return Action("stop", reason="completed")

        # 先检索
        if not any(s["tool"] == "search_material" for s in steps):
            return Action("tool", "search_material", {"topic": topic})

        # 失败处理：可重试且未重试过 -> 重试一次；否则停止
        if last and last.get("ok") is False:
            key = (last["tool"], json.dumps(last.get("args", {}), sort_keys=True, ensure_ascii=False))
            if last.get("retryable") and key not in self._retried:
                self._retried.add(key)
                return Action("tool", last["tool"], last["args"])
            return Action("stop", reason="tool_error")

        mat = self._choices[self._idx]

        # 为当前素材生成脚本
        if not self._has_success(steps, "generate_script", mat):
            return Action("tool", "generate_script", {"topic": topic, "material_ids": [mat]})

        # 为当前素材估算
        if not self._has_success(steps, "estimate_cost", mat):
            return Action("tool", "estimate_cost", {
                "material_ids": [mat],
                "tool_ids": ["tool_script", "tool_design"],
                "budget": inp["budget"],
                "deadline_hours": inp["deadline_hours"],
            })

        # 已估算 -> 判断是否超支
        est = self._last_success(steps, "estimate_cost", mat)
        data = est["result"] or {}
        if data.get("over_budget") or data.get("over_deadline"):
            if self._idx + 1 < len(self._choices):
                self._idx += 1
                nxt = self._choices[self._idx]
                return Action("tool", "generate_script", {"topic": topic, "material_ids": [nxt]})
            return Action("stop", reason="no_feasible_plan")

        # 预算内 -> 保存
        script = ""
        gen = self._last_success(steps, "generate_script", mat)
        if gen and gen["result"]:
            script = gen["result"].get("script", "")
        plan = {
            "topic": topic,
            "material_ids": [mat],
            "tool_ids": ["tool_script", "tool_design"],
            "script": script,
            "total_cost": data.get("total_cost"),
            "total_hours": data.get("total_hours"),
        }
        return Action("tool", "save_plan", {"plan": plan})

    def _has_success(self, steps, tool, material_id):
        return any(
            s["tool"] == tool and s["status"] == "success"
            and material_id in (s["params"].get("material_ids") or [])
            for s in steps
        )

    def _last_success(self, steps, tool, material_id):
        for s in reversed(steps):
            if s["tool"] == tool and s["status"] == "success" and material_id in (s["params"].get("material_ids") or []):
                return s
        return None