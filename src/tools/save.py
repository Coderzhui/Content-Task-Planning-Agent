"""方案保存工具（幂等：确定性 plan_id）。"""
import hashlib
import json

from ..planner import DEFAULT_TOOL_IDS


def _normalize_plan(plan):
    p = dict(plan or {})
    if not p.get("material_ids") and p.get("materials"):
        p["material_ids"] = [
            m["id"] for m in p["materials"] if isinstance(m, dict) and m.get("id")
        ]
    if not p.get("tool_ids"):
        p["tool_ids"] = list(DEFAULT_TOOL_IDS)
    return p


def save_plan(args, catalog):
    plan = _normalize_plan(args.get("plan"))
    key = json.dumps({
        "topic": plan.get("topic"),
        "material_ids": plan.get("material_ids"),
        "tool_ids": plan.get("tool_ids"),
    }, sort_keys=True, ensure_ascii=False)
    plan_id = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
    return {"ok": True, "data": {"plan_id": plan_id, "saved": True, "plan": plan}, "error": None, "retryable": None}