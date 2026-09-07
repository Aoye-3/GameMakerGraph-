# GameMakerGraph Skills

当前独立仓库直接在根目录 `skills/` 发布七个 Skill，并由
`.codex-plugin/plugin.json` 声明为一个 Codex 插件。

| Skill | 用途 | 来源与收窄方式 |
| --- | --- | --- |
| [`game-project-exploration`](../../skills/game-project-exploration/SKILL.md) | 快速理解项目、功能上下文与影响 | GameGraph/CodeGraph 查询流程 |
| [`codegraph-documentation`](../../skills/codegraph-documentation/SKILL.md) | 搭建玩法到前后端代码的技术文档 | 新增的 CodeGraph 组合能力 |
| [`game-project-bootstrap`](../../skills/game-project-bootstrap/SKILL.md) | 开发前定范围、拆模块、建最小文档 | 用户提供的框架先行与渐进开发经验 |
| [`game-direction`](../../skills/game-direction/SKILL.md) | 轻量玩法、剧情、体验和范围讨论 | 旧 `studio-advisor` 的收窄版本 |
| [`game-art-direction`](../../skills/game-art-direction/SKILL.md) | 视觉基准、资产槽位、变体和 UI 占位 | 用户提供的美术一致性经验 |
| [`game-quality-review`](../../skills/game-quality-review/SKILL.md) | 代码、性能、文档、运行和试玩复核 | 旧 `evidence-review` 的轻量完成判定 |
| [`minigame-validation`](../../skills/minigame-validation/SKILL.md) | 使用真实游戏 MCP 验证一个可玩闭环 | 旧 `game-delivery` 的最小实测闭环 |

## 旧 Skill 在哪里

上一轮 GameMakerAgent 的 `studio-advisor`、`game-delivery` 和 `evidence-review` 仍保留在外层旧框架
的 `plugins/gamemaker-agent/skills/` 中，也可能由工作区注入到 `.agents/skills/`。独立
GameMakerGraph 首轮抽离时只迁入了 `codegraph-documentation`，所以此前在新目录里看不到其余
Skill。本目录是收窄后的正式集合，不把旧重型流程整份复制回来。

## 用户经验如何进入 Skill

- “框架和文档先行、拆小模块、渐进实现”进入 `game-project-bootstrap`；
- “核心剧情由人写，AI 查漏补缺并人工复核”进入 `game-direction`；
- “先定美术基准稿、再批量生成，UI 先按尺寸留槽位”进入 `game-art-direction`；
- “功能完成后检查代码质量与性能，但不要盲从全面审查”进入 `game-quality-review`；
- “最终以真实试玩和玩家反馈为准”同时进入 `game-quality-review` 与 `minigame-validation`。

这些规则保留方法，不携带截图中的具体游戏名称、剧情、资产内容或未确认偏好。
