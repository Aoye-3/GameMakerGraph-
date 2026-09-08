# Changelog

## [0.6.0] - 2026-09-08

### Added

- 用户确认后、编码前持久化的 Increment Contract，以及跨 MCP 窗口恢复。
- 标准库本地 monitor、派生 Review 状态和离线变化补抓。
- 主动 Review findings、证据分级和 `gamegraph_confirm_increment` MCP 工具。

### Changed

- 文档应用后自动重建 GameGraph，并闭合为 `documented/current`。
- 代码变化只标记 `implemented_unverified`；同 revision 的试玩或用户确认才能验证玩法。
- MCP envelope、插件和文档契约升级到 0.6。

### Security

- watcher 只维护 `.gamemakergraph` 派生文件，不读取 Maker 配置内容或静默确认语义。
- 证据类型、项目相对路径和 revision 在 Review 边界校验。

## [0.5.0] - 2026-09-08

### Added

- 九类持续记忆语义节点、六类关系和受控 Markdown 解析。
- 六工具本地 stdio MCP、统一 envelope、revision-safe 维护与幂等重建。
- MCP SDK v2 进程内与真实 stdio 集成测试。
- 持续记忆、语义模型、MCP 契约、Maker 验收文档与 project-memory 模板。

### Changed

- 七个开发 Skills 优先使用新 MCP 闭环。
- 中文 README 聚焦“游戏项目持续记忆 + 下一步导航”。

### Security

- Maker 配置内容永不读取或输出；语义与证据路径限制为项目相对路径。
- 文档应用限制为用户确认的闭合受控区块，并拒绝 stale revision。
