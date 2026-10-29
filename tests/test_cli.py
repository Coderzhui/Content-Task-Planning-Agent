import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

from src.main import main


class CliTests(unittest.TestCase):
    def _run(self, data):
        buf_out, buf_err = StringIO(), StringIO()
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(data, f)
            path = f.name
        try:
            with redirect_stdout(buf_out), redirect_stderr(buf_err):
                code = main(["--input", path])
        finally:
            os.unlink(path)
        return code, json.loads(buf_out.getvalue())

    def test_normal(self):
        code, out = self._run({"topic": "t", "budget": 15, "deadline_hours": 20})
        self.assertEqual(code, 0)
        self.assertEqual(out["status"], "completed")

    def test_missing_budget(self):
        code, out = self._run({"topic": "t", "deadline_hours": 20})
        self.assertEqual(code, 0)
        self.assertEqual(out["status"], "needs_input")
        self.assertEqual(out["missing"], ["budget"])

    def test_bad_json_file(self):
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            code = main(["--input", "no_such_file.json"])
        self.assertEqual(code, 2)

    def test_resume(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump({"topic": "t", "budget": 15, "deadline_hours": 20}, f)
            in_path = f.name
        ck = tempfile.mktemp(suffix=".json")
        try:
            out1 = StringIO()
            with redirect_stdout(out1):
                code1 = main(["--input", in_path, "--max-steps", "2", "--checkpoint", ck])
            first = json.loads(out1.getvalue())
            self.assertEqual(code1, 0)
            self.assertEqual(first["status"], "incomplete")
            self.assertEqual(first["reason"], "step_limit_reached")
            self.assertTrue(os.path.exists(ck))

            out2 = StringIO()
            with redirect_stdout(out2):
                code2 = main(["--resume", ck, "--checkpoint", ck])
            second = json.loads(out2.getvalue())
            self.assertEqual(code2, 0)
            self.assertEqual(second["status"], "completed")
            self.assertEqual(second["total_cost"], 12)
        finally:
            os.unlink(in_path)
            if os.path.exists(ck):
                os.unlink(ck)


if __name__ == "__main__":
    unittest.main()