# AI 使用说明

本仓库在对话式开发中由 AI 辅助完成，覆盖需求分析、方案设计、实施计划、代码实现、测试与文档撰写。

## AI 使用范围

| 阶段 | AI 贡献 | 验证方式 |
|---|---|---|
| 需求/方案/计划 | 起草 `ANALYSIS.md`、`docs/02-solution.md`、`PLAN.md` | 对照 `question.md` 检查需求与验收点覆盖 |
| 代码 | 实现 `src/`（校验/目录/状态/工具/模型双入口/ReAct 引擎/CLI，含 `--resume` 续跑） | 28 项 unittest 全部通过 |
| 测试 | 生成 tests/* 与 5 组 examples 输入/输出 | `python -m unittest discover -s tests -v` |
| 结果 | 写入实际运行输出与 `test-results.txt` | 与输入逐项对应 |

## 关键设计决策与个人修改记录

> 说明：下表「个人贡献」列记录候选人在本次协作中**实际做出的决策与评审**（据对话如实记录）。AI 负责起草，个人负责判断、拍板与取舍。若有手写代码修改，请在下方补充；切勿照搬 AI 产出或虚构改动。

| # | 决策/问题 | AI 初稿 | 个人贡献与验证 |
|---|---|---|---|
| 1 | 技术栈选型 | 原生 Python 手写 ReAct | 在「原生 vs LangGraph/ADK」中选定原生手写 + 双入口模型 + CLI，理由为零依赖、隔离环境最易复现 |
| 2 | `estimate_cost` 显式传 budget/deadline | 建议显式传参 | 在「显式传参 vs 读全局 State」中选择显式传参，并确认 `over_budget/over_deadline` 由工具返回后进入观察 |
| 3 | 离线 Mock 决策序列 | 建议 A/B/C 三条 | 确认 A/B/C 三条确定性序列与 `retryable` 重试规则，作为离线集成测试预期 |
| 4 | 交付 JSON 结构 | 建议 `plan.steps` + `trace` 对象数组 | 确认 `status` 收敛为 3 值、`plan.steps` 嵌套、`trace` 对象数组、`saved_plan` 可空 |
| 5 | 失败注入 `retryable` 层级 | 建议顶层字段 | 拍板 Option A（顶层 `retryable`、`error` 保持字符串），确认失败注入默认 `retryable=true` |
| 6 | 文档口径冲突 | 两份文档技术选型口径不一 | 主动发现并推动统一 `02-solution` 与 `PLAN` 的选型 / deadline 口径 |

### 需候选人本人补充（重要）

- 上方记录的是「决策/评审」贡献。校招考核通常还期望至少一处**手写代码修改**（例如：AI 初稿存在 X 缺陷，本人改为 Y 并新增测试）。当前协作中代码由 AI 生成，请在提交前至少亲自做一处实际修改并在下表补记，否则个人贡献会显得单薄且不实。

| 改动 | 原因 | 验证 |
|---|---|---|
| `summarize()` 只暴露业务字段 | AI 初稿把整个 `state.input`（含 `fail_injections` 测试注入项）喂给模型，会向真实 LLM 泄露测试细节 | 手写过滤为 `topic/budget/deadline_hours`；新增 `test_summarize_hides_fail_injections`，28 项测试通过 |

## 验证结论

- 离线 Mock 只验证流程与状态机制；真实模型决策效果已通过 DeepSeek 实跑验证，三条路径记录于 `examples/llm-*.output.json`、`docs/03-evaluation.md`。
- 本文件不替代候选人的真实贡献说明，最终提交前需补齐「个人贡献」列。