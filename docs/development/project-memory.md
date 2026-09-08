# Project Memory

Status: template

本文件是 GameMakerGraph 维护持续项目记忆的标准模板。人工说明、设计笔记和链接放在标记区块之外；
只有用户确认过的 draft 或维护计划才能通过 `gamegraph_confirm_increment` 或
`gamegraph_apply_maintenance` 合并到受控 JSON。

## Human notes

- 在这里记录不应由工具覆盖的背景、创作解释或维护约定。

## Managed facts

<!-- GAMEGRAPH:START -->
```json
{
  "nodes": [],
  "edges": [],
  "applied_plans": []
}
```
<!-- GAMEGRAPH:END -->

## Maintenance rule

候选事实先预览；用户确认后 confirm/apply；派生图自动 rebuild。不要把推断写成已确认事实。
