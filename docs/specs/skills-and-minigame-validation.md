# Skills and Minigame Validation Specification

## Objective

让 GameMakerGraph 以可安装、可发现的插件形式提供一组轻量开发 Skill，并把一个已经初始化的
TapTap Maker 本地项目准备到“可以由 Agent 连接 Maker MCP 开始小游戏实测”的状态。

本切片实现 `development-skills` 与首个 `tool-integrations` 验证入口，不在 Core 内复制 Maker MCP、
创建远端项目或伪造运行证据。

## Capability mapping

本规格落实已有 `CAPABILITY_MAP.md` 中两个已经确认的模块：

| Module | Deliverable | Depends on |
| --- | --- | --- |
| `development-skills` | 可发现的 Skill 插件与当前 Skill 目录 | `gamegraph-core`, `docs-framework` |
| `tool-integrations` | TapTap Maker 项目预检、准备和验证计划 | `gamegraph-core`, `docs-framework` |

## Skill set

首个可交付集合包含：

1. `game-project-exploration`：使用 GameGraph 与 CodeGraph 快速理解项目和功能影响；
2. `codegraph-documentation`：搭建前端、后端、玩法实现、测试与交付文档；
3. `game-project-bootstrap`：开发前先确定范围、拆分模块并建立最小文档；
4. `game-direction`：对玩法、剧情和范围做轻量讨论，保留人的创作主导权；
5. `game-art-direction`：先确定视觉基准、资产槽位和 UI 尺寸，再批量生成或替换；
6. `game-quality-review`：分别检查代码质量、性能、整体体验与试玩反馈；
7. `minigame-validation`：编排 TapTap Maker MCP 小游戏验证，不把工具调用成功当作游戏通过。

旧 GameMakerAgent 的 Skill 不原样复制：`studio-advisor` 收窄到 `game-direction`，`game-delivery` 的
最小闭环进入 `minigame-validation`，`evidence-review` 的完成判定进入 `game-quality-review` 与验证
Skill。用户提供的开发经验按上述职责提炼，不把某个示例游戏、剧情或资产清单写成通用事实。

每个 Skill 必须有独立 `SKILL.md` 和 `agents/openai.yaml`。插件必须包含
`.codex-plugin/plugin.json`，且 manifest 中的版本与 Python 包版本一致。

## Commands

```text
gamegraph trial status [PROJECT] [--provider taptap-maker]
gamegraph trial prepare [PROJECT] [--provider taptap-maker]
gamegraph trial plan [PROJECT] [--provider taptap-maker]
```

### `status`

只读检查：

- TapTap Maker 项目绑定标记 `.maker-mcp/config.json`；
- Maker 的基础 `scripts/` 与 `assets/` 目录；
- GameGraph 是否 current；
- 最小开发文档是否存在；
- 本地是否能找到 `taptap-maker` 或 `npx` 启动入口。

它必须把“本地项目已准备”和“当前 Agent 会话已经连接 MCP”分开。Core 无权把连接状态标记为
已验证。

### `prepare`

仅对已经存在 Maker 绑定标记的项目执行。先补齐缺失开发文档，再重建 GameGraph，已有文档不覆盖。
未初始化的目录返回 `blocked` 且不得写文件；不得自动运行登录、创建远端应用、clone、安装 MCP、
build 或 publish。

### `plan`

只读返回一个范围受控的验证契约：一个主要操作、一个可观察状态变化、一个成功目标、一次重启或
重试路径、零阻断诊断，以及开发后 GameGraph/文档新鲜度检查。它不指定具体玩法，不替代用户确认。

## Output contract

所有命令输出 JSON，包含稳定的 `schema_version`、`operation`、`provider`、`project_root`、检查结果、
准备状态和下一步。状态至少区分：

- `blocked`：Maker 项目尚未初始化或本地结构不完整；
- `preparation_required`：项目存在，但图或文档尚未准备；
- `ready_for_live_validation`：本地上下文已准备，仍需当前 Agent 会话真实连接 MCP；
- `validated` 不由本切片自动产生，必须来自后续真实运行证据。

## Testing strategy

- 文件系统测试覆盖未初始化、结构不完整和已绑定项目；
- 回归测试证明 `prepare` 不会在未初始化目录写文件；
- 集成测试证明准备顺序为文档初始化后再建图，最终 GameGraph 为 current；
- 打包测试检查插件 manifest、Skill 名称和 UI 元数据；
- CLI 测试检查 JSON 输出；
- 完成前运行全部 pytest、Ruff、所有 Skill 校验和插件校验。

## Boundaries

### Always

- 保持原生项目和 Maker 项目配置为真源；
- 只读取 Maker 配置是否存在，绝不输出认证内容；
- 区分本地准备、MCP 连接、游戏运行和人工体验判断；
- 对代码、玩法、资产和验证关系保留可追溯来源。

### Ask first

- 安装或升级 TapTap Maker；
- 登录、创建远端项目或选择账号下应用；
- 构建、上传或发布游戏；
- 将推断的玩法、剧情或审美方向写成确认事实。

### Never

- 把本地 marker 当作 MCP 已连接；
- 把 build、截图或文件存在当作小游戏验收通过；
- 在已绑定目录上重新创建或覆盖 Maker 项目；
- 把 Maker 原始工具名固化进 GameGraph Core。

## Success criteria

1. 仓库中可以直接看到并验证七个 Skill；
2. 插件 manifest 可被 Codex 插件校验器接受；
3. 未初始化目录执行 `prepare` 不产生任何文件；
4. 已初始化夹具执行 `prepare` 后具有最小文档和 current GameGraph；
5. `status` 明确说明 MCP live connection 仍未验证；
6. `plan` 给出可观察、可复验但不预设玩法的小游戏验收契约；
7. 实际 TapTap Maker 安装、登录、项目创建和运行保留给下一步真实验证会话。
