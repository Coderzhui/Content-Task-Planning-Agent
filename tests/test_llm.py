import json
import unittest
import urllib.error
from unittest.mock import patch

from src.models.llm import LLMModel


class _FakeResponse:
    def __init__(self, data):
        self._data = data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._data


def _ok_body(content):
    return json.dumps({"choices": [{"message": {"content": content}}]}).encode("utf-8")


class LLMTests(unittest.TestCase):
    def test_retries_on_429_then_succeeds(self):
        model = LLMModel(base_url="http://x", api_key="k", model="m")
        ok = _ok_body('{"action":"stop","reason":"done"}')

        calls = []

        def fake_urlopen(req, timeout):
            calls.append(1)
            if len(calls) == 1:
                raise urllib.error.HTTPError(req.full_url, 429, "Too Many", {}, None)
            return _FakeResponse(ok)

        with patch("urllib.request.urlopen", side_effect=fake_urlopen), patch("time.sleep"):
            action = model.decide({"input": {}, "steps": [], "last": None}, [])

        self.assertEqual(action.kind, "stop")
        self.assertEqual(action.reason, "done")
        self.assertEqual(len(calls), 2)

    def test_parse_action_json_fence(self):
        model = LLMModel(base_url="http://x", api_key="k", model="m")
        action = model._parse_action('```json\n{"action":"search_material","args":{"topic":"t"}}\n```')
        self.assertEqual(action.kind, "tool")
        self.assertEqual(action.tool, "search_material")
        self.assertEqual(action.args, {"topic": "t"})


if __name__ == "__main__":
    unittest.main()