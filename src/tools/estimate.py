"""成本估算工具（费用 + 耗时，显式传 budget / deadline_hours）。"""


def estimate_cost(args, catalog):
    material_ids = args.get("material_ids") or []
    tool_ids = args.get("tool_ids") or []
    budget = args.get("budget")
    deadline_hours = args.get("deadline_hours")

    try:
        mats = [catalog.get_material(mid) for mid in material_ids]
        tools = [catalog.get_tool(tid) for tid in tool_ids]
    except KeyError as exc:
        return {"ok": False, "data": None, "error": f"unknown id: {exc}", "retryable": False}

    total_cost = sum(m["cost"] for m in mats) + sum(t["cost"] for t in tools)
    total_hours = sum(m["hours"] for m in mats) + sum(t["hours"] for t in tools)

    return {"ok": True, "data": {
        "total_cost": total_cost,
        "total_hours": total_hours,
        "over_budget": total_cost > budget,
        "over_deadline": total_hours > deadline_hours,
    }, "error": None, "retryable": None}