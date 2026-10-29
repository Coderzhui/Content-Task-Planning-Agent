"""CLI 入口。"""
import argparse
import json
import sys
from pathlib import Path

from .validate import validate
from .catalog import Catalog
from .state import load_checkpoint
from .agent import run_agent, build_model


def main(argv=None):
    parser = argparse.ArgumentParser(description="内容任务规划 Agent")
    parser.add_argument("--input")
    parser.add_argument("--model", default="offline_mock", choices=["offline_mock", "llm"])
    parser.add_argument("--max-steps", type=int, default=12)
    parser.add_argument("--checkpoint", help="运行结束写入 checkpoint 的路径")
    parser.add_argument("--resume", help="从 checkpoint 文件续跑")
    args = parser.parse_args(argv)

    if not args.input and not args.resume:
        parser.error("必须提供 --input 或 --resume 之一")

    catalog = Catalog.load()
    model = build_model(args.model)

    if args.resume:
        try:
            state, call_counts = load_checkpoint(args.resume)
        except (OSError, ValueError) as exc:
            print(json.dumps({"status": "invalid_input", "error": f"resume: {exc}"}, ensure_ascii=False), file=sys.stderr)
            return 2
        result = run_agent(state.input, model, catalog, max_steps=args.max_steps,
                           resume_state=state, resume_call_counts=call_counts,
                           checkpoint_path=args.checkpoint)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

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

    result = run_agent(normalized, model, catalog, max_steps=args.max_steps,
                       checkpoint_path=args.checkpoint)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())