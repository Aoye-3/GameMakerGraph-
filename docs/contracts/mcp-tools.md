# GameMakerGraph MCP 契约

## 运行时

入口 `gamegraph-mcp` 使用官方 Python MCP SDK 2.x 的 `MCPServer` 和 stdio transport。类型注解生成输入
schema，Python dict 作为 structured output。实现参考官方
[SDK v2 文档](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/index.md)与
[工具 annotations](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/servers/tools.md)。

## Envelope

七个工具的成功、冲突、缺失和边界错误都返回八个固定顶层字段：`schema_version`、`operation`、
`status`、`project_root`、`revision`、`facts`、`warnings`、`next_actions`。错误不会把任意输入文件内容
复制到 warning。

## 工具语义

| 工具 | 只读 | 说明 |
| --- | --- | --- |
| inspect | 是 | 文档/图/Provider/Maker marker、活动增量和 Review 状态 |
| prepare | 是 | 当前目标的事实与确定性 draft；candidate_persistence=none |
| confirm | 否 | 用户确认后幂等持久化 draft，并建立实现基线 |
| query | 是 | 当前或内存派生的局部匹配，可选 CodeGraph |
| review | 是 | 已确认增量与当前 artifact 差异、证据分级、findings 和确定性计划 |
| apply | 否 | 用户确认后受控文档写入并自动重建；非破坏、幂等、闭合世界 |
| rebuild | 否 | 唯一派生索引写入；非破坏、幂等、闭合世界 |

## 冲突与幂等

confirm 要求 draft 的确定性 `increment_id` 和 `expected_revision` 匹配。review 只接受活动中的已确认
`increment_id`。apply 重新计算计划哈希，并先识别已
应用 `plan_id`；已应用返回 unchanged。新计划只有在 `expected_revision` 等于实时 revision 时才写入。
apply 自动 rebuild，并将活动增量闭合为 `documented/current`。

## 主动 Review

MCP 进程第一次访问项目时注册 watcher。受支持文件变化经防抖后自动重建派生图，并在
`.gamemakergraph/review-state.json` 标记 `review_required`。MCP 关闭期间的变化由下一次 inspect 同步
发现。代码变化最多证明 `implemented_unverified`；同 revision 的 passed playtest 或
user_confirmation 才能把结果提升为 `validated`。

若派生 Review 状态被删除，inspect 从 confirmed Markdown 恢复活动增量，并明确返回
`baseline_recovered` 警告；无法重建的历史路径不得猜测。

## 路径与秘密

项目根在工具边界解析并要求存在。图节点 source、实现映射和 evidence path 全部是项目相对路径。
`.maker-mcp/config.json` 只通过 `is_file()` 检查存在性，任何工具都不得打开或输出其内容。
