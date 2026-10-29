"""Model 抽象与 Action。"""


class Action:
    def __init__(self, kind, tool=None, args=None, reason=None):
        self.kind = kind  # "tool" | "stop"
        self.tool = tool
        self.args = args or {}
        self.reason = reason


class Model:
    def decide(self, observation, tools_schema):
        raise NotImplementedError