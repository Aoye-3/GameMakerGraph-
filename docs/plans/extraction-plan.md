# GameMakerGraph 抽离计划

## 状态

Phase 0 complete: product README and capability boundaries established.

## 原则

- 只在当前工作区的 `GameMaker/` 中建立新框架；
- 不复制旧仓库，不创建嵌套 Git 仓库或 worktree；
- 从旧实现选择性迁移经过验证的最小能力；
- 每个增量保持新目录可独立测试和发布；
- 具体游戏项目、资产和运行证据不进入新框架。

## Phase 0：产品基线

- [x] 新 README
- [x] Capability Map
- [x] 产品边界文档
- [x] 两阶段验证路径

验收：新读者能区分 GameGraph Core、文档框架、轻量 Skill、外部工具和可选证据扩展。

## Phase 1：GameGraph Core

- [ ] 写 Core 规格并确认公共命令；
- [ ] 建立独立 Python 包和测试入口；
- [ ] 扫描文件与 Markdown 文档；
- [ ] 生成带来源和 revision 的确定性图；
- [ ] 实现 overview、search、context、impact、status；
- [ ] 实现可丢弃索引和 stale 检测；
- [ ] 决定 Godot 解析器是首版内置还是后续插件。

验收：对两个不同结构的本地夹具建立等价可重建图，不依赖旧包或 MCP。

## Phase 2：Documentation Framework

- [ ] 定义项目类型与最小文档集的输入；
- [ ] 建立不含具体游戏内容的文档模板；
- [ ] 实现 docs inspect、suggest、init、check；
- [ ] 将标题、引用、系统和资产槽位加入 GameGraph；
- [ ] 区分已确认事实、模板占位和 Agent 推断。

验收：能从空白项目搭建最小文档，也能在已有项目中只补缺口而不覆盖原文。

## Phase 3：Development Skills

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

## 本轮不迁移

- Project1 和 Dice Maze 内容；
- godot-ai 固定版本安装与本机探针；
- 旧 Production Card / Asset Spec / Godot Binding 默认流程；
- 旧 Evidence Bundle 的强制完成门禁；
- 旧包名、CLI 和 Schema ID。

这些内容保留在旧实验中作为证据和参考，只有新模块规格明确需要时才迁入。
