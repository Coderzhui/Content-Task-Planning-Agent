"""State/Step 数据模型与序列化（保留成功步骤结果、失败续跑基础）。"""
import json
from pathlib import Path


def new_step(step_id, name, tool, params):
    return {
        "id": step_id,
        "name": name,
        "tool": tool,
        "params": params,
        "status": "pending",
        "result": None,
        "cost": 0.0,
        "hours": 0.0,
        "error": None,
    }


class State:
    def __init__(self, request):
        self.input = request
        self.steps = []
        self.total_cost = 0.0
        self.total_hours = 0.0
        self.observations = []
        self.status = "running"
        self.reason = None
        self.step_count = 0
        self.saved_plan = None

    def record(self, action, result):
        """记录一次工具执行；成功/失败都保留，不丢弃历史。"""
        step = new_step(f"step_{len(self.steps) + 1}", action.tool, action.tool, action.args)
        step["status"] = "success" if result["ok"] else "failed"
        step["result"] = result.get("data")
        step["error"] = result.get("error")
        data = result.get("data") or {}
        if result.get("ok") and "total_cost" in data:
            step["cost"] = data["total_cost"]
        if result.get("ok") and "total_hours" in data:
            step["hours"] = data["total_hours"]

        self.steps.append(step)
        self.observations.append({
            "tool": action.tool,
            "args": action.args,
            "ok": result["ok"],
            "data": result.get("data"),
            "error": result.get("error"),
            "retryable": result.get("retryable"),
        })
        self.step_count += 1

    def to_dict(self):
        return {
            "input": self.input,
            "steps": self.steps,
            "total_cost": self.total_cost,
            "total_hours": self.total_hours,
            "observations": self.observations,
            "status": self.status,
            "reason": self.reason,
            "step_count": self.step_count,
            "saved_plan": self.saved_plan,
        }

    @classmethod
    def from_dict(cls, data):
        state = cls(data["input"])
        state.steps = data["steps"]
        state.total_cost = data["total_cost"]
        state.total_hours = data["total_hours"]
        state.observations = data["observations"]
        state.status = data["status"]
        state.reason = data["reason"]
        state.step_count = data["step_count"]
        state.saved_plan = data.get("saved_plan")
        return state


def save_checkpoint(path, state_dict, call_counts=None):
    """把 State 与工具调用计数序列化到文件，供 --resume 续跑。"""
    data = {"state": state_dict, "call_counts": call_counts or {}}
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_checkpoint(path):
    """从 checkpoint 恢复 (State, call_counts)。"""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return State.from_dict(data["state"]), data.get("call_counts", {})
