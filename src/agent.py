"""ReAct 引擎：循环、步数上限、观察构造、交付结果组装。"""
from .state import State
from .tools import registry
from .models.base import Action
from .models.offline_mock import OfflineMockModel
from .models.llm import LLMModel
from .planner import TOOL_SCHEMAS

MAX_STEPS = 12


def build_model(kind="offline_mock", **kwargs):
    if kind == "llm":
        return LLMModel(**kwargs)
    return OfflineMockModel(**kwargs)


def summarize(state):
    last = state.observations[-1] if state.observations else None
    return {"input": state.input, "steps": state.steps, "last": last}


def run_agent(request, model, catalog, max_steps=MAX_STEPS):
    state = State(request)
    call_counts = {}

    while state.step_count < max_steps:
        observation = summarize(state)
        try:
            action = model.decide(observation, TOOL_SCHEMAS)
        except Exception as exc:  # 真实 LLM 出错 -> 明确未完成
            state.status = "incomplete"
            state.reason = f"model_error: {exc}"
            return build_deliverable(state)

        if action.kind == "stop":
            if state.saved_plan:
                state.status = "completed"
                state.reason = None
            else:
                state.status = "incomplete"
                state.reason = action.reason or "stopped_without_saving"
            return build_deliverable(state)

        result = registry.execute(action.tool, action.args, catalog, request["fail_injections"], call_counts)
        state.record(action, result)

        if action.tool == "estimate_cost" and result["ok"]:
            state.total_cost = result["data"]["total_cost"]
            state.total_hours = result["data"]["total_hours"]
        if action.tool == "save_plan" and result["ok"]:
            data = result["data"]
            state.saved_plan = {
                "plan_id": data["plan_id"],
                "topic": data["plan"]["topic"],
                "material_ids": data["plan"]["material_ids"],
                "tool_ids": data["plan"]["tool_ids"],
                "total_cost": data["plan"]["total_cost"],
                "total_hours": data["plan"]["total_hours"],
            }

    state.status = "incomplete"
    state.reason = "step_limit_reached"
    return build_deliverable(state)


def build_deliverable(state):
    trace = [
        {"step": i, "action": obs["tool"], "args": obs["args"],
         "result_summary": _summary(obs), "decision": _decision(obs)}
        for i, obs in enumerate(state.observations, 1)
    ]
    return {
        "status": state.status,
        "topic": state.input["topic"],
        "budget": state.input["budget"],
        "deadline_hours": state.input["deadline_hours"],
        "plan": {"steps": state.steps},
        "tool_results": [
            {"tool": obs["tool"], "args": obs["args"], "ok": obs["ok"], "summary": _summary(obs)}
            for obs in state.observations
        ],
        "total_cost": state.total_cost,
        "total_hours": state.total_hours,
        "saved_plan": state.saved_plan,
        "reason": state.reason,
        "trace": trace,
    }


def _summary(obs):
    if obs["ok"]:
        d = obs["data"] or {}
        if "total_cost" in d:
            return {"total_cost": d["total_cost"], "total_hours": d["total_hours"],
                    "over_budget": d.get("over_budget"), "over_deadline": d.get("over_deadline")}
        if "plan_id" in d:
            return {"plan_id": d["plan_id"]}
        if "materials" in d:
            return {"material_ids": [m["id"] for m in d["materials"]]}
        if "script" in d:
            return {"script": d["script"], "material_ids": d["material_ids"]}
        return d
    return {"error": obs["error"], "retryable": obs["retryable"]}


def _decision(obs):
    if not obs["ok"]:
        return "工具失败，重试或停止"
    if obs["tool"] == "estimate_cost":
        d = obs["data"] or {}
        if d.get("over_budget") or d.get("over_deadline"):
            return "超预算/超截止，改选更便宜的素材"
        return "预算内，准备保存"
    if obs["tool"] == "save_plan":
        return "方案已保存"
    return "继续下一步"