"""方案保存工具（幂等：确定性 plan_id）。"""
import hashlib
import json


def save_plan(args, catalog):
    plan = args.get("plan") or {}
    key = json.dumps({
        "topic": plan.get("topic"),
        "material_ids": plan.get("material_ids"),
        "tool_ids": plan.get("tool_ids"),
    }, sort_keys=True, ensure_ascii=False)
    plan_id = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
    return {"ok": True, "data": {"plan_id": plan_id, "saved": True, "plan": plan}, "error": None, "retryable": None}