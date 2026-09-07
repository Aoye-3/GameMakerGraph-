# 持续记忆架构

## 目标

GameMakerGraph 把跨会话需要保留的项目事实放在项目自己的 Markdown 中，把可删除的关系索引放在
`.gamemakergraph/graph.json`。它解决的是上下文连续性和下一步导航，不保存聊天历史，也不接管引擎。

## 三层

1. 真源层：原生代码、场景、资源、资产、配置、人工文档和运行证据。
2. 语义层：受控 Markdown 中已确认的玩法、状态、规则、决定、里程碑、验收和证据。
3. 派生层：GameGraph 文件/语义关系与可选 CodeGraph 符号关系。

事实流向只能是“真源或用户确认 → Markdown → rebuild → 派生图”。prepare 的候选、Agent 推断或旧
索引不能绕过 Markdown 直接成为语义事实。

## revision 与并发

revision 是规范化项目相对路径和文件内容 SHA-256 的组合。prepare 返回开发前 revision；review 用
持久索引保存的 revision 作为基线，比较当前 artifact 哈希并生成维护计划。apply 同时校验计划内容哈希
形成的 `plan_id` 和 review 时的 `expected_revision`。任一不匹配都零写入。

重复应用已记录的 `plan_id` 返回 `unchanged`，即使调用者仍携带应用前 revision。apply 之后索引必然
stale，直到显式 rebuild。rebuild 的输出内容相同时不替换索引文件。

## 写入边界

当前闭合世界只允许 apply 修改 `docs/development/project-memory.md` 的 GAMEGRAPH 标记区块。区块外
标题、说明、笔记和链接保持原样。服务端不会调用 Sampling、后台任务或其他 MCP 来扩大写入范围。

## Provider

CodeGraph 是可选只读代码 Provider；TapTap Maker 是独立执行 Provider。GameMakerGraph 只返回它们的
状态或经规范化的公开结果，不读取私有索引或 Maker 配置内容，也不代理它们的写操作。
