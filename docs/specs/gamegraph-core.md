# GameGraph Core Specification

## Status

- Version: `0.1`
- State: first executable slice
- Scope: local project discovery, disposable graph, overview, search, freshness

## Problem

通用编码 Agent 可以读取文件，却缺少一份稳定、局部、带来源的游戏项目结构视图。反复全文搜索会
浪费上下文，也无法直接连接开发文档与场景、脚本、资源之间的关系。

GameGraph Core 必须从本地项目原生文件生成可删除、可重建的索引。索引不是新的事实源；无法由
文件证明的玩法意图不得写入图中。

## Inputs

- 一个本地项目根目录；
- 根目录下受支持的开发文档、代码、场景、资源、配置和数据文件；
- 文件中明确存在的 Markdown 相对链接或 `res://` 引用。

首片不要求 `project.godot` 存在，也不要求 MCP、编辑器或网络在线。

## Outputs

默认输出目录为项目内的 `.gamemakergraph/`：

- `graph.json`：确定性排序的节点、关系、警告与源 revision；
- 查询结果：JSON 格式的 `overview`、`search` 与 `status`。

`.gamemakergraph/` 是派生缓存，删除后必须能从原生文件重建。

## Node model

首片包含：

- `project`：当前项目根；
- `document`：Markdown 文档；
- `heading`：Markdown 标题，用于把文档结构变为可查询语义；
- `scene`、`script`、`resource`、`data`、`config`、`asset`：本地文件。

每个节点至少包含稳定 `id`、`kind`、`label` 和相对 `source`。文件节点包含内容摘要哈希，不能
存储项目外路径。

## Edge model

首片包含：

- `contains`：项目包含文件；
- `declares`：Markdown 文档声明标题；
- `links_to`：Markdown 相对链接指向项目内文件；
- `references`：文本文件中的 `res://` 引用指向项目内文件。

每条边必须记录证据来源。无法解析或越出项目根的引用不得创建边，并产生可读 warning。

## Freshness

revision 是按规范化相对路径和文件内容计算的 SHA-256。相同输入必须生成相同 revision、节点和
关系；任何已索引文件内容变化必须使现有图返回 `stale`。

扫描必须忽略 `.git/`、`.gamemakergraph/`、常见依赖/构建缓存和隐藏目录，避免索引递归污染。

## Queries

### `build`

扫描项目并原子写入索引，返回 `current` 状态和图统计。

### `overview`

读取当前图，返回项目类型、revision、各节点类型数量、关系数量与 warning。若图已过期，查询必须
显式返回 `stale`，不能伪装为当前结果。

### `search`

对节点的标签、来源和结构化细节执行大小写不敏感的词项匹配，返回有上限、确定性排序的结果。

### `status`

对比当前原生文件 revision 与索引 revision，返回 `missing`、`current` 或 `stale`。

## Command line

```text
gamegraph build [PROJECT]
gamegraph overview [PROJECT]
gamegraph search QUERY [PROJECT]
gamegraph status [PROJECT]
```

所有命令输出 JSON，便于人类、Skill 和 MCP 适配层复用。

## Acceptance criteria

1. 非 Godot 本地目录可完成建图与查询；
2. Godot 场景、脚本和 `res://` 引用可识别；
3. Markdown 文档、标题和相对链接可识别；
4. 相同输入连续构建产生等价图；
5. 修改已索引文件后状态变为 `stale`；
6. 索引自身、隐藏目录和常见依赖目录不会进入图；
7. Core 没有 MCP、游戏项目记录或重型交付流程依赖。

## Deferred

- bounded task context 与多跳 impact 查询；
- 文档缺口和实现漂移规则；
- CodeGraph 或引擎 MCP 数据适配；
- watch 模式与增量更新；
- 图可视化；
- 可选交付证据。
