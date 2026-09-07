# GameMakerGraph

面向独立游戏开发者的本地项目知识图谱与 AI 开发增强框架。

GameMakerGraph 帮助 Codex、Claude Code 等通用编程 Agent 在修改游戏前快速回答：

- 这个项目是什么，核心玩法和当前开发方向是什么；
- 某项功能位于哪些文档、场景、脚本、资源和数据中；
- 修改一个系统可能影响什么；
- 开发文档是否齐全，文档与实现是否已经脱节；
- 当前任务需要读取哪些上下文，而不必扫描整个项目。

它不复刻 GameStudio 式的重型多 Agent 工作室，也不替代游戏引擎、代码 Agent 或已有 MCP。
它为本地 Vibe Game 开发提供结构化项目理解、文档搭建，以及少量按需启用的开发 Skill。

> **状态：产品方向已经确定，正在基于上一轮 GameMakerAgent 开发成果做收窄式迁移。**
> `0.2.0` 已完成本地扫描、建图、概览、搜索、新鲜度、任务上下文、影响分析和 CodeGraph CLI
> 组合；文档检查和自动搭建继续按增量切片迁移。重型生产编排降为可选能力。

## 核心价值

GameMakerGraph 的核心产品是 **GameGraph**：一份从本地项目重建、可查询、带来源和新鲜度的
游戏开发关系图。

```text
本地游戏项目
  ├─ 开发文档：定位、玩法、系统、资产、UI、测试和计划
  ├─ 原生实现：场景、脚本、资源、输入、配置和数据
  ├─ 制作关系：功能、资产槽位、实现位置和验收目标
  └─ 当前状态：revision、缺口、冲突和验证结果
            │
            ▼
        GameGraph Core
       索引 · 查询 · 影响分析 · 文档检查
            │
            ├─ Agent：获得任务局部上下文
            ├─ 开发者：快速理解项目和变更范围
            └─ Skills：搭建文档、讨论方向、检查结果
```

我们借鉴 [CodeGraph](https://github.com/colbymchenry/codegraph) 的产品思路：让 Agent 优先查询
结构化关系，而不是反复 grep 和读取大量文件。但两者解决的问题不同：

| CodeGraph | GameMakerGraph |
| --- | --- |
| 理解函数、类、导入和调用链 | 理解玩法、文档、场景、脚本、资源、资产和验证关系 |
| 回答“谁调用这个函数” | 回答“这个玩法在哪里实现、修改后影响什么” |
| 生成代码级影响范围 | 生成游戏功能与制作语义的影响范围 |
| 检查代码架构和测试关系 | 检查开发文档、游戏实现与项目状态是否脱节 |

GameMakerGraph 不复制 CodeGraph 的多语言解析器。需要符号级代码分析时，可以把 CodeGraph
作为上游数据源；GameMakerGraph 专注游戏开发语义。

> **建议搭配 CodeGraph 使用。** GameMakerGraph 解释“玩法、文档、场景和资源如何关联”，
> CodeGraph 解释“前后端代码、符号和调用链如何实现”。`codegraph-documentation` Skill 会合并
> 两类查询结果，按实际项目搭建可交付、可追溯的本地技术文档，使通用编程 Agent 同时理解玩法
> 实现与代码实现；没有 CodeGraph 时，GameMakerGraph Core 仍可独立工作。

## 从上一轮框架继承什么

GameMakerGraph 不是重新从零设计。上一轮开发已经证明了本地项目扫描、可重建关系图、任务局部
上下文和过期拒绝可以协同工作。新框架按下表收敛这些成果：

| 上一轮能力 | GameMakerGraph 中的去向 |
| --- | --- |
| Project Semantic Model / `query` | 进入 GameGraph 的项目概览、搜索和上下文查询 |
| Project Map / `impact` | 重命名并扩展为 GameGraph Core |
| 原生文件指纹与 CURRENT/STALE 状态 | 保留为图新鲜度基础 |
| Context Pack | 简化为面向当前开发任务的 bounded context |
| Studio Advisor | 收窄为轻量 Game Direction Skill |
| Production Card / Asset Spec / Binding | 文档框架可选模板，不再是普通开发必经流程 |
| Evidence Review / Provider Conformance | 移到高风险交付与发布检查扩展 |
| Godot Dock 与 godot-ai 固定探针 | 不进入 Core；按需要转为工具集成 |

迁移原则是保留经过测试的机制，改变默认产品路径；不是把旧目录整份复制，也不是只换名字。

## 三项产品能力

### GameGraph Core

这是较重的工程核心。

- 扫描本地项目并建立可重建索引；
- 连接开发文档、场景、脚本、资源、数据、资产和测试；
- 提供项目概览、搜索、任务上下文和变更影响查询；
- 为每项关系保留来源与 revision，拒绝静默使用过期图；
- 标记缺失文档、断开引用和实现/文档冲突；
- 保持原生项目文件为真源，不创建第二套引擎数据模型。

首版以本地文件为共同基础，以 Godot 项目验证游戏语义。其他引擎的编辑、运行、截图和诊断
优先接入已有 MCP 或 CLI，本项目不重新实现引擎控制层。

### Documentation Framework

代码探索和文档搭建采用明确、可验证但可裁剪的框架。GameMakerGraph 根据项目类型和已有内容，
帮助建立最小必要文档，例如：

- 项目定位和玩家体验目标；
- 核心循环、系统规则和数值边界；
- 场景、资源与模块结构；
- 美术方向、基准图和资产槽位；
- UI 结构、尺寸和后续替换位置；
- 测试、试玩、已知问题和开发计划。

文档框架发现缺口、建立结构并保持关联，但不替开发者虚构世界观、剧情、审美判断或未确认的
玩法事实。小项目不需要维护完整 GDD。

### Development Skills

方向探讨和开发辅助保持轻量。Skill 消费 GameGraph，但不是常驻角色或强制阶段。

计划提供：

- **Project Bootstrap**：理解现有项目并建议最小文档集；
- **Feature Context**：开发前返回相关文档、实现位置、影响范围和未知关系；
- **Documentation Builder**：搭建或补齐经用户确认的开发文档；
- **CodeGraph Documentation**：结合 GameGraph 与 CodeGraph，搭建前端、后端、架构、开发和交付文档；
- **Game Direction**：简洁讨论玩法、体验、范围和优先级；
- **Asset & UI Planning**：明确风格基准、资产槽位和 UI 占位；
- **Review & Playtest**：按需检查实现、文档和玩家可见结果。

只有存在真实创作取舍时才进入方向讨论。普通编码和修错不会被迫经过完整策划流程。

## 典型体验

开发者在已有项目中提出：

> “我要增加一个商店事件，先帮我看看应该改哪里。”

GameMakerGraph 应该返回：

1. 与商店、事件、货币和奖励相关的设计文档；
2. 对应场景、脚本、数据表、资源和测试；
3. 已知引用关系与可能遗漏的动态关系；
4. 开发前需要确认的最小玩法问题；
5. 文档或验收中仍缺少的内容。

确认方向后，编码 Agent 继续使用原有工具修改项目。GameMakerGraph 不接管编辑器，也不要求用户
进入虚拟工作室工作流。

## 当前可运行能力

需要 Python 3.11 或更高版本。在本目录安装开发版本后，可对任意本地项目运行：

```bash
python -m pip install -e .
gamegraph build /path/to/game
gamegraph overview /path/to/game
gamegraph search "shop economy" /path/to/game
gamegraph context "add a shop event" /path/to/game
gamegraph impact "file:scenes/shop.tscn" /path/to/game --code-symbol open_shop
gamegraph status /path/to/game
```

当前索引识别 Markdown 文档与标题、常见代码/配置/数据/资产文件、Markdown 相对链接，以及
Godot 文件中的 `res://` 引用。输出为 JSON；派生索引保存在目标项目的 `.gamemakergraph/`。

### 与 CodeGraph 直接组合

GameMakerGraph 不内嵌或复刻 CodeGraph。安装并初始化上游 CodeGraph 后，`context` 会自动检测
项目内的 `.codegraph/`，通过官方 JSON CLI 合并符号级结果：

```bash
# CodeGraph 的安装方式以其官方文档为准
codegraph init /path/to/game
gamegraph build /path/to/game
gamegraph context "how is player inventory implemented" /path/to/game
```

`impact` 默认返回 GameGraph 的玩法/文档/资源影响范围；提供 `--code-symbol` 时同时查询代码影响：

```bash
gamegraph impact "file:docs/inventory.md" /path/to/game --code-symbol InventoryService
```

CodeGraph 未安装、未初始化或索引有待同步变更时，结果会明确返回 `unavailable`、`uninitialized`
或 `stale`，GameGraph 本身仍可使用。用 `--no-codegraph` 可以显式关闭组合查询。适配契约见
[`docs/contracts/codegraph-provider.md`](docs/contracts/codegraph-provider.md)，上游源码结构与集成取舍见
[`CodeGraph 源码分析`](docs/research/codegraph-source-analysis-2026-09-07.md)。

`codegraph-documentation` Skill 位于
[`plugins/gamemaker-graph/skills/codegraph-documentation`](plugins/gamemaker-graph/skills/codegraph-documentation/SKILL.md)，
用于组合 GameMakerGraph 与 CodeGraph 查询结果并搭建本地技术文档。

## 明确不做

- 不训练或包装专用游戏开发模型；
- 不创建固定人数的多 Agent 团队；
- 不维护强制的策划、美术、程序、测试阶段状态机；
- 不自动生成完整游戏并宣称成品质量；
- 不重新实现 Godot、Unity 或其他引擎 MCP；
- 不把 GameGraph 变成第二套 SceneTree；
- 不要求普通修错填写大量生产记录；
- 不自动把 Agent 推断写成已确认的玩法事实。

## 架构原则

1. **Local first**：代码、文档、图索引和开发记录留在本地项目。
2. **Graph before grep**：有可靠关系时先查询图；未覆盖时明确回到原生文件。
3. **Native source of truth**：场景、脚本和资源事实由原生项目决定。
4. **Human-confirmed semantics**：玩法与创作意图来自用户确认或明确文档。
5. **Disposable index**：GameGraph 可以删除并从当前项目重建。
6. **Bounded context**：只给 Agent 当前任务相关的邻域。
7. **Provider reuse**：引擎和素材执行复用成熟 MCP、CLI 与生成工具。
8. **Progressive structure**：小项目保持轻量，复杂度出现后再增加结构。

## 验证路径

### 第一阶段：TapTapMakerMCP 小游戏

连接 TapTapMakerMCP 完成一款范围受控的小游戏，验证：

- 能快速建立项目概览；
- Agent 能在开发前查询相关文档和实现位置；
- 能从空白或半成品状态搭建最小开发文档；
- GameGraph 能跟随实际修改保持新鲜；
- 使用者能够感知上下文查找和返工减少。

这一阶段验证产品是否改善独立开发者的本地 Vibe 编程体验，不绑定特定引擎实现。

### 第二阶段：Godot + TapTapGameJam

连接现有 Godot MCP，在 TapTapGameJam 的真实制作压力下验证：

- 玩法文档、场景、脚本、资源和资产关系能否持续维护；
- 开发前影响分析能否减少误改和遗漏；
- 美术基准、UI 占位和资产替换是否可追踪；
- 轻量方向讨论是否帮助控制范围而不打断开发；
- 框架在真实迭代速度下是否仍足够轻。

具体游戏的玩法、关卡、资产和项目文档保留在独立项目仓库；本仓库只接收去项目化、经过验证的
通用能力。

## 当前抽离顺序

1. 固定产品定位、继承边界和非目标；
2. 从上一轮实现迁移本地索引、新鲜度和 GameGraph 查询核心；
3. 建立可裁剪的开发文档框架；
4. 提供消费 GameGraph 的轻量 Skills；
5. 将严格生产交付和证据机制降为可选扩展；
6. 完成包名、CLI、Schema 和插件接口；
7. 执行 TapTapMakerMCP 与 Godot 两阶段验证。

详细模块边界见 [CAPABILITY_MAP.md](CAPABILITY_MAP.md)，迁移步骤见
[抽离计划](docs/plans/extraction-plan.md)。

## 开发状态

当前目录是新框架的独立发布根。迁移代码必须满足：

- 不依赖旧仓库中的具体游戏项目或私有路径；
- 每个模块具有独立、可执行的验收条件；
- GameGraph 索引可以删除重建；
- 核心查询不依赖某个引擎 MCP；
- 旧框架已有测试随迁移能力一起进入，不能只复制实现；
- 旧框架能力按新产品默认路径重新分层，而不是重新发明同一机制。

抽离完成的标准不是“替换所有旧名称”，而是独立开发者无需进入重型流程，就能可靠地理解项目、
搭建文档、讨论方向并继续使用现有工具开发。

## 致谢

特别感谢 [Colby Mchenry 的 CodeGraph](https://github.com/colbymchenry/codegraph)。它提供了本地优先
的符号、调用链和代码影响分析，也启发了 GameMakerGraph 的“Graph before grep”体验。
GameMakerGraph 没有复制 CodeGraph 源码；我们通过其公开 CLI/MCP 边界组合能力，并专注补充玩法、
文档、场景、资源和开发意图之间的游戏语义层。
