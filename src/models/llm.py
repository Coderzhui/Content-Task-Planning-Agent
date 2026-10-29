"""真实 LLM 模型（OpenAI 兼容 chat/completions，标准库 urllib，未实跑）。"""
import json
import os
import urllib.request

from .base import Model, Action

SYSTEM_PROMPT = (
    "你是内容活动规划助手。你只能使用给定工具，逐步完成方案规划。"
    "只用给定素材与工具，不编造数字。必须在预算与截止时间内完成；"
    "工具失败时调整动作（可重试一次或换方案），已成功步骤的结果必须保留，失败步骤不得记为成功。"
    "每次只输出一个 JSON 动作：{\"action\": \"工具名\", \"args\": {...}} 或 {\"action\": \"stop\", \"reason\": \"...\"}。"
)


class LLMModel(Model):
    def __init__(self, base_url=None, api_key=None, model=None):
        self.base_url = (base_url or os.getenv("LLM_BASE_URL", "")).rstrip("/")
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.model = model or os.getenv("LLM_MODEL", "kimi-k2.6")

    def decide(self, observation, tools_schema):
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": self._build_prompt(observation, tools_schema)},
            ],
            "temperature": 0,
        }).encode("utf-8")

        req = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        content = body["choices"][0]["message"]["content"]
        return self._parse_action(content)

    def _build_prompt(self, observation, tools_schema):
        return json.dumps({"observation": observation, "tools": tools_schema}, ensure_ascii=False, indent=2)

    def _parse_action(self, content):
        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM 输出不是合法 JSON") from exc

        action = data.get("action")
        if action == "stop":
            return Action("stop", reason=data.get("reason", "completed"))
        if action is None:
            raise ValueError("LLM 输出缺少 action 字段")
        return Action("tool", action, data.get("args", {}))