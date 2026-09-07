# Documentation Framework Specification

## Objective

为本地游戏项目提供可裁剪、可检查、不会覆盖创作事实的开发文档搭建流程，使通用编程 Agent
能够从项目定位和玩法规则导航到场景、资源、前后端代码、测试与交付入口。

首版提供四个独立命令：

```text
gamegraph docs inspect [PROJECT]
gamegraph docs suggest [PROJECT]
gamegraph docs init [PROJECT]
gamegraph docs check [PROJECT]
```

## Inputs and detection

输入是本地项目根目录。检测只依赖文件系统与当前 GameGraph，不要求 CodeGraph 或引擎 MCP 在线。

项目能力信号：

| Capability | Evidence examples |
| --- | --- |
| game | `project.godot`, `.unity`, `.uproject`, scenes/assets directories |
| frontend | `package.json` plus `src`, `app`, `pages`, `components` or web entry files |
| backend | `server`, `backend`, `api`, framework manifests or server entry files |
| delivery | workflow, container, build/export or deployment configuration |

检测结果只说明仓库存在相应技术表面，不推断产品方向或部署策略。

## Minimal document set

所有项目建议：

- `docs/README.md`：文档导航、状态和维护规则；
- `docs/product/overview.md`：项目定位、目标用户/玩家和范围；
- `docs/architecture/overview.md`：组件边界、入口和数据流；
- `docs/development/setup.md`：本地开发与运行方式；
- `docs/development/testing.md`：自动化、运行时和人工验证入口；
- `docs/development/project-memory.md`：确认后的玩法语义、决定、验收与证据受控区块；
- `docs/architecture/implementation-map.md`：概念到文件、符号和验证的映射。

检测到游戏项目时增加 `docs/product/gameplay.md`。检测到 frontend、backend 或 delivery 时，分别增加
`docs/architecture/frontend.md`、`docs/architecture/backend.md`、`docs/delivery/release.md`。

## Operations

### `inspect`

返回项目能力、现有 Markdown 文件、建议文件的存在状态、GameGraph 状态和统计。不写文件。

### `suggest`

返回最小建议集、每个建议的证据和原因。已存在文件保留在结果中但标记 `existing`。不写文件。

### `init`

创建缺失的建议目录和 Markdown 文件；已有文件返回 `preserved`，内容和时间戳不得改变。所有新模板
必须区分：

- `Confirmed`：只能由已存在来源或用户确认填写；
- `To confirm`：创作、产品和架构未知项；
- `Implementation map`：路径和符号的可追溯关系。

命令不得运行 CodeGraph、修改代码或自动执行构建/发布。

### `check`

返回结构问题：缺失建议文档、项目内 Markdown 断链、仍未确认的模板项、空的实现映射，以及
GameGraph stale/missing 状态。检查结果分为 `error`、`warning`、`info`，不修改文件。

## Output contract

所有命令输出 JSON，至少包含：

```json
{
  "schema_version": "0.1",
  "operation": "inspect",
  "project_root": "...",
  "project_capabilities": ["game"],
  "documents": [],
  "issues": []
}
```

输出中的文档路径必须相对项目根；内部实现不得把项目外路径写入模板。

## Project structure

```text
src/gamemaker_graph/docs.py       detection, suggestions, templates, checks
src/gamemaker_graph/cli.py        docs command routing
tests/test_docs_framework.py      filesystem behavior and safety tests
docs/specs/                       this contract
```

## Code style

使用现有 Python 3.11、标准库和 JSON 输出约定。模板为模块内受控常量或小型渲染函数；不增加模板
引擎依赖。

## Testing strategy

- 小型文件系统测试验证能力检测、建议集和检查规则；
- 集成测试验证 `init` 后 `inspect/check` 的完整状态；
- 回归测试证明 `init` 不覆盖已有文档；
- CLI 测试验证机器可读 JSON；
- 完成前运行全部 pytest、Ruff 和真实目录冒烟验证。

## Boundaries

### Always

- 使用项目相对路径；
- 保留现有文档；
- 把创作未知项保持为待确认；
- 根据实际仓库能力裁剪文档；
- 将 GameGraph 新鲜度暴露给调用者。

### Ask first

- 改写已有文档；
- 将推断升级为已确认事实；
- 添加项目专属流程、团队角色或发布策略。

### Never

- 自动生成完整 GDD；
- 编造玩法、剧情、美术或用户需求；
- 自动运行外部 MCP、部署或发布；
- 把模板完成度当作游戏质量证据。

## Success criteria

1. 通用、Godot 和含前后端信号的项目获得不同的最小建议集；
2. `inspect`、`suggest` 和 `check` 无文件写入；
3. `init` 创建缺失文档且不覆盖任何已有内容；
4. `check` 能识别缺失文档、断链、待确认项和空实现映射；
5. 所有输出路径稳定、相对、确定性排序；
6. 功能不依赖 CodeGraph、MCP 或第三方 Python 包。

## Deferred

- 基于 CodeGraph 自动填充符号映射；
- 基于 GameGraph 关系生成候选实现映射；
- 项目自定义文档策略文件；
- 文档漂移的 revision 级验证；
- 非 Markdown 文档格式。
