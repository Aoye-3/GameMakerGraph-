# GameGraph 0.6 语义模型

## 来源格式

语义事实只从 Markdown 行级 `GAMEGRAPH:START` 与 `GAMEGRAPH:END` HTML 注释标记之间的单个 JSON
代码块读取。对象包含 `nodes`、`edges`、`applied_plans` 三个数组。标记外的 JSON、表格、标题和自然
语言永不被提升为语义事实。

节点最少包含：

```json
{"key": "collect-star", "kind": "feature", "label": "Collect a star"}
```

`key` 是项目内稳定身份；`label` 可以修改。ID 由 kind 与规范化 key 确定。`source` 由解析器设为承载
区块的项目相对 Markdown 路径，调用者不能注入绝对来源。

## 节点

| kind | 用途 |
| --- | --- |
| `feature` | 玩家或系统可感知的能力 |
| `player_action` | 玩家可执行的动作 |
| `game_state` | 会变化且影响玩法的状态 |
| `rule` | 约束状态变化或结果的规则 |
| `milestone` | 有边界的开发到达点 |
| `acceptance_criterion` | 可观察、可复验的完成条件 |
| `decision` | 已确认且影响实现的选择 |
| `issue` | 当前阻塞或缺陷 |
| `validation_evidence` | 指向项目相对证据的声明 |

artifact 节点继续由原生文件扫描生成，包括 document、scene、script、resource、data、config、asset。

## 关系

- `documents`：语义节点 → Markdown artifact；
- `implemented_by`：除 evidence 外的语义节点 → 实现 artifact；
- `depends_on`：语义依赖，或语义节点依赖 artifact；
- `changes`：feature/player_action/decision → feature/game_state/rule/milestone；
- `validated_by`：可验收语义节点 → validation_evidence；
- `blocked_by`：非 evidence 语义节点 → issue。

关系端点不存在、类型组合不合法、自指或越界路径都会产生 warning，且不进入图。

## 证据

证据可以记录 `kind`、`claim`、`result`、`observed_at`、`tool`、`revision` 与 `path`。若有 path，它必须是项目
相对路径，不能是绝对路径或包含 `..`。构建日志、截图或文件存在只支持其直接声明；“玩法通过”仍需
同一 revision 的实际运行、玩家输入、可观察状态变化和人工体验确认。只有 `playtest` 或
`user_confirmation` 的 passed 证据可以验证玩法；build/runtime 证据只支持其直接声明。
输入 evidence 的 `kind` 在语义节点中保存为 `evidence_kind`，节点自身的 kind 始终是
`validation_evidence`。
