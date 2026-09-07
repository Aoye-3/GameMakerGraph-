# TapTap Maker 完整闭环验收

## 前置

在客户端安装 Maker：

```bash
npx -y @taptap/maker install --ide codex,cursor,claude
```

在空白游戏目录初始化：

```bash
npx -y @taptap/maker init
```

安装后按客户端情况重启、刷新或重连 MCP。GameMakerGraph 只检查 Maker marker 是否存在，不读取内容，
也不把 marker 当作当前会话已经连接 Maker 的证明。

## 验收步骤

1. inspect：确认目标项目、GameGraph/CodeGraph 状态和 Maker marker。
2. prepare：输入一个自然语言小游戏目标，记录开发前 revision。
3. 人工确认：限定一个主要玩家动作、一个可见状态变化、一个成功结果和明确排除项。
4. Maker：核对 live project identity，再实现并构建当前目录。
5. 运行：在真实预览中执行玩家动作；记录动作前后状态、成功结果、重启/重试与同一运行诊断。
6. 人工试玩：用户确认是否真的可玩、反馈是否清晰；无法试玩时结果必须是 insufficient evidence。
7. review：提交项目相对 evidence；逐条报告 supported/failed/insufficient。
8. 维护确认：展示完整确定性 plan，用户确认后 apply。
9. rebuild：重建后 inspect/query，要求 GameGraph 为 current，证据节点可追溯。
10. 下一步：只给出一个新的最小增量，不自动开始。

## 证据最低要求

- 真实运行身份与当前源码 revision 对应；
- 玩家输入或操作轨迹；
- 操作前后可观察的状态变化；
- 玩家可见结果；
- 同一运行的阻断诊断；
- 玩家/用户体验结论。

构建成功只证明可构建，截图只证明一个画面，文件存在只证明产物存在。三者都不能单独证明玩家动作、
隐藏状态或完整玩法目标通过。
