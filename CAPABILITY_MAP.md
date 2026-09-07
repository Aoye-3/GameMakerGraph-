# Capability Map: GameMakerGraph

## 目标

把上一轮 GameMakerAgent 已验证的项目图、上下文、新鲜度和 Skill 路由，收窄为面向独立开发者
的本地 GameGraph 产品。模块边界以用户体验和可独立验证能力划分；实现从旧框架迁移，但默认路径
不继承旧的重型交付流程。

## 模块

| Module ID | 职责 | 依赖 |
| --- | --- | --- |
| `gamegraph-core` | 扫描本地项目，建立可重建关系图，提供概览、搜索、上下文、影响和状态查询 | — |
| `docs-framework` | 识别项目文档，搭建最小文档集，检查文档缺口与实现漂移 | `gamegraph-core` |
| `development-skills` | 提供项目理解、功能上下文、文档搭建和轻量方向讨论 Skill | `gamegraph-core`, `docs-framework` |
| `tool-integrations` | 把 TapTapMakerMCP、Godot MCP、CodeGraph 等成熟工具接到稳定边界 | `gamegraph-core` |
| `delivery-evidence` | 为高风险功能提供可选的严格交付和运行证据扩展 | `gamegraph-core`, `tool-integrations` |

依赖方向保持单向。Core 不依赖 Skill、MCP 或证据扩展。

## 上一轮实现映射

| Module ID | 主要迁移来源 | 迁移方式 |
| --- | --- | --- |
| `gamegraph-core` | `project.py`, `project_map.py`, `context.py`, 对应 Schema 与测试 | 保留确定性扫描、新鲜度、受限查询；移除对 Production/Evidence 的硬依赖 |
| `docs-framework` | `docs/` 契约经验、Decision/Production 中已验证的文档字段 | 提炼为普通 Markdown 项目文档与缺口检查 |
| `development-skills` | Studio Advisor、Game Delivery 的查询和确认边界 | 合并、改名并缩短默认流程 |
| `tool-integrations` | Provider profile、Godot probe、Dock 实验 | 只保留稳定集成边界，不迁移固定安装路径 |
| `delivery-evidence` | Evidence Review、Binding、运行记录 | 保留为默认关闭的可选扩展 |

## 建设顺序

```text
gamegraph-core
  ├─> docs-framework ─> development-skills
  └─> tool-integrations ─> delivery-evidence（可选）
```

首轮产品验证顺序：

1. `gamegraph-core`
2. `docs-framework`
3. `development-skills` 的最小子集
4. TapTapMakerMCP integration
5. Godot integration
6. 确有需要时再迁移 `delivery-evidence`

## 模块验收边界

### `gamegraph-core`

- 对一个本地项目生成确定性图；
- 每个节点和关系有本地来源；
- 提供 overview、search、context、impact、status；
- 文件变化会使旧图变为 stale；
- 删除索引后可以重建等价关系；
- 不要求任何引擎 MCP 在线。

### `docs-framework`

- 能识别现有 Markdown 开发文档；
- 根据项目类型建议最小文档集，不默认生成完整 GDD；
- 只在用户确认后创建或改变创作语义；
- 能报告缺少章节、未解析引用和文档/实现漂移；
- 模板不包含具体游戏设定。
- `inspect`、`suggest`、`init`、`check` 四步链路已经实现；
- `init` 只补缺失文件，现有文档保持不变。

### `development-skills`

- 普通代码查询不会加载方向顾问；
- 功能开发前优先读取 GameGraph 的任务局部上下文；
- 文档搭建具有明确输入、输出和确认边界；
- 方向讨论保持简短，不创建阶段状态机；
- Skill 不依赖具体 MCP 工具名称。
- `codegraph-documentation` 可在 CodeGraph 可用时合并玩法图与代码图，生成可追溯的本地技术文档；
- 前端、后端、部署等文档按仓库实际组成启用，不为不存在的系统生成占位架构。
- 根目录 `skills/` 已发布项目探索、文档搭建、项目启动、方向讨论、美术规划、质量审查和小游戏验证；
- `.codex-plugin/plugin.json` 提供可发现的插件入口与 UI 元数据。

### `tool-integrations`

- Integration 只映射外部工具能力，不重写工具本身；
- 替换 MCP 不改变 GameGraph 的公共查询语义；
- 第一个真实适配目标为 TapTapMakerMCP；
- 第二个真实适配目标为 Godot MCP；
- 工具不可用时，核心查询和文档能力仍然工作。
- CodeGraph 首版通过 `status/query/impact --json` 组合，不读取其 SQLite 或复制解析器；
- CodeGraph Provider 已完成本地 CLI 适配，MCP 原生桥接留待真实 Agent 宿主验证。
- TapTap Maker 已实现 `trial status/prepare/plan` 本地适配；live MCP 连接和可玩结果只由真实验证确认。

### `delivery-evidence`

- 默认关闭，普通修改不产生大量记录；
- 只在高风险功能、发布检查或用户显式要求时启用；
- 旧 GameMakerAgent 的 Production/Binding/Evidence 只选择性迁入；
- 不得反向成为 Core 的必需依赖。

## 明确排除

- 多 Agent 工作室编排；
- 通用代码 AST/调用图引擎；
- 游戏引擎远程控制实现；
- 素材生成服务；
- 自动写入未确认设计；
- 对所有任务强制 Production Card 和 Evidence Bundle。

## 当前验证切片

框架已经能把完成初始化的 TapTap Maker 项目准备到 `ready_for_live_validation`。下一步在独立游戏
项目中连接真实 Maker MCP，完成一个主要操作、一个可观察状态变化、一个成功目标和一次可重复运行，
再依据真实断点修正 Core、文档和 Skill。
