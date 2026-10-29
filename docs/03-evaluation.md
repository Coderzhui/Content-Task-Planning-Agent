# 测试与评估

运行记录见 [test-results](../examples/test-results.txt)；输入/输出/ Trace 见 [examples/](../examples/)。

自动化测试共 **28 项，全部通过**（`python -m unittest discover -s tests -v`）。

## 用例与验收点对照

| 用例 | 输入要点 | 预期 | 实测 | 覆盖验收点 |
|---|---|---|---|---|
| `normal` | budget=15 | `completed`，total_cost=12（premium） | 通过 | 正常完成 |
| `missing` | 缺 budget | `needs_input`，missing=[budget] | 通过 | 缺预算/截止 |
| `tool-failure` | 注入 generate 第 1 次失败（retryable） | 重试成功 → `completed`；retain search 成功 + 存在一次 failed | 通过 | 工具失败 |
| `budget-overrun` | budget=10 | 高端 12 over → 改标准 8 → `completed` | 通过 | 预算超限 |
| `no-feasible-plan` | budget=5 | `incomplete` + `no_feasible_plan`，saved_plan=null | 通过 | 无可行方案（延伸） |
| 重复执行（测试） | 同 plan 两次 `save_plan` | plan_id 一致 | 通过 | 重复执行 |
| 步数上限（测试） | max_steps=2 | `incomplete` + `step_limit_reached` | 通过 | 步数上限（硬性要求） |
| 不可重试失败（测试） | retryable=false | `incomplete` + `tool_error` | 通过 | 工具失败边界 |
| `resume` | 注入 generate 第 1 次失败 + max_steps=2 中断 | resume 后 `completed`；search 不重复、generate 重试成功 | 通过 | 失败续跑（加分） |

## 评审观察项

| 观察项 | 证据 | 结论 |
|---|---|---|
| 预算计算正确 | `estimate_cost`: premium=12 / standard=8 | 通过 |
| 步骤依赖与实际状态一致 | Trace 中 generate→estimate→save 顺序，failed/success 状态正确 | 通过 |
| 注入失败后调整计划且保留成功结果 | `tool-failure` Trace：search success 保留，generate 失败后重试成功 | 通过 |
| 合理重规划 | `budget-overrun` Trace：premium over → 改 standard | 通过 |
| 状态保留 | `State` 序列化往返测试通过 | 通过 |
| 失败续跑保留成功结果 | `resume` 示例：search success 保留、generate failed 重试成功、estimate+save 补齐 | 通过 |

## 真实 LLM 实跑记录（DeepSeek）

`--model llm` 接 DeepSeek `deepseek-flash`，三条执行路径均 `completed`，运行记录见 `examples/llm-*.output.json`：

| 场景 | 结果 | 决策要点 |
|---|---|---|
| `normal` | completed，total_cost=12（premium） | 预算内直接生成并保存 |
| `budget-overrun` | completed，total_cost=8（standard） | 按预算约束选择低成本方案 |
| `tool-failure` | completed，total_cost=8 | 先估算两素材=17 超预算→改选 standard=8；generate 注入失败→重试成功，保留成功步骤 |

## 已知限制

- 真实 LLM 已通过 DeepSeek 实跑验证（见上表）；本页离线 Mock 用例用于确定性复现流程与状态机制。
- 失败步骤续跑已通过 `--checkpoint` / `--resume` 实现；示例与运行记录见 `examples/resume.*`。