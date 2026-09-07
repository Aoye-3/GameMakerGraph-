# GameMakerGraph 抽离计划

## 状态

Phase 0 complete. Phase 1 first executable slice complete; context and impact remain pending.

## 原则

- 只在当前工作区的 `GameMakerGraph-/` 中建立新框架；
- 不复制旧仓库，不创建嵌套 Git 仓库或 worktree；
- 从上一轮实现迁移经过验证的扫描、图、上下文、Schema 和测试；
- 收窄默认流程，不重新实现已有机制；
- 每个增量保持新目录可独立测试和发布；
- 具体游戏项目、资产和运行证据不进入新框架。

## Phase 0：产品基线

- [x] 新 README
- [x] Capability Map
- [x] 产品边界文档
- [x] 两阶段验证路径

验收：新读者能区分 GameGraph Core、文档框架、轻量 Skill、外部工具和可选证据扩展。

## Phase 1：GameGraph Core

- [x] 写 Core 规格并确认公共命令；
- [x] 建立独立 Python 包和测试入口；
- [x] 从 `project.py` 迁移文件扫描、manifest 和 revision；
- [ ] 从 `project_map.py` 迁移图构建、影响查询和生命周期；
- [ ] 从 `context.py` 迁移并简化任务局部上下文；
- [x] 将 Markdown 文档提升为一等节点；
- [x] 生成带来源和 revision 的确定性图；
- [ ] 实现 overview、search、context、impact、status；
- [x] 实现 build、overview、search、status；
- [x] 实现可丢弃索引和 stale 检测；
- [x] 首版内置最小 Godot `res://` 引用解析，不依赖 Godot MCP。

验收：对两个不同结构的本地夹具建立等价可重建图，不依赖旧包或 MCP。

## Phase 2：Documentation Framework

- [ ] 定义项目类型与最小文档集的输入；
- [ ] 建立不含具体游戏内容的文档模板；
- [ ] 实现 docs inspect、suggest、init、check；
- [ ] 将标题、引用、系统和资产槽位加入 GameGraph；
- [ ] 区分已确认事实、模板占位和 Agent 推断。

验收：能从空白项目搭建最小文档，也能在已有项目中只补缺口而不覆盖原文。

## Phase 3：Development Skills

- [x] CodeGraph Documentation
- [ ] Project Bootstrap
- [ ] Feature Context
- [ ] Documentation Builder
- [ ] Game Direction
- [ ] Asset & UI Planning
- [ ] Review & Playtest

验收：查询/搭建采用明确流程，方向讨论保持轻量；普通编码不会加载无关 Skill。

## Phase 4：TapTapMakerMCP 验证

- [ ] 定义最小 Integration 契约；
- [ ] 连接已有 TapTapMakerMCP；
- [ ] 从需求、文档、开发到可玩小游戏完成一次自然流程；
- [ ] 记录图查询是否减少全仓扫描、遗漏和返工；
- [ ] 根据真实断点修正 Core、文档与 Skill。

验收：独立开发者可以感知 GameMakerGraph 相比直接使用 Agent + MCP 的增量价值。

## Phase 5：Godot GameJam 验证

- [ ] 连接已有 Godot MCP；
- [ ] 在独立比赛项目中维护玩法、文档、场景、脚本和资产关系；
- [ ] 验证真实迭代速度下的索引成本与上下文质量；
- [ ] 验证美术基准、UI 占位和资产替换路径；
- [ ] 按实际需要决定是否迁移严格 Evidence 扩展。

验收：框架在 GameJam 压力下仍然轻量，并实际减少理解、沟通或修改错误。

## 不进入默认核心

- Project1 和 Dice Maze 内容；
- godot-ai 固定版本安装与本机探针；
- 旧 Production Card / Asset Spec / Godot Binding 默认流程；
- 旧 Evidence Bundle 的强制完成门禁；
- 旧包名、CLI 和 Schema ID；它们在新接口稳定后一次性替换。

这些内容保留在旧实验中作为证据和参考。与项目扫描、图查询、上下文和文档无关的能力，不因
“上一轮已经做过”而自动进入新产品。
