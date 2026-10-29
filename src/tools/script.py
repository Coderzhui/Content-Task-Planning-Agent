"""脚本生成工具（模板占位）。"""


def generate_script(args, catalog):
    topic = args.get("topic", "")
    material_ids = args.get("material_ids") or []
    if not material_ids:
        return {"ok": False, "data": None, "error": "material_ids is required", "retryable": False}
    try:
        names = "、".join(catalog.get_material(mid)["name"] for mid in material_ids)
    except KeyError as exc:
        return {"ok": False, "data": None, "error": f"unknown material: {exc}", "retryable": False}
    script = f"围绕「{topic}」的内容活动脚本，使用素材：{names}"
    return {"ok": True, "data": {"script": script, "material_ids": material_ids}, "error": None, "retryable": None}