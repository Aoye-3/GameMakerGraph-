# 产品边界：GameMakerGraph

## 状态

Accepted as extraction baseline

## 背景

上一轮 GameMakerAgent 同时实现并验证了玩法顾问、项目扫描、Project Map、上下文裁剪、素材生产、
Godot Provider、运行证据和交付记录。它证明了本地文件、确认语义和运行结果可以建立可追踪关系，
但默认产品路径过于接近一套完整游戏生产流程，增加了独立开发者日常使用的认知与记录成本。

目标用户需要的首要能力不是虚拟工作室，而是让通用代码 Agent 快速理解本地游戏项目，并在修改前
获得可靠、有限、可追踪的代码和文档上下文。

## 决策

GameMakerGraph 定位为本地优先的游戏项目知识图谱与 Agent 增强框架。

1. GameGraph Core 与 Documentation Framework 是主要产品能力。
2. 开发方向讨论由按需 Skill 提供，保持轻量和非强制。
3. 引擎编辑、运行和素材生成复用已有 MCP、CLI 和生成工具。
4. GameGraph 连接游戏语义与本地实现，但不复制成熟通用代码图引擎。
5. 旧交付和证据能力移为可选扩展，不进入普通任务关键路径。
6. 首次真实验证使用 TapTapMakerMCP 完成小游戏；第二次使用 Godot 参加 TapTapGameJam。
7. 新实现从上一轮经过测试的扫描、图、新鲜度与上下文代码迁移，不另写一套平行原型。

## 与 CodeGraph 的关系

CodeGraph 提供代码符号、调用和依赖关系。GameMakerGraph 提供玩法、文档、场景、资源、资产、
测试和开发状态之间的游戏语义关系。两者可以组合：CodeGraph 是代码关系 Provider，GameGraph
是面向游戏开发任务的上层语义图。

## 后果

- Core 必须在没有任何 MCP 在线时仍可工作。
- 文档成为图中的一等来源，而不是 Production Card 的附件。
- 旧 Project Map 是新 Core 的实现起点，但必须解除 Production/Evidence 的默认耦合并加入文档节点。
- 新功能必须说明它改善了项目理解、文档搭建或开发前分析中的哪一个问题。
- 复杂交付验证仍可存在，但不得增加默认路径的摩擦。
