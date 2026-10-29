"""预设计划骨架与工具 schema。"""

DEFAULT_TOOL_IDS = ["tool_script", "tool_design"]

TOOL_SCHEMAS = [
    {"name": "search_material", "description": "检索可用素材，返回素材列表（含 id/name/cost/hours）",
     "params": {"topic": "string"}},
    {"name": "generate_script", "description": "为指定素材生成内容脚本",
     "params": {"topic": "string", "material_ids": ["string"]}},
    {"name": "estimate_cost", "description": "估算费用与耗时；tool_ids 应填 ['tool_script','tool_design']",
     "params": {"material_ids": ["string"], "tool_ids": ["string"], "budget": "number", "deadline_hours": "number"}},
    {"name": "save_plan", "description": "保存方案；plan 需含 topic / material_ids(字符串数组) / tool_ids(字符串数组) / total_cost / total_hours",
     "params": {"plan": "object"}},
]
