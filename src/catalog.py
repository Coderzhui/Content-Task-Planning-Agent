"""素材/工具目录加载与查询。"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


class Catalog:
    def __init__(self, materials, tools):
        self._materials = {m["id"]: m for m in materials}
        self._tools = {t["id"]: t for t in tools}

    def get_material(self, material_id):
        if material_id not in self._materials:
            raise KeyError(material_id)
        return self._materials[material_id]

    def get_tool(self, tool_id):
        if tool_id not in self._tools:
            raise KeyError(tool_id)
        return self._tools[tool_id]

    def list_materials(self):
        return list(self._materials.values())

    def list_tools(self):
        return list(self._tools.values())

    @classmethod
    def load(cls, path=None):
        path = Path(path) if path else DATA_DIR / "catalog.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(data.get("materials", []), data.get("tools", []))
