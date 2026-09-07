# GameMakerGraph MCP 契约

## 运行时

入口 `gamegraph-mcp` 使用官方 Python MCP SDK 2.x 的 `MCPServer` 和 stdio transport。类型注解生成输入
schema，Python dict 作为 structured output。实现参考官方
[SDK v2 文档](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/index.md)与
[工具 annotations](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/servers/tools.md)。

## Envelope

六个工具的成功、冲突、缺失和边界错误都返回八个固定顶层字段：`schema_version`、`operation`、
`status`、`project_root`、`revision`、`facts`、`warnings`、`next_actions`。错误不会把任意输入文件内容
复制到 warning。

## 工具语义

| 工具 | 只读 | 说明 |
| --- | --- | --- |
| inspect | 是 | 文档/图/Provider/Maker marker 状态 |
| prepare | 是 | 当前目标的事实、问题和验收候选；candidate_persistence=none |
| query | 是 | 当前或内存派生的局部匹配，可选 CodeGraph |
| review | 是 | 基线与当前 artifact 差异、证据清洗、确定性计划 |
| apply | 否 | 用户确认后唯一受控文档写入；非破坏、幂等、闭合世界 |
| rebuild | 否 | 唯一派生索引写入；非破坏、幂等、闭合世界 |

## 冲突与幂等

review 要求 `base_revision` 对应当前持久索引，否则返回 conflict。apply 重新计算计划哈希，并先识别已
应用 `plan_id`；已应用返回 unchanged。新计划只有在 `expected_revision` 等于实时 revision 时才写入。
apply 不隐式 rebuild，以便调用者清楚看到 stale → current 的状态转换。

## 路径与秘密

项目根在工具边界解析并要求存在。图节点 source、实现映射和 evidence path 全部是项目相对路径。
`.maker-mcp/config.json` 只通过 `is_file()` 检查存在性，任何工具都不得打开或输出其内容。
