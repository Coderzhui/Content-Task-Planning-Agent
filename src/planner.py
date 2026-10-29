"""预设计划骨架与工具 schema。"""

DEFAULT_TOOL_IDS = ["tool_script", "tool_design"]

TOOL_SCHEMAS = [
    {"name": "search_material", "description": "检索可用素材", "params": {"topic": "string"}},
    {"name": "generate_script", "description": "生成内容脚本", "params": {"topic": "string", "material_ids": ["string"]}},
    {"name": "estimate_cost", "description": "估算费用与耗时",
     "params": {"material_ids": ["string"], "tool_ids": ["string"], "budget": "number", "deadline_hours": "number"}},
    {"name": "save_plan", "description": "保存方案", "params": {"plan": "object"}},
]
