"""CLI 入口。"""
import argparse
import json
import sys
from pathlib import Path

from .validate import validate
from .catalog import Catalog
from .agent import run_agent, build_model


def main(argv=None):
    parser = argparse.ArgumentParser(description="内容任务规划 Agent")
    parser.add_argument("--input", required=True)
    parser.add_argument("--model", default="offline_mock", choices=["offline_mock", "llm"])
    parser.add_argument("--max-steps", type=int, default=12)
    args = parser.parse_args(argv)

    try:
        request = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "invalid_input", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2

    try:
        normalized, missing = validate(request)
    except ValueError as exc:
        print(json.dumps({"status": "invalid_input", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2

    if missing:
        print(json.dumps({"status": "needs_input", "missing": missing, "trace": ["validate"]}, ensure_ascii=False, indent=2))
        return 0

    catalog = Catalog.load()
    model = build_model(args.model)
    result = run_agent(normalized, model, catalog, max_steps=args.max_steps)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())