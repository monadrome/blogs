---
title: "The Zen of Go 深度解读：Dave Cheney 的 Go 工程价值观"
date: 2026-06-27
source: research
---

# The Zen of Go 深度解读：Dave Cheney 的 Go 工程价值观

## 一、背景与起源

"The Zen of Go" 是 Go 语言社区最具影响力的技术散文之一，作者 Dave Cheney 是 Go 社区的资深贡献者和知名技术作家。这篇文章最初源自他在 **GopherCon Israel 2020** 上的同名演讲，后整理为博客文章发表于 [dave.cheney.net](https://dave.cheney.net/2020/02/23/the-zen-of-go)，并最终扩展为一本 Leanpub 电子书。

Cheney 提出了一个根本性问题：**"How do you know when you've written good Go code?"** -- 你如何知道自己写出了好的 Go 代码？他没有给出又一套"最佳实践"清单，而是尝试从更底层回答这个问题：好的代码背后，应该有哪些工程价值观（Engineering Values）来指导决策？

---

## 二、文章结构：先破后立的论述式散文

这篇文章不是格言式罗列，而是一篇 **约 5500 字的长篇论述式散文**，采用经典的"先破后立"结构：

### 第一层：破 -- 解构现有框架

**1. 批判"Idiomatic Go"（惯用 Go）**

Cheney 首先对"你的代码不够 idiomatic"这一社区常见批评发起了挑战。他认为这个概念本质上是排外的：

> "My concern with the mantra of idiomatic Go is, in many ways, it can be exclusionary. It's saying 'you can't sit with us.'"

他引用词典定义来论证：idiom（惯用语）是"只有母语使用者才能自然理解的表达"，因此"idiomatic Go"本质上是一个需要通过社区浸润才能习得的东西，不适合作为教学工具。

**2. 批判"Go Proverbs"（Go 格言）**

他接着对 Rob Pike 的 Go Proverbs 提出了温和的质疑：这些格言是"observations, not statements of value"（观察结论，而非价值判断）。比如"空接口什么都没说"这句话，对一个来自没有结构类型系统的语言的新手来说，毫无指导意义。

### 第二层：立 -- 建立工程价值观框架

Cheney 引入了 Mark Lucovsky 在 Windows NT 团队提出的概念：**"Values guide decisions in an unknown design space"**（价值观在未知的设计空间中指导决策）。NT 团队的价值观是可移植性、可靠性、安全性和可扩展性。

以此为理论基础，他提出了用 **Engineering Values**（工程价值观）取代 Idioms 和 Proverbs 来指导 Go 编程，并以 Python 之禅（PEP-20）为参照系，逐一推导出 Go 的工程价值观。

### 第三层：用 -- 逐条展开论证

每一条价值观都遵循统一的论证模板：
1. 引用 Zen of Python 的相关条目作为起点
2. 指出 Python 的理想与现实之间的差距
3. 提出 Go 的工程价值观
4. 用代码示例和权威引用来支撑论证

---

## 三、十大工程价值观详解

### 1. 每个包都应该有单一职责（Each package fulfils a single purpose）

**Zen of Python 对照：** "Namespaces are one honking great idea -- let's do more of those!"（第 19 条）

**核心论点：** 在 Go 中，namespace 就是 package。一个好的包名应该像电梯演讲一样，用一个词描述它提供什么。包名是名词，不是动词。

**关键引用：**
- Sandi Metz: "Design is the art of arranging code to work today, and be changeable forever."
- Cheney 自己的观点：设计是为了替换，而不是为了增强。"Rather than enhancing components, we replace them."

**实操建议：** 当包名不再匹配需求时，找一个替代品，而不是往里塞更多功能。

### 2. 简单很重要（Simplicity matters）

**Zen of Python 对照：** "Simple is better than complex."（第 3 条）

**核心论点：** 每个新语言都声称自己很简单，但真正把简单作为核心价值的寥寥无几。

**三重权威引用加固：**
- **C.A.R. Hoare**（1980 年图灵奖得主）: "There are two ways of constructing a software design: One way is to make it so simple that there are obviously no deficiencies, and the other way is to make it so complicated that there are no obvious deficiencies. The first method is far more difficult."
- **Dijkstra** (EWD498, 1975): "Simplicity is prerequisite for reliability."
- **Kernighan** (Software Tools, 1976): "Controlling complexity is the essence of computer programming."

**关键定义：** "Simple doesn't mean crude, it means readable and maintainable. Simple doesn't mean unsophisticated, it means reliable, relatable, and understandable."（简单不意味着粗糙，它意味着可读和可维护。简单不意味着不精密，它意味着可靠、可关联和可理解。）

### 3. 避免包级状态（Avoid package level state）

**Zen of Python 对照：** "Explicit is better than implicit."（第 2 条）

**核心论点：** Cheney 认为这是 Python 的 PEP-20 "more aspirational than factual"（更像理想而非事实）的地方 -- Python 有装饰器、dunder 方法等大量隐式机制。而 Go 通过工程价值观来真正践行"显式优于隐式"。

**核心判断：** "Management of state is THE problem in computer science."（状态管理是计算机科学的根本问题。）

**代码示例：** 一个 `counter` 包，使用包级变量 `var count int` -- 无法独立测试、无法并行测试、无法支持多实例。解决方案：封装到结构体中。

**实操建议：** 将依赖作为结构体的字段注入，而不是使用包级变量，从而减少耦合和"幽灵般的远距离作用"（spooky action at a distance）。

### 4. 为失败做计划，而不是为成功（Plan for failure, not success）

**Zen of Python 对照：** "Errors should never pass silently."（第 10 条）

**核心论点：** Cheney 对比了基于异常的语言（他称之为"武士道原则：不成功便成仁"）和 Go 的显式错误处理。

**关键引用：** Peter Bourgon (GoTime #91): "I think that error handling should be explicit, this should be a core value of the language."

**核心立场：** "Go programmers think about the failure case first. We solve the 'what if...' case first. This leads to programs where failures are handled at the point of writing, rather than the point they occur in production."

**对 `if err != nil` 的辩护：** "The verbosity is outweighed by the value of deliberately handling each failure condition at the point at which they occur."（冗长的代价远低于在编写时就刻意处理每个失败条件的价值。）

### 5. 提前返回，避免深层嵌套（Return early rather than nesting deeply）

**Zen of Python 对照：** "Flat is better than nested."（第 5 条）

**核心论点：** 引用 Mat Ryer 的"视线编码"（line of sight coding）概念 -- 将快乐路径对齐到左边缘。

**三个具体技术：**
1. 使用守卫子句（guard clauses）在前提条件不满足时提前返回
2. 将成功返回语句放在函数末尾，而不是嵌套在条件块中
3. 通过提取函数和方法来减少整体缩进

**认知科学引用：** "Every time you indent you add another precondition to the programmer's stack, consuming one of their 7 +/- 2 short term memory slots."（每次缩进都往程序员的认知栈上加一个前提条件，消耗他们 7±2 个短期记忆槽位中的一个。）

### 6. 如果你觉得它慢，先用基准测试证明（If you think it's slow, prove it with a benchmark）

**Zen of Python 对照：** "In the face of ambiguity, refuse the temptation to guess."（第 12 条）

**核心论点：** 很多性能"优化"基于过时的经验教条，而非实际测量。

**他点名的常见教条：** "defer is slow, CGO is expensive, always use atomics not mutexes" -- 这些都应该被验证，而不是被假设。

**关键引用：** Josh Bloch: "APIs should be easy to use and hard to misuse."

**实操建议：** "Don't complicate your code because of outdated dogma, and, if you think something is slow, first prove it with a benchmark."

### 7. 在启动 goroutine 之前，知道它何时会停止（Before you launch a goroutine, know when it will stop）

**核心论点：** 这是 Go 独有的价值观，没有直接的 Python 对应。Cheney 引用 Rob Pike (dotGo 2015) 的话："You type g o, a space, and then a function call. Three keystrokes, you've just started a sub process."（你输入 g o，空格，然后一个函数调用。三次按键，你就启动了一个子进程。）

**三个必须回答的问题：**
1. 在什么条件下 goroutine 会停止？（几乎总是 channel 操作 -- range 循环在 channel 关闭时退出）
2. 需要什么条件才能使这种情况发生？（谁来关闭 channel，什么时候关闭？）
3. 你用什么信号来知道 goroutine 已经停止？（通常是一个用于回传信号的 channel 或用于 fan-in 的 WaitGroup）

**核心洞察：** "Goroutines are the key to resource ownership in Go. To be useful a goroutine has to do something, and that means it almost always holds reference to, or ownership of, a resource."

### 8. 把并发留给调用者（Leave concurrency to the caller）

**核心论点：** Cheney 用 `net/http` 作为反面案例 -- 因为每个连接都是在 `net/http.Server` 内部启动的 goroutine，外部程序无法控制这些 goroutine 的生命周期。

**实操建议：** "Leave the responsibility of starting the goroutine to your caller. Let the caller choose how they want to start, track, and wait on your functions execution."

**参考实现：** go-kit 的 `run.Group` 和 Go 团队的 `ErrGroup`。

### 9. 用测试锁定 API 行为（Write tests to lock in the behaviour of your package's API）

**核心论点：** 测试不是可选的文档，而是 API 的契约。

**关键表述：**
- "Your tests are the contract about what your software does and does not do."
- "Tests lock in api behaviour. Any change that adds, modifies or removes a public api must include changes to its tests."

### 10. 节制是一种美德（Moderation is a virtue）

**核心论点：** Cheney 分享了自己过度使用 channel、goroutine 和 embedding 的亲身经历。

**实操建议：** "If you can, don't reach for a goroutine, or a channel, or embed a struct, anonymous functions, going overboard with packages, interfaces for everything, instead prefer simpler approach rather than the clever approach."

### 收束：可维护性至上（Maintainability counts）

**Zen of Python 对照：** "Readability Counts."（第 7 条）

**Cheney 的升级：** "Simplicity, readability, clarity, productivity -- they are all synonyms for one word: maintainability."（简单、可读、清晰、生产力 -- 它们都是同一个词的同义词：可维护性。）

**终极问题：** "Can the thing you worked hard to build be maintained after you're gone? What can you do today to make it easier for someone to maintain your code tomorrow?"（你辛苦构建的东西能在你离开后继续维护吗？你今天能做什么来让明天接手的人更容易维护你的代码？）

---

## 四、修辞手法与论证技巧分析

Cheney 的写作有一套非常成熟的修辞策略，值得技术写作者学习：

### 4.1 权威引用的三层叠加

Cheney 不是简单地抛出观点，而是用权威引用来构建论证的可信度。他的引用策略分三个层次：

| 层次 | 来源 | 效果 |
|------|------|------|
| 计算机科学先驱 | Hoare、Dijkstra、Kernighan | 为抽象原则提供学术背书 |
| Go 语言创造者 | Rob Pike、Ken Thompson | 为语言设计决策提供第一手权威 |
| 社区实践者 | Peter Bourgon、Josh Bloch、Mat Ryer、Sandi Metz | 为工程实践提供社区共识 |

### 4.2 词典定义作为论证锚点

Cheney 多次使用词典定义来框定讨论范围。他先定义"idiom"是什么，再讨论"idiomatic Go"是否成立；先定义"proverb"是什么，再评估 Go Proverbs 的局限性。这种手法让他的论证有了不可动摇的基础。

### 4.3 先破后立的辩证结构

他不是直接说"这是好的 Go 代码的标准"，而是先解构两个已有的框架（Idiomatic Go 和 Go Proverbs），指出它们的不足，再提出自己的替代方案。这让读者在心理上更容易接受新框架。

### 4.4 代码示例的反面教学

在"避免包级状态"一节中，他先展示了一个有问题的 `counter` 包，让读者自己发现它的问题（无法测试、无法并行、无法多实例），再给出解决方案。这种反面教学比直接展示正确做法更有效。

### 4.5 跨语言参照系

以 Zen of Python 为参照系是一个精妙的修辞选择。它：
- 让 Python 开发者也能产生共鸣
- 借用了 Zen of Python 的知名度和文化影响力
- 通过对比凸显 Go 设计哲学的独特性
- 为每条原则提供了现成的简洁表述

### 4.6 个人经验的脆弱性表达

在"节制是一种美德"一节中，Cheney 承认自己也曾过度使用 channel 和 goroutine。这种自我暴露建立了与读者的信任，让他的建议显得更像是"过来人的忠告"而非"自上而下的教条"。

---

## 五、与 The Zen of Python 的异同

### 5.1 结构对比

| 维度 | Zen of Python (PEP-20) | Zen of Go |
|------|----------------------|-----------|
| 形式 | 19 条格言，诗意、抽象、哲学化 | 10 条工程价值观，具体、可操作、可执行 |
| 作者 | Tim Peters（社区共识） | Dave Cheney（个人提炼） |
| 载体 | PEP-20，Python 官方文档的一部分 | 博客文章 + 演讲 + Leanpub 电子书 |
| 获取方式 | `import this` | 阅读博客/观看演讲/购买电子书 |
| 字数 | 约 300 字 | 约 5500 字（博客）/ 10 章（书） |
| 论证 | 无（格言自证） | 详细论证 + 代码示例 + 权威引用 |

### 5.2 价值观映射

Cheney 在文章中直接建立了 7 条 Python 到 Go 的映射关系：

| Zen of Python | Zen of Go |
|---------------|-----------|
| "Namespaces are one honking great idea" (19) | 每个包有单一职责 |
| "Simple is better than complex" (3) | 简单很重要 |
| "Explicit is better than implicit" (2) | 避免包级状态 |
| "Errors should never pass silently" (10) | 为失败做计划 |
| "Flat is better than nested" (5) | 提前返回，避免深层嵌套 |
| "In the face of ambiguity, refuse the temptation to guess" (12) | 先用基准测试证明 |
| "Readability counts" (7) | 可维护性至上 |

### 5.3 Go 独有的价值观

以下三条是 Python 之禅中没有对应物的，属于 Go 语言并发模型带来的独特工程挑战：

1. **启动 goroutine 前知道它何时停止** -- Python 没有等价的轻量级并发原语
2. **把并发留给调用者** -- Python 的 GIL 使得这个讨论不太一样
3. **节制是一种美德** -- Python 鼓励灵活性（"There should be one-- and preferably only one --obvious way to do it"），而 Go 通过限制特性数量来实现类似效果

### 5.4 哲学层面的根本差异

**Python 的哲学是"信任开发者"：** 给予灵活性、表达力、元编程能力，相信开发者会做出好的选择。Python 的 `this` 模块（`import this` 输出 Zen of Python）本身就充满了 Python 式的隐式魔法。

**Go 的哲学是"约束开发者，信任工具链"：** `gofmt` 不是建议而是强制执行；没有泛型（直到 1.18）不是疏忽而是有意为之；没有异常机制不是缺陷而是设计选择。Cheney 在文章中批评 Python 的"显式优于隐式"原则在 Python 自身并未被很好遵守（装饰器、dunder 方法等），而 Go 通过更少的特性来真正实现这一原则。

---

## 六、对技术文章写作的启示

### 6.1 长文的结构设计

Cheney 的文章证明，5000+ 字的技术长文完全可以保持读者注意力，关键是结构设计：

- **以问题开头，不以答案开头。** "How do you know when you've written good Go code?" 比 "Here are 10 principles for good Go code" 更有吸引力。
- **先建立共同的"痛点"。** 他在提出自己的框架之前，先让读者认同"idiomatic Go"和"Go Proverbs"的局限性。
- **使用参照系降低认知负担。** 以 Zen of Python 为锚点，读者不需要从零理解每条原则。

### 6.2 权威引用的策略

不要只引用一个人。Cheney 的引用横跨 50 年的计算机科学史（1975 Dijkstra -> 1976 Kernighan -> 1980 Hoare -> 2015 Pike -> 2019 Bourgon），这让他的论证既有历史纵深感，又有当代实践支撑。

### 6.3 从抽象到具体的论证路径

每条原则都遵循：抽象概念 -> 权威引用 -> 代码示例 -> 实操建议。这种路径满足了不同层次读者的需求：架构师看概念，开发者看代码，团队负责人看建议。

### 6.4 勇于挑战共识

Cheney 最大胆的修辞选择是挑战"idiomatic Go"这个社区共识。他不是全盘否定，而是指出其局限性并提出替代方案。这种"批判性继承"的姿态比简单的"我的方法更好"更有说服力。

### 6.5 个人经验的价值

技术文章不应该是冰冷的规范文档。Cheney 在"节制是一种美德"中分享自己过度使用 channel 的经历，这种自我反思让文章有了温度，也让读者更愿意接受建议。

---

## 七、核心金句摘录

**关于代码质量：**
- "Simplicity, readability, clarity, productivity -- they are all synonyms for one word: maintainability."
- "If software cannot be maintained, then it will be rewritten; and that could be the last time your company will invest in Go."

**关于状态管理：**
- "Management of state is THE problem in computer science."
- "Reduce coupling and spooky action at a distance."

**关于错误处理：**
- "Go programmers think about the failure case first. We solve the 'what if...' case first."
- "The verbosity is outweighed by the value of deliberately handling each failure condition."

**关于性能优化：**
- "So many crimes against maintainability are committed in the name of performance."
- "Optimisation tears down abstractions, exposes internals, and couples tightly."

**关于社区文化：**
- "Idiomatic Go is not something you learn from a book, it's something that you acquire by being part of a community."
- "My concern with the mantra of idiomatic Go is, in many ways, it can be exclusionary. It's saying 'you can't sit with us.'"

---

## 八、参考资源

| 资源 | 链接 |
|------|------|
| 博客原文 | https://dave.cheney.net/2020/02/23/the-zen-of-go |
| GopherCon Israel 2020 演讲 | https://www.youtube.com/watch?v=yd_rtwYaXps |
| 精简版网站 | https://the-zen-of-go.netlify.app/ |
| Leanpub 电子书 | https://leanpub.com/thezenofgo |
| Zen of Python (PEP-20) | https://www.python.org/dev/peps/pep-0020/ |
