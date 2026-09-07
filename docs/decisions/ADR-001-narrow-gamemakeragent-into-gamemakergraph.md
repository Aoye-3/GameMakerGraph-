# ADR-001：在上一轮框架基础上收窄为 GameMakerGraph

## 状态

Accepted

## 日期

2026-09-07

## 背景

上一轮 GameMakerAgent 已完成本地 Godot 项目扫描、Project Map、上下文裁剪、Schema、Skill
路由、素材交接、Provider 探测和 Evidence Review，并通过框架回归与真实项目试跑。

这些能力证明“游戏语义—本地实现—开发记录”可以形成可查询关系，但把完整生产交付链作为默认
路径，会让独立开发者的普通 Vibe Game 编程承担过多流程和记录成本。用户真正需要的首要体验是：
快速理解项目、开发前分析影响、搭建并维护开发文档，以及在需要时进行轻量方向讨论。

## 决策

1. 产品更名为 GameMakerGraph，独立发布根为 `GameMakerGraph-/`。
2. GameGraph Core 和 Documentation Framework 成为主要产品能力。
3. 从上一轮实现迁移项目扫描、revision、Project Map、impact、Context Pack、Schema 和测试。
4. Project Map 演进为 GameGraph；Markdown 文档成为一等图节点。
5. Studio Advisor 收窄为轻量方向讨论，不进入普通代码查询路径。
6. Production、Asset Binding、Provider Conformance 和 Evidence Review 降为可选扩展。
7. 引擎编辑和运行复用 TapTapMakerMCP、Godot MCP 等现有工具。
8. 第一阶段用 TapTapMakerMCP 完成小游戏；第二阶段用 Godot 参加 TapTapGameJam。

## 未采用方案

### 从零重写新框架

会丢失上一轮已验证的新鲜度、影响查询和测试资产，并重复制造相同缺陷，因此拒绝。

### 只做全局改名

会保留重型生产流程和旧产品假设，无法体现新的用户价值，因此拒绝。

### 继续扩展完整 GameStudio 流程

会增加常驻角色、阶段和上下文成本，不符合独立开发者的本地开发方式，因此拒绝。

## 后果

- 迁移必须能指出旧实现来源和保留的测试；
- 默认命令围绕 overview、search、context、impact、docs 和 status；
- 高风险证据机制仍可复用，但不会绑架普通开发；
- 旧仓库继续作为迁移来源和历史证据，新目录形成独立产品边界；
- 新增能力必须证明它改善项目理解、文档搭建或开发前分析。
