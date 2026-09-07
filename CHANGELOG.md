# Changelog

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
