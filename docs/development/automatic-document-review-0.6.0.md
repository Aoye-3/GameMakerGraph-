# GameMakerGraph 0.6.0 自动文档维护与主动 Review

Status: accepted for implementation

## 目标

GameMakerGraph 在 Coding Agent 开发前保存用户确认的增量契约，在代码、场景、资源或文档发生变化后
自动标记待复核状态，并在开发完成后生成确定性的文档维护预览。新开发窗口只读取项目目录，就能恢复
当前目标、验收标准、变化、证据缺口和下一步。

自动化只处理可确定的机械事实。目标、设计决定、验收含义和“功能已经通过”等语义结论，必须经用户
确认后才能进入 Markdown 真源。

## 状态机

```text
draft -> confirmed -> changed -> review_required
                              -> implemented_unverified
                              -> validated -> documented/current

confirmed increments may also become blocked, rejected, or superseded.
```

- `draft` 只存在于 `prepare` 返回值，不写项目。
- `confirmed` 表示用户确认了目标、边界和验收标准；确认结果写入受控 Markdown。
- `changed` 与 `review_required` 由派生 monitor 状态自动产生。
- `implemented_unverified` 表示存在实现变化，但证据不足以证明玩法通过。
- `validated` 必须有与当前 revision 对齐的 runtime、playtest 或 user-confirmation 证据。
- `documented/current` 表示已确认维护计划写入文档，派生图与项目当前内容一致。

## 真源与派生状态

- `docs/development/project-memory.md` 的 `GAMEGRAPH:START/END` 区块保存已确认语义事实。
- `.gamemakergraph/graph.json` 是可删除、可重建的关系索引。
- `.gamemakergraph/review-state.json` 是可删除、可重建的活动增量、基线 manifest、变化和 Review 状态。
- watcher 不读取 `.maker-mcp/config.json`，不调用 Maker MCP、CodeGraph MCP 或 Sampling。
- watcher 永不自行修改 Markdown；它只维护派生状态和派生图，并生成待用户确认的计划。

## 自动监测

stdio MCP 进程第一次收到某个项目根的工具调用时注册该项目。后台 monitor 使用标准库线程轮询已注册
项目，约一秒防抖；发现受支持文件 manifest 改变后，重建派生图并更新 Review 状态。MCP 进程关闭期间
不安装系统服务；下次 `inspect` 会同步执行同样的 reconcile，从而发现离线变化。

若 `review-state.json` 被删除，inspect 从已确认 Markdown 恢复活动目标并进入 `review_required`。由于旧
manifest 无法由当前文件反推，Review 必须报告 `baseline_recovered`，不得伪造历史 changed paths。

受控 Markdown 写入完成后，应用流程在同一临界区重建图并更新 monitor 基线，避免 watcher 把自己的
维护写入误判为新的实现变化。

## MCP 契约

`gamegraph_prepare_increment(project_root, goal)` 返回确定性 draft：

- `increment_id`、`goal`、`player_observable_change`；
- `constraints`、`non_goals`、`acceptance_criteria`、`open_questions`；
- `codegraph_queries` 和 `base_revision`。

`gamegraph_confirm_increment(project_root, expected_revision, draft)` 在用户确认后写入项目记忆并建立活动
增量。相同 `increment_id` 与相同内容重复确认返回 `unchanged`；内容不同或 revision 过期时零写入。

`gamegraph_review_increment(project_root, increment_id, evidence=[])` 只允许复核已确认增量，返回：

- 分类后的 added、modified、removed 路径；
- `findings`、`evidence`、`evidence_gaps`；
- `implemented_unverified` 或 `validated`；
- 带确定性 `plan_id` 的 Markdown 维护预览。

`gamegraph_apply_maintenance` 仍要求用户确认 exact plan。成功后自动 rebuild，并把活动增量闭合为
`documented/current`。显式 `gamegraph_rebuild_index` 保留用于恢复。

## Review 证据规则

- `build` 只证明构建结果，不能证明玩法通过。
- `runtime` 证明同一 revision 的项目实际启动或执行。
- `playtest` 证明玩家操作产生了验收标准要求的可观察状态变化。
- `user_confirmation` 证明用户接受体验结论。
- `validated` 至少需要一条 `passed` 的 `playtest` 或 `user_confirmation`；仅有 build/runtime 时保持
  `implemented_unverified`。
- 证据路径必须是现存的项目相对路径；输出只保留允许字段和摘要，不复制证据文件内容。

## 实施与验证

1. 先以失败测试锁定 draft、确认、冲突与跨进程恢复。
2. 实现派生 review-state 与同步 reconcile。
3. 增加后台 monitor，并测试防抖、多项目、删除和连续修改。
4. 改造 Review、apply 和 MCP schema。
5. 更新 README、契约、架构、语义模型、Skills、CHANGELOG 与版本。

完成条件是三窗口场景可重复通过：窗口 A 确认目标后退出；窗口 B 修改并运行；窗口 C 只凭项目路径
主动发现待 Review，展示证据缺口，确认维护后恢复 `current`。
