# AI Coding Agent 的行为操作系统：从 Memory 到 Harness 的全景指南

> 每个 AI coding agent 都有一个"行为控制系统"——让你决定它怎么工作。本文从 Claude Code 的 memory 机制出发，横跨 10+ 个主流框架，揭示这个领域正在发生的范式转移。

## 一、一个真实的踩坑故事

我有一个多项目 workspace，十几个独立项目。每次开新会话，Claude Code 都像"失忆"一样——不记得项目架构、不记得上次做到哪、不记得我的工作流偏好。

于是我开始用 memory。但第一次就踩了坑：**我把 memory 文件放错了位置。**

```
❌ 项目根目录/memory/                    ← 我以为的位置
✅ ~/.claude/projects/<encoded-path>/memory/  ← 实际位置
```

这个错误让我重新思考：**AI agent 的行为控制到底该怎么设计？**

带着这个问题，我调研了 Claude Code、OpenAI Codex、Cursor、Cline、Windsurf、GitHub Copilot、Kiro、OpenClaw 等 10+ 个框架。结论是：这个领域正在从"写规则"演进到"装操作系统"。

## 二、行为控制的四层模型

分析所有主流框架后，我发现 AI agent 的行为控制可以分为四层：

```
┌─────────────────────────────────────────────────┐
│  身份层：你是谁                                  │  SOUL.md、角色定义
├─────────────────────────────────────────────────┤
│  规则层：如何工作                                │  AGENTS.md、CLAUDE.md
├─────────────────────────────────────────────────┤
│  技能层：能做什么                                │  SKILL.md、scripts/
├─────────────────────────────────────────────────┤
│  记忆层：记住什么                                │  MEMORY.md、memories/
└─────────────────────────────────────────────────┘
```

| 层 | 解决的问题 | 典型文件 | 加载策略 |
|---|-----------|---------|---------|
| 身份层 | AI 的角色和性格 | SOUL.md | 始终加载 |
| 规则层 | 编码规范、工作流约定 | AGENTS.md / CLAUDE.md | 始终加载 |
| 技能层 | 特定任务的执行能力 | SKILL.md | 按需加载 |
| 记忆层 | 跨会话的连续性 | MEMORY.md | 始终加载 |

**关键洞察：大多数项目只用了"规则层"，忽略了其他三层。** 而真正高效的 harness 是四层协同。

## 三、各框架的机制全景

### 3.1 AGENTS.md：正在形成的事实标准

AGENTS.md 已成为多个 agent 框架的通用配置入口：

| 框架 | 读取方式 | 备注 |
|------|---------|------|
| Claude Code | 根目录 AGENTS.md | 与 CLAUDE.md 并行 |
| OpenAI Codex | 根目录 AGENTS.md | VS Code 扩展也读取 |
| Antigravity | 根目录 AGENTS.md | 类似 .cursorrules |
| CodeWhale | 根目录 AGENTS.md | 回退到 CLAUDE.md |
| Swival | 根目录 AGENTS.md | 也支持 ~/.config/swival/AGENTS.md |
| Gemini CLI | contextFileName 指向 | 通过扩展清单配置 |

**优势：** 零配置、跨框架、人类可读。

**典型内容：**
```markdown
# AGENTS.md
## 项目结构
## 构建、测试与开发命令
## 编码风格与命名约定
## 测试约定
## 提交与合并请求约定
## 协作沟通偏好
```

### 3.2 Claude Code：最完整的四层体系

Claude Code 是目前唯一支持完整四层的框架：

```
~/.claude/CLAUDE.md              # 全局规则
<project>/CLAUDE.md              # 项目规则
<project>/backend/CLAUDE.md      # 子目录规则
<project>/AGENTS.md              # 跨平台规则

~/.claude/projects/<project>/memory/
├── MEMORY.md                    # 记忆索引
├── *.md                         # 记忆文件（feedback/project/reference/user）

~/.claude/skills/                # 全局技能
<project>/.claude/skills/        # 项目技能
```

**Memory 机制的独特设计：**
- 按项目隔离（`~/.claude/projects/<encoded-path>/memory/`）
- YAML frontmatter 元数据（name、description、type）
- 支持 `[[wiki-link]]` 交叉引用
- MEMORY.md 作为索引加载到每次会话

### 3.3 Aider：文件即上下文的极简主义

Aider 的设计理念是**极简**——一个 YAML 配置文件 + 一个 conventions 文件，解决所有问题。

**四种等价的配置方式：**
```bash
# 命令行开关
aider --dark-mode

# YAML 配置文件
# .aider.conf.yml
dark-mode: true

# 环境变量
export AIDER_DARK_MODE=true

# .env 文件
AIDER_DARK_MODE=true
```

**Conventions 机制——文件即上下文：**
```bash
# 加载 conventions 文件（标记为只读）
aider --read CONVENTIONS.md

# 或在配置中声明
# .aider.conf.yml
read: [CONVENTIONS.md, coding-standards.md]
```

**核心设计思想：** conventions 不是特殊格式，就是普通文件注入 LLM 上下文。`--read` 标记区分"参考文件"和"编辑目标"——这是对 LLM 工具调用的精确控制。

**配置加载优先级（从低到高）：**
1. `~/.aider.conf.yml`（用户级）
2. 仓库根目录
3. 当前工作目录
4. 命令行参数

**可借鉴之处：**
- 四种等价配置方式，让用户按习惯选择
- `--read` 的只读语义，减少意外修改风险
- conventions 是"以文件为载体的 prompt engineering"

### 3.4 OpenAI Codex：最先进的技能机制

Codex 的 Skills 机制代表了下一代设计方向：

```
~/.codex/
├── config.toml                  # 全局配置
├── rules/default.rules          # 命令级权限
├── skills/                      # 技能目录
│   └── skill-name/
│       ├── SKILL.md             # 必需，YAML frontmatter + 指令
│       ├── scripts/             # 可执行脚本
│       ├── references/          # 按需加载的参考文档
│       └── assets/              # 输出资源
└── memories/                    # 记忆系统
```

**渐进式披露设计（三级加载）：**
1. **元数据**（name + description）— 始终在上下文中（约 100 词）
2. **SKILL.md body** — 触发时加载（< 5k 词）
3. **Bundled resources** — 按需加载（无限制）

**这意味着：** 你可以有 100 个技能，但上下文中只占用 100 词的元数据。当用户说"帮我做 X"，系统匹配 description，只加载那一个 SKILL.md。

### 3.5 GitHub Copilot：最完整的分层体系

Copilot 发展出了一套**多文件类型 + 分层优先级**的自定义体系：

```
.github/
├── copilot-instructions.md          # 始终加载的项目级指令
└── instructions/                    # 按条件触发的文件级指令
    ├── frontend/
    │   └── react.instructions.md
    └── backend/
        └── api-design.instructions.md
```

**`.instructions.md` 的条件触发：**
```yaml
---
name: 'Python Standards'
description: 'Coding conventions for Python files'
applyTo: '**/*.py'
---
# Python coding standards
- Follow PEP 8
- Use type hints for all function signatures
```

**三层优先级（冲突解决）：**
1. **个人指令**（`~/.copilot/instructions/`）— 最高优先级
2. **仓库指令**（`.github/copilot-instructions.md`）— 中等
3. **组织指令**（GitHub 组织设置）— 最低

**跨工具兼容：** Copilot 还支持读取 `AGENTS.md` 和 `CLAUDE.md`，降低用户迁移成本。

**更广泛的自定义生态：**

| 类型 | 用途 |
|------|------|
| Instructions | 编码规范，自动应用 |
| Prompt Files (`.prompt.md`) | 可复用的斜杠命令 |
| Custom Agents (`.agent.md`) | 专用角色（如只读审查员） |
| Agent Skills (`SKILL.md`) | 自包含的工作流包 |
| Hooks | 代理生命周期中的自动化操作 |

**可借鉴之处：**
- `applyTo` glob 让指令按文件类型自动应用，解决 monorepo 痛点
- 个人 > 仓库 > 组织的优先级模型，清晰的冲突解决策略
- 跨工具兼容（读取 AGENTS.md、CLAUDE.md），务实的互操作决策

### 3.6 IDE 的 rules 机制：简单但有效

| 框架 | 配置文件 | 格式 | 特色 |
|------|---------|------|------|
| Cursor | `.cursor/rules/*.mdc` | MD + YAML frontmatter | glob 模式匹配 |
| Cline | `.clinerules/*.md` | 纯 Markdown | 最简单 |
| Windsurf | `.windsurf/rules/*.md` | 纯 Markdown | 与 Cline 类似 |
| Kiro | `.kiro/steering/*.md` | MD + YAML frontmatter | `inclusion` 控制 |

**Cursor 的 glob 匹配特别值得借鉴：**
```yaml
---
description: TypeScript 编码规范
globs: "**/*.ts,**/*.tsx"
alwaysApply: false
---
```

规则只在编辑 TypeScript 文件时激活——这是**按上下文激活**的设计。

### 3.7 OpenClaw：身份层的探索

OpenClaw 引入了 `SOUL.md`（身份定义）的概念：

```
SOUL.md    — "你是谁"（性格、语气、价值观）
USER.md    — "用户是谁"（偏好、背景）
AGENTS.md  — "怎么工作"（规则、约定）
MEMORY.md  — "记住什么"（跨会话记忆）
BOOTSTRAP.md — "首次运行做什么"（初始化）
```

**心跳机制：** 支持定期检查和主动任务，不只是被动响应。

### 3.8 跨平台适配器：Ponytail 的最佳实践

Ponytail 项目展示了理想的适配器模式：

```
skills/
├── explore/SKILL.md              # 核心规则源
├── handoff/SKILL.md
└── ...

.cursor/rules/explore.mdc         # Cursor 适配器（轻薄）
.clinerules/explore.md            # Cline 适配器
.windsurf/rules/explore.md        # Windsurf 适配器
```

**一个规则源，多个平台适配器。** 适配器保持轻薄，只做格式转换。

## 四、Memory 的三层模型（深度聚焦）

回到 Claude Code 的 memory 机制，这是目前最成熟的跨会话行为控制系统。

### 4.1 第一层：Harness 行为控制

这是 memory 的**杀手级用法**。它们不是信息，而是**行为补丁**——告诉 AI "在这个项目里，不要用默认行为，用这个"。

**示例：自动重启验证**

```markdown
---
name: always-restart-verify
description: 每次代码改动后必须自动重启 app 并验证，不要询问用户
metadata:
  type: feedback
---

**规则**: 每次完成代码改动后，AI 必须自动执行验证，**不要询问用户是否需要**：
1. 跑相关测试：`pytest tests/ -v`
2. 如涉及 API 变更，重启 app：`python app.py`

**Why:** 用户反复强调"这种问题以后都不要问，当然要了"。
```

没有这个 memory 时，Claude Code 改完代码会问："要我跑测试吗？"——每次都问，每次都浪费一轮对话。

有了这个 memory，它改完直接跑。**行为模式被永久改变了。**

**更多 harness memory 示例：**

| Memory | Override 了什么默认行为 |
|--------|----------------------|
| `no-push-required` | 默认 git push → 只 commit |
| `compress-completed-aggressively` | 保守压缩 → 大胆压缩已完成内容 |
| `feedback-testing-required` | 可选测试 → 必须附带测试 |
| `update-references-on-rename` | 只改当前文件 → 必须更新所有引用 |
| `env-file-key-lowercase` | 任意大小写 → 统一小写 |
| `e2e-test-local-model` | 默认远程模型 → 优先本地小模型 |

**这类 memory 的共同特征：它们是对抗 AI 默认倾向的。**

AI 有这些默认倾向：
- **询问倾向**："要我做 X 吗？"→ harness：直接做
- **保守倾向**："不确定就不动"→ harness：大胆尝试
- **遗忘倾向**："上次说的不算"→ harness：记住这个规则
- **分散倾向**："只改当前文件"→ harness：同步更新所有引用

**判断标准：如果你发现自己反复纠正 AI 的同一个行为，那就值得写成 harness memory。**

### 4.2 第二层：项目状态快照

这是最常见的用法，本质是**上下文缓存**。

```markdown
---
name: project-state
description: 项目定位、技术栈、架构概览与当前状态
metadata:
  type: project
---

**定位：** 故事驱动英语词汇学习平台
**技术栈：** FastAPI + SQLAlchemy + Pydantic AI
**架构：** DDD 领域驱动，领域之间零依赖
**Agent 清单（7 个）：** ...
**测试：** 430 passed
```

没有这个 memory，新会话需要读 CLAUDE.md、扫目录、分析代码——花 30 秒建立上下文。

有了这个 memory，0 秒恢复。**但它不会改变 AI 的行为方式，只是加速启动。**

### 4.3 第三层：历史事件记录

价值最低，但偶尔有用。

```markdown
---
name: langchain-to-pydantic-ai-migration-complete
metadata:
  type: project
---

LangChain → Pydantic AI 迁移已完成，所有服务已迁移。
```

这类 memory 的问题：**会过时。** 迁移完成了，这个 memory 就变成噪音。应该及时清理或归档。

## 五、Harness Memory 的设计原则

### 原则 1：对抗默认倾向

Harness memory 的本质是**行为 override**。写之前先问自己：

> "AI 的默认行为是什么？我想要的行为是什么？两者有差距吗？"

如果有差距，就需要 harness memory。

### 原则 2：明确 Why 和 How to apply

```markdown
**Why:** 用户反复强调"这种问题以后都不要问"。
**How to apply:** 完成任何代码改动后，直接执行验证步骤，不询问。
```

没有 Why，AI 不知道什么时候该应用。没有 How to apply，AI 不知道具体怎么做。

### 原则 3：feedback 类型优先

Memory 的 `type` 字段决定了优先级：

| Type | 含义 | 优先级 |
|------|------|--------|
| `feedback` | 用户纠正 AI 行为 | 最高 — 永远遵守 |
| `project` | 项目状态信息 | 中等 — 参考用 |
| `user` | 用户画像 | 低 — 个性化 |
| `reference` | 外部资料 | 最低 — 按需查阅 |

**Harness memory 永远是 feedback 类型。**

### 原则 4：单一职责

每个 harness memory 只控制一个行为。不要写"综合规范"，要写"具体规则"。

```
❌ 一个文件包含 10 条规则
✅ 10 个文件，每个文件一条规则
```

这样可以独立更新、独立删除、独立引用。

### 原则 5：跨项目继承

有些 harness 是通用的，有些是项目专属的：

```
# 通用（workspace 级）
~/.claude/projects/<workspace>/memory/
├── no-push-required.md
├── env-file-key-lowercase.md
└── update-references-on-rename.md

# 项目专属
~/.claude/projects/<project>/memory/
├── always-restart-verify.md      # 有 web app 的项目
├── e2e-test-local-model.md       # 有本地模型的项目
└── feedback-testing-required.md
```

## 六、完整 Harness 体系示例

以下是我在一个真实项目中建立的 harness 体系：

```
~/.claude/projects/<project>/memory/
├── MEMORY.md                         # 索引（按三层分组）
│
│  # Harness 行为控制（6 个）
├── always-restart-verify.md          # 改完代码直接验证，别问
├── feedback-testing-required.md      # 新增代码必须有测试
├── compress-completed-aggressively.md # 压缩时大胆删已完成内容
├── no-push-required.md               # 只 commit 不 push
├── update-references-on-rename.md    # 重命名必须同步所有引用
├── env-file-key-lowercase.md         # .env key 小写
│
│  # 项目状态（4 个）
├── project-state.md                  # 架构、Agent 清单、测试状态
├── known-gaps.md                     # 测试盲区、技术债务
├── design-decisions.md               # 关键决策与 trade-off
├── integration-pic2text.md           # 项目间边界
│
│  # 历史事件（2 个）
├── langchain-to-pydantic-ai-migration-complete.md
└── vision-story-content-persistence.md
```

**6 个 harness + 4 个状态 + 2 个历史 = 12 个 memory 文件。**

MEMORY.md 索引按三层分组：

```markdown
# Harness 行为控制
- [Always restart verify](always-restart-verify.md) — 代码改动后自动重启验证
- [Feedback testing required](feedback-testing-required.md) — 新增代码必须附带测试
...

# 项目状态
- [Project state](project-state.md) — 项目定位、技术栈、架构
...

# 历史事件
- [LangChain to Pydantic AI migration complete](...) — 迁移已完成
...
```

## 七、Memory 的生命周期管理

### 创建时机

| 场景 | 创建什么 |
|------|----------|
| 反复纠正同一个行为 | harness memory（feedback） |
| 新会话花很久建立上下文 | 项目状态 memory（project） |
| 完成重大变更 | 历史事件 memory（project） |

### 更新时机

| 场景 | 操作 |
|------|------|
| 项目架构变更 | 更新 `project-state.md` |
| 发现新的技术债务 | 更新 `known-gaps.md` |
| 做了新的架构决策 | 更新 `design-decisions.md` |

### 清理时机

| 场景 | 操作 |
|------|------|
| 历史事件已过时 | 删除或归档 |
| 项目状态已不准确 | 更新或删除 |
| harness 规则不再适用 | 删除 |

## 八、设计趋势：从规则到操作系统

### 趋势 1：AGENTS.md 成为跨平台标准

越来越多的框架选择读取 AGENTS.md。这是自下而上形成的社区标准，优势在于：
- 零配置：放在仓库根目录即可
- 跨框架：多个 agent 可以共享同一份规则
- 人类可读：开发者可以直接阅读和编辑

### 趋势 2：渐进式披露

Codex 的 Skills 机制代表了下一代设计：
- 元数据始终加载（100 词）
- 详细内容按需加载（< 5k 词）
- 参考文档延迟加载（无限制）

**解决了核心矛盾：规则越多越全，但上下文窗口越满。**

### 趋势 3：行为分层控制

从"一个文件管所有"到"四层各司其职"：
- 身份层定义"你是谁"
- 规则层定义"怎么工作"
- 技能层定义"能做什么"
- 记忆层定义"记住什么"

### 趋势 4：从 PR Review 自动提取规则

pydantic_ai 的 `<!-- rule:ID -->` 模式：
- 从 PR 审查中自动提取编码规范
- 每条规则带唯一标识
- 包含规则描述和设计理由
- 可以被工具自动处理和索引

### 趋势 5：跨平台适配器生态

Ponytail 项目展示了理想模式：
- 核心行为定义在 `skills/` 中
- 各平台适配器保持轻薄
- 共享的指令构建器确保一致性
- 支持 15+ 个平台

### 趋势 6：文件即上下文 + 条件激活

Aider 和 Copilot 代表了两种互补的设计思想：

**Aider 的"文件即上下文"：** conventions 不是特殊格式，就是普通文件注入 LLM 上下文。`--read` 标记区分"参考"和"编辑目标"，这是对 LLM 工具调用的精确控制。

**Copilot 的"条件激活"：** `applyTo` glob 让指令按文件类型自动激活。monorepo 中前端和后端可以有完全不同的规则，无需手动切换。

**两者结合的趋势：** 规则不再是"一个文件管所有"，而是"按上下文自动组装"。

## 九、总结：给不同读者的建议

### 如果你是 Claude Code 用户

从 harness memory 开始。找到你反复纠正 AI 的行为，写成 feedback 类型的 memory。

```
判断标准：如果你发现自己反复纠正 AI 的同一个行为，写成 harness memory。
```

### 如果你是框架开发者

参考 Codex 的渐进式披露设计。解决"规则越多上下文越满"的矛盾。

### 如果你是多平台用户

用 AGENTS.md 作为基础，为各平台提供轻薄的适配器。参考 Ponytail 的模式。

### 如果你是团队 Lead

建立团队级的 harness 体系：
- AGENTS.md 放团队编码规范
- Memory 放项目状态和决策记录
- Skills 放可复用的工作流

---

**参考资源：**
- [Claude Code Memory 文档](https://docs.anthropic.com/en/docs/claude-code)
- [OpenAI Codex Skills](https://github.com/openai/codex)
- [Aider Conventions](https://aider.chat/docs/usage/conventions.html)
- [GitHub Copilot Custom Instructions](https://code.visualstudio.com/docs/copilot/copilot-customization)
- [Ponytail 跨平台适配](https://github.com/ponytail/ponytail)
- [AGENTS.md 规范讨论](https://github.com/anthropics/claude-code/discussions)

**本文涉及的框架：** Claude Code、OpenAI Codex、Aider、GitHub Copilot、Cursor、Cline/Roo Code、Windsurf、Kiro、OpenCode、OpenClaw、Pydantic AI
