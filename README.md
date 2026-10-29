# Content-Task-Planning-Agent

帮助运营人员在**预算**与**截止时间**双重约束下完成一份内容活动方案，并通过 ReAct 决策循环在**预算超限、工具失败、部分成功**时动态重规划、保留已成功步骤结果。

## 快速运行

Python 3.10+，标准库 only；离线 Mock 无需密钥。在仓库根目录执行：

```sh
python -m src.main --input examples/normal.input.json
python -m src.main --input examples/missing.input.json
python -m src.main --input examples/tool-failure.input.json
python -m src.main --input examples/budget-overrun.input.json
python -m src.main --input examples/no-feasible-plan.input.json
python -m src.main --input examples/over-deadline.input.json
python -m unittest discover -s tests -v

# 失败续跑：先触发中断写 checkpoint，再 --resume 续跑
python -m src.main --input examples/resume.input.json --max-steps 2 --checkpoint examples/resume.checkpoint.json
python -m src.main --resume examples/resume.checkpoint.json
```

- 成功输出 JSON 交付结果；业务异常以 JSON 状态返回；输入文件格式错误返回退出码 2。
- 运行记录见 `examples/test-results.txt`。

## 项目目录

```text
.
├── README.md
├── requirements.txt          # 标准库 only
├── .env.example              # 真实 LLM（可选）环境变量
├── docs/                     # 需求/方案/评估/AI使用/复盘（02-solution 已就绪）
├── src/
│   ├── main.py               # CLI 入口
│   ├── agent.py              # ReAct 引擎
│   ├── state.py              # State/Step 与序列化
│   ├── catalog.py            # 素材/工具目录
│   ├── validate.py           # 输入校验
│   ├── planner.py            # 工具 schema / 预设骨架
│   ├── models/               # base.py / offline_mock.py / llm.py
│   └── tools/                # registry + search/script/estimate/save
├── data/catalog.json         # 素材/工具费用耗时表
├── tests/                    # unittest
└── examples/                 # 输入、实际输出、Trace
```

## 评审导航

| 检查项 | 入口 |
|---|---|
| 方案设计 | [docs/02-solution.md](docs/02-solution.md) |
| 测试预期与结果 | `tests/` + `examples/test-results.txt` |

## 模型接入

- **离线 Mock（默认）**：`--model offline_mock`。确定性策略，只验证引擎循环与状态机制，**不构成真实 ReAct 决策证据**。
- **真实 LLM**：`--model llm`，读取环境变量 `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL`（OpenAI 兼容 `chat/completions`，标准库直连）。已用 DeepSeek 实跑，见 `examples/llm-*.output.json` 与 `docs/03-evaluation.md`。

## 已知边界

- 素材/工具为合成数据，脚本生成为模板占位，不评估真实创意与合规质量。
- 失败步骤续跑已通过 `--checkpoint` / `--resume` 实现，示例见 `examples/resume.*`。