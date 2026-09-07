# TapTap Maker Integration Notes

Date checked: 2026-09-07

## Upstream facts

TapTap 官方的 `taptap/instant-games-open-mcp` 仓库将 Maker 本地开发发布为 `@taptap/maker`。
官方流程以 `taptap-maker init` 初始化或选择项目，成功后写入 `.maker-mcp/config.json`，并提供
`doctor`、`apps --json`、`mcp verify` 等 CLI 入口。Maker MCP 负责当前 Agent 宿主中的真实工具
连接与执行；本地项目切换不应通过给全局 MCP 配置写死 `cwd` 完成。

Sources:

- [TapTap instant-games-open-mcp](https://github.com/taptap/instant-games-open-mcp)
- [TapTap Maker local development](https://github.com/taptap/instant-games-open-mcp/blob/main/docs/MAKER.md)
- [TapTap Maker NPM package](https://www.npmjs.com/package/@taptap/maker)

## GameMakerGraph boundary

GameMakerGraph 不内嵌 Maker runtime，也不读取或重写其认证配置。首个适配只使用三个稳定事实：

1. `.maker-mcp/config.json` 表示目录已经完成项目绑定，不表示 MCP 当前在线；
2. `scripts/` 与 `assets/` 是 Maker 本地项目的基础开发表面；
3. 真实连接必须由当前 Agent 宿主通过 Maker status/doctor 类能力确认。

因此 `gamegraph trial` 只负责准备和描述验证：补齐最小文档、建立 GameGraph、给出范围受控的验收
计划。安装、OAuth、远端应用创建、构建和发布仍由官方 CLI/MCP 执行，并遵守用户确认边界。

## First live trial

首个实测应选择一个独立 Maker 项目，范围只包含：

- 一个主要玩家操作；
- 一个能够从运行状态观察的变化；
- 一个明确成功目标；
- 一个可重复开始的路径；
- 当前运行截图或预览、输入/操作记录和无阻断诊断；
- 修改后重新生成的 current GameGraph 与对应实现文档。

不要用空白占位项目、单次生成成功、build 成功或 MCP 调用成功替代玩家可见闭环。
