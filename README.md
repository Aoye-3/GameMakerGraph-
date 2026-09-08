# GameMakerGraph 0.6.0

GameMakerGraph 是给本地 Vibe Game 开发者的“项目持续记忆 + 下一步导航”。它尤其适合不会写代码、
或只具备少量代码经验、主要通过 Codex/Cursor/Claude 等 Agent 与游戏引擎工具协作的人。

它不是重型 Game Studio，也不替代游戏引擎、代码索引器或人的创作判断。它把项目里已经确认的玩法、
状态、规则、决定、里程碑、验收条件和验证证据，连接到真实文档与实现文件；下一次对话开始时，Agent
不必重新猜“这个游戏在做什么、做到哪里、下一步改哪里”。

## 核心价值

- 持续记忆：确认过的语义事实保存在标准 Markdown，而不是某次对话历史里。
- 下一步导航：开发前把自然语言目标收窄到局部事实、实现入口、确认问题与可观察验收。
- 有证据的闭环：开发后比较 revision、运行证据和文档，先预览维护计划，再由用户确认应用。
- 本地且可重建：`.gamemakergraph/graph.json` 是派生索引，随时可以删除和重建；Markdown 与原生项目
  文件才是真源。
- 对初学者友好：GameGraph 解释“为什么、现在是什么、下一步是什么”，外部 Maker/引擎工具负责
  “怎么执行、怎么构建、怎么运行”。

## 完整开发闭环

```text
探索本地代码与已有文档
        ↓
理解玩法、实现现状与索引新鲜度
        ↓
准备下一步最小增量（draft，不写图）
        ↓
用户确认 → confirm 写入契约并建立基线
        ↓
外部引擎 / TapTap Maker MCP 实现、构建和运行
        ↓
watcher 自动发现变化并标记 review_required
        ↓
收集同一版本的运行、试玩与诊断证据
        ↓
GameGraph review 生成确定性文档维护预览
        ↓
用户确认 → apply 只改受控区块并自动 rebuild
        ↓
图状态 current、证据可追溯、给出下一步
```

`prepare` 和 `review` 不修改 Markdown。候选建议不会直接进入图。只有用户确认后，`confirm` 才把
增量契约写入 `GAMEGRAPH:START/END` 受控区块。MCP 进程内 watcher 只自动维护
`.gamemakergraph/` 派生状态和索引，不静默确认产品语义，也不依赖 Sampling。进程关闭期间的变化在
下次 `inspect` 时补抓。

## GameGraph、CodeGraph 与 Maker 的分工

| 组件 | 负责 | 不负责 |
| --- | --- | --- |
| GameMakerGraph | 玩法、状态、规则、决定、里程碑、验收、证据、文档与下一步 | 运行游戏、生成构建、代替用户确认 |
| CodeGraph（可选） | 代码符号、调用关系、导入、实现与代码影响面 | 推断玩法意图、维护 GameGraph 文档 |
| TapTap Maker（独立 MCP） | Maker 项目状态、同步、实现执行、构建、预览/运行证据 | 充当项目长期语义记忆 |

建议搭配 [CodeGraph](https://github.com/colbymchenry/codegraph) 使用：GameGraph 回答“这个变化对游戏意味
着什么”，CodeGraph 回答“哪些符号和调用链实现它”。CodeGraph 不可用时核心功能仍能独立运行。

特别感谢 CodeGraph 项目提供的本地代码图思路。GameMakerGraph 不复制其解析器或私有数据库，只通过
公开 Provider 边界组合结果。详见 [CodeGraph Provider 契约](docs/contracts/codegraph-provider.md)。

GameMakerGraph MCP 不直接调用 Maker MCP。Agent 在同一会话中分别调用两者，避免 MCP 间隐式转发、
权限扩大和证据来源混淆。

## 语义模型

GameGraph 保留已有 artifact 层：项目、文件、文档、标题、场景、脚本、资源、数据、配置、资产和
revision。0.6.0 在既有语义模型上增加已确认增量生命周期和主动 Review 状态：

- 节点：`feature`、`player_action`、`game_state`、`rule`、`milestone`、
  `acceptance_criterion`、`decision`、`issue`、`validation_evidence`；
- 关系：`documents`、`implemented_by`、`depends_on`、`changes`、`validated_by`、`blocked_by`。

节点与证据路径始终使用项目相对路径。语义 ID 由节点类型和稳定 `key` 决定；改标签不会改变 ID。
非法节点、关系或越界路径只产生 warning，不会进入图。完整格式见
[语义模型](docs/specs/semantic-model.md)，可复制模板见
[project-memory.md](docs/development/project-memory.md)。

## 安装

要求 Python 3.11+。核心 CLI 没有第三方运行依赖；MCP 是可选 extra。

```powershell
git clone https://github.com/Aoye-3/GameMakerGraph-.git
cd GameMakerGraph-
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
```

macOS/Linux：

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -e '.[mcp]'
```

只用原有 Core/CLI 时可执行 `python -m pip install -e .`，未安装 MCP extra 也能继续使用
`gamegraph build/status/search/context/impact/docs/trial`。

仓库的 `.mcp.json` 由插件清单自动引用。若要手工注册到 Codex，可用实际虚拟环境入口：

```powershell
codex mcp add gamemaker-graph -- F:\path\to\GameMakerGraph\.venv\Scripts\gamegraph-mcp.exe
codex mcp list --json
```

安装或修改 MCP 配置后，Codex/Cursor/Claude 可能需要重启客户端、刷新 MCP 或新开会话，工具才会
可见。Python SDK v2 的服务端模式、工具 schema 和 Client 测试方式依据
[官方 MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/index.md)、
[Tools 文档](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/servers/tools.md)与
[Client transports 文档](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/client/transports.md)。

## 七个 MCP 工具

所有工具返回同一 envelope：

```json
{
  "schema_version": "0.6",
  "operation": "gamegraph_query",
  "status": "current",
  "project_root": "...",
  "revision": "sha256:...",
  "facts": {},
  "warnings": [],
  "next_actions": []
}
```

| 工具 | 输入 | 行为 |
| --- | --- | --- |
| `gamegraph_inspect_project` | `project_root` | 检查项目、Provider、活动增量和待 Review 状态 |
| `gamegraph_prepare_increment` | `project_root`, `goal` | 只读准备局部事实、代码上下文、问题和验收候选 |
| `gamegraph_confirm_increment` | `project_root`, `expected_revision`, `draft` | 用户确认后幂等持久化增量契约并建立基线 |
| `gamegraph_query` | `project_root`, `query`, `include_code=true` | 只读查询语义图，并按需组合 CodeGraph |
| `gamegraph_review_increment` | `project_root`, `increment_id`, `evidence=[]` | 复核已确认增量、证据缺口和维护预览 |
| `gamegraph_apply_maintenance` | `project_root`, `expected_revision`, `plan` | 幂等应用已确认计划并自动重建；revision 冲突拒绝 |
| `gamegraph_rebuild_index` | `project_root` | 非破坏、幂等，从闭合项目文件集合重建派生索引 |

`inspect`、`prepare`、`query`、`review` 带 MCP `readOnlyHint`；`confirm`、`apply`、`rebuild` 声明
`destructiveHint=false`、`idempotentHint=true`、
`openWorldHint=false`。这些 annotations 是客户端提示，不替代服务端自己的路径、revision 和计划校验。

### 示例

1. `gamegraph_inspect_project("F:/games/star-runner")`
2. `gamegraph_prepare_increment("F:/games/star-runner", "让玩家收集星星后分数增加")`
3. 用户确认 draft 后，将其原样传给 `gamegraph_confirm_increment`。
4. Agent 使用独立 Maker/引擎 MCP 实现并运行；watcher 自动标记待 Review。
5. 将同 revision 的项目相对证据和 `increment_id` 传给 review：

```json
{
  "project_root": "F:/games/star-runner",
  "increment_id": "increment:已确认增量 ID",
  "evidence": [
    {
      "path": "evidence/star-playtest.md",
      "kind": "playtest",
      "claim": "玩家实际碰到星星后分数从 0 变为 1",
      "result": "passed",
      "revision": "sha256:当前 GameGraph revision"
    }
  ]
}
```

6. 向用户展示 review 的 `facts.plan`；确认后把原计划原样传给 apply。
7. apply 自动 rebuild；再次 inspect 的结束条件是 Review 为 `documented/current`、图为 current、证据可追溯。

## Skills

插件包含 7 个可发现 Skills，均优先调用 0.6.0 MCP，MCP 不可用时才回退 CLI：

- [`game-project-exploration`](skills/game-project-exploration/SKILL.md)：开发前的局部项目与影响探索；
- [`codegraph-documentation`](skills/codegraph-documentation/SKILL.md)：连接玩法文档与代码符号；
- [`game-project-bootstrap`](skills/game-project-bootstrap/SKILL.md)：收窄首个可玩闭环和最小文档；
- [`game-direction`](skills/game-direction/SKILL.md)：保留创作者主导的玩法/叙事/范围讨论；
- [`game-art-direction`](skills/game-art-direction/SKILL.md)：视觉基准、资产槽位和可替换集成计划；
- [`game-quality-review`](skills/game-quality-review/SKILL.md)：代码、文档、运行证据与体验分层复核；
- [`minigame-validation`](skills/minigame-validation/SKILL.md)：编排真实 Maker 小游戏闭环。

## TapTap Maker 前置与验收

Maker 是独立工具。按 TapTap 官方流程先安装客户端配置：

```bash
npx -y @taptap/maker install --ide codex,cursor,claude
```

然后在一个空白游戏目录执行：

```bash
npx -y @taptap/maker init
```

安装后可能需要重启或重连客户端。官方 Maker 说明见
[TapTap instant-games-open-mcp](https://github.com/taptap/instant-games-open-mcp) 和
[Maker 文档](https://github.com/taptap/instant-games-open-mcp/blob/main/docs/MAKER.md)。

真实验收顺序是：自然语言目标 → GameGraph prepare → 用户确认并 confirm → Maker 实现/构建 →
watcher 标记待 Review → 真实预览与玩家操作 → 同一 revision 的状态/诊断证据 → GameGraph review →
用户确认 → apply 自动 rebuild。构建成功、截图、
文件存在或 MCP 调用成功都不能单独证明玩法通过；必须观察玩家操作导致的状态变化，并让玩家/用户确认
体验结论。详见 [TapTap Maker 闭环验收](docs/validation/taptap-maker-loop.md)。

## 安全边界

- 只接受存在的本地项目根；所有语义节点和证据路径必须是项目相对路径，拒绝绝对路径和 `..` 越界。
- 只检查 `.maker-mcp/config.json` 是否存在，永不读取、记录或输出其内容。
- `prepare` 与 `review` 不修改 Markdown；候选、推断和未确认创意不进入图。
- watcher 只写 `.gamemakergraph/` 派生状态和索引，不能把推断提升为已确认事实。
- confirm/apply 只允许维护 `docs/development/project-memory.md` 的标记区块，保留人工内容。
- apply 校验确定性 `plan_id` 与 `expected_revision`；冲突零写入，重复计划返回 `unchanged`。
- watcher/rebuild 只写 `.gamemakergraph/`，相同输入不会二次写入。
- 不自动安装/初始化 CodeGraph，不读取 `.codegraph` 私有数据库。
- 不自动调用 Maker、不登录、不创建远端应用、不上传或发布。

## Core CLI

原有 CLI 继续受支持：

```text
gamegraph build [PROJECT]
gamegraph overview [PROJECT]
gamegraph search QUERY [PROJECT]
gamegraph context QUERY [PROJECT] [--no-codegraph]
gamegraph impact ROOT_ID [PROJECT] [--code-symbol SYMBOL] [--no-codegraph]
gamegraph status [PROJECT]
gamegraph docs inspect|suggest|init|check [PROJECT]
gamegraph trial status|prepare|plan [PROJECT] --provider taptap-maker
```

## 开发与验证

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe C:\path\to\skill-creator\scripts\quick_validate.py skills\<name>
.\.venv\Scripts\python.exe C:\path\to\plugin-creator\scripts\validate_plugin.py .
gamegraph build .
gamegraph status .
codegraph status . --json
```

测试覆盖原有 Core/CLI、语义节点与稳定 ID、证据与非法关系、候选不入图、stale、四个只读工具、
受控维护、冲突与幂等、Maker 配置保密，以及 MCP SDK v2 的进程内 Client 和真实 stdio 子进程。

## 路线图

- 0.6.x：用真实 Maker 小游戏持续验证自动监测、主动 Review 和跨窗口恢复。
- 后续候选：更细的语义查询排序、项目自定义闭合文档集合、更多引擎 Provider 适配。
- 明确不在当前版：PyPI 发布、自包含运行时、MCP 间转发、系统级常驻服务、完整美术/UI/叙事本体、
  图形化 Game Studio。

## 许可证

MIT
