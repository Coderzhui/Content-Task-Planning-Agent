"""工具注册与统一执行（含失败注入与调用计数）。"""
from . import search, script, estimate, save

TOOLS = {
    "search_material": search.search_material,
    "generate_script": script.generate_script,
    "estimate_cost": estimate.estimate_cost,
    "save_plan": save.save_plan,
}


def execute(tool_name, args, catalog, fail_injections, call_counts):
    if tool_name not in TOOLS:
        return {"ok": False, "data": None, "error": f"unknown tool: {tool_name}", "retryable": False}

    call_counts[tool_name] = call_counts.get(tool_name, 0) + 1
    n = call_counts[tool_name]

    for inj in fail_injections:
        if inj.get("tool") == tool_name and inj.get("on_call", 1) == n:
            return {
                "ok": False,
                "data": None,
                "error": inj.get("error", f"injected {tool_name} failure"),
                "retryable": inj.get("retryable", True),
            }

    return TOOLS[tool_name](args, catalog)