"""素材检索工具。"""


def search_material(args, catalog):
    # 合成数据：topic 仅透传，返回全部可选素材（含分档费用/耗时）。
    return {"ok": True, "data": {"materials": catalog.list_materials()}, "error": None, "retryable": None}