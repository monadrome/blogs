# The Zen of Erlang 深度调研

> **原文:** [The Zen of Erlang](https://ferd.ca/the-zen-of-erlang.html)
> **作者:** Fred Hebert (ferd)
> **发布日期:** 2016/02/08
> **场合:** ConnectDev'16 (Genetec 组织的技术大会)
> **形式:** 演讲的自由文字转录版 (loose transcript)

---

## 一、作者背景

Fred Hebert 是一位自学成才的 Erlang/OTP 专家，目前担任 Honeycomb.io 的 Staff SRE。他的职业轨迹涵盖了从 PHP 网站开发到 Erlang 基础设施、再到 SRE 和韧性工程 (Resilience Engineering) 的完整路径。

**关键成就：**
- 著有免费在线教程 [Learn You Some Erlang for Great Good!](https://learnyousomeerlang.com)
- 著有运维手册 [Erlang in Anger](https://erlang-in-anger.com/)
- 著有 [Property-Based Testing with PropEr, Erlang, and Elixir](https://propertesting.com)
- Erlang 构建工具 rebar3 的联合维护者
- [Erlang Ecosystem Foundation](https://erlef.org/) 联合创始人及四年董事会成员
- 2025 年起担任 [Resilience in Software Foundation](https://resilienceinsoftware.org/) 董事会成员

他的博客副标题是 "My bad opinions"，风格自嘲而深刻。

---

## 二、文章结构分析

文章采用 **递进式论证结构**，从基础构件到组合模式，再到运维现实，层层递进：

### 第一部分：破题——重新理解 "Let It Crash"（幻灯片 001-004）

| 章节 | 核心论点 |
|------|----------|
| 开场 | 明确假设听众未使用过 Erlang，承诺只讲高层概念 |
| Let It Crash | 承认这个口号初看令人困惑——容错语言怎么能让东西崩溃？ |
| 火箭类比 | "Let it crash" 之于 Erlang，就像 "Blow it up" 之于火箭科学——关键在于**控制** |
| 以火攻火 | 用魁北克蓝莓田的 controlled burn 类比：受控的破坏可以防止更大的失控 |

**修辞手法：** 连续使用三个出人意料的类比（火箭爆炸、森林火灾），制造认知张力，然后通过"重新定义"消解矛盾。

### 第二部分：基础构件——五种"食材"（幻灯片 005-010）

文章用"烹饪食谱"的隐喻，将 Erlang 的容错能力分解为五种核心构件：

#### 1. 进程隔离（Processes / 蜜蜂类比）
- **完全隔离**：没有进程能访问另一个进程的内存
- **极轻量**：可以有成千上万个进程
- **设计原则**：使用你需要的那么多进程，而不是你能承受的那么多
- **类比**：如果面向对象语言只能同时运行 32 个对象，你会觉得荒谬

#### 2. 消息传递（Message Passing / 信使类比）
- **异步**：发消息后回去做自己的事，不会站在门廊等回信
- **复制**：数据在传递时被拷贝，发送方死亡不会影响接收方的数据
- **邮箱模型**：每个进程一个邮箱，所有人可以写，只有主人能读
- **历史类比**：从骑马信使、拿破仑旗语、电报到现代通信

#### 3. 链接与监控（Links & Monitors / 登山者类比）
- **Monitors（监控）**：单向观察，被监控进程死亡时收到消息，对方不知道你在观察
- **Links（链接）**：双向命运绑定，一方死亡发送退出信号杀死另一方
- **trap_exit**：特殊进程可以将退出信号转化为消息，实现"不随同伴一起死"
- **登山者类比**：如果只有 link，登山者一滑全队就死；trap_exit 让某些进程成为"不会被同伴拖下水"的角色

#### 4. 抢占式调度（Preemptive Scheduling / 阿波罗 11 类比）
- **阿波罗 11 登月**：导航计算机因雷达硬件 bug 占用过多 CPU 周期，但优先级调度保住了宇航员的命
- **抢占式 > 协作式**：开发者不必精确计算每个组件的 CPU 使用量
- **附加价值**：自动负载均衡、奖惩机制、自适应系统

#### 5. 网络感知（Network Aware / 双座战斗机类比）
- **F-82 Twin Mustang**：双座设计让飞行员可以轮换休息
- **Erlang 原生分布式**：大多数语言忽略分布式，Erlang 将其作为一等公民
- **多语言节点**：其他语言可以伪装成 Erlang 节点构建多语言系统

### 第三部分：组合模式——监督树（幻灯片 011-020）

从构件到架构的飞跃：

#### 监督树的核心思想
- **树形层次结构**：关键组件靠近根部，易碎组件在叶子
- **自然类比**：树叶可以秋天全部掉落，树依然活着

#### 三种重启策略
| 策略 | 适用场景 | 行为 |
|------|----------|------|
| one_for_one | 子进程相互独立 | 只重启死亡的那个 |
| one_for_all | 子进程相互依赖 | 全部杀死，全部重启 |
| rest_for_one | 按启动顺序有依赖 | 杀死死亡进程及其后续启动的进程 |

#### Bohrbug vs Heisenbug（Jim Gray 1985 年术语）

这是文章最精彩的论证之一：

| 类型 | 特征 | 开发阶段发现难度 | 生产环境频率 |
|------|------|------------------|--------------|
| Bohrbug（波尔虫） | 稳定、可观测、可重复 | 核心功能：容易发现 | 核心功能：几乎不会到生产 |
| Heisenbug（测不准虫） | 不稳定、条件依赖、观察行为可能隐藏它 | 几乎不可能发现 | **占生产 bug 的 131/132** |

**关键数据**：Jim Gray 报告在 132 个客户现场 bug 中，只有 1 个是 Bohrbug。在每秒 10 万请求的系统中，十亿分之一概率的 bug 每 3 小时就会出现一次。

**结论**：重启对 Heisenbug 极其有效——因为回滚到已知稳定状态后再次尝试，几乎不可能命中同样的异常上下文。

#### 选举系统示例

文章用一个选举计票系统的完整监督树示例，展示了如何：
- 将 OCR（可能用 C 写的危险代码）放在叶子节点，高容错
- 将计数进程放在中间，中等容错
- 将存储层放在靠近根部，低容错
- 信息从叶子"成熟"后流向核心

**核心洞察**：错误处理被烘焙进了系统结构中，代码中不再需要大量防御性编程。

#### OTP 应用（Applications）

监督子树可以被封装为独立的 OTP Application，实现：
- 可复用性（OTP Application = Erlang 的"库"）
- 依赖声明
- 独立配置、重启、开发

系统获得的属性清单：
1. 什么对系统生存是关键的
2. 什么被允许失败，以及多大频率内可以接受
3. 软件应按什么保证和顺序启动
4. 软件如何失败——定义了部分失败的合法状态
5. 软件如何升级（支持热升级）
6. 组件之间的依赖关系

### 第四部分：现实检验（幻灯片 021-024）

文章在这里转向诚实的自我审视：

#### Heroku 的真实案例
- 生产环境每天产生 50 万到 120 万异常
- 用户完全无感知
- 1/17000 到 1/7000 的异常率，在高流量下几乎必然发生
- 修复后仍有每天几万个已知但无影响的异常，两年后也没修

#### 飞机类比的反转
- 第一个航班：液压系统故障，两个备用系统接管，安全降落——优秀的工程
- 第二个航班（United 734）：暴雪中冲出跑道——再好的工程也不能每次都救你

#### Richard Cook 的影响
- 引用韧性工程学者 Richard Cook 的观点
- 运维永远是系统成功的关键因素
- 操作员逐渐习惯违规操作，将系统推向危险边缘
- "扩大一个好团队永远比扩大一个程序更难"

### 第五部分：总结（幻灯片 025-027）

**Erlang 的终极 Zen：**

> 先构建交互，确保最坏的情况仍然可以接受。然后你的系统中就不会有让你紧张的故障（当故障发生时，你可以在运行时检查一切！）。你可以坐下来放松。

---

## 三、设计哲学原则提炼

从文章中可以提炼出以下核心设计哲学原则：

### 原则 1：拥抱失败，而非预防失败
> "If we can embrace failures, crashes and exceptions and do so in a very well-controlled manner, they stop being this scary event to be avoided and instead become a powerful building block."

**含义**：不要试图编写完美的代码来避免所有错误，而是设计一个能够在错误发生时优雅处理的系统结构。

### 原则 2：隔离是容错的基础
> "No process can go and reach into another one's memory, or impact the work it's doing by corrupting the data it operates on."

**含义**：组件之间的完全隔离（内存、状态、故障域）是构建可靠系统的前提。

### 原则 3：按需而非按能力使用资源
> "Use as many processes as you need, rather than as many as you can."

**含义**：细粒度的隔离带来更精确的故障控制。

### 原则 4：异步通信 + 数据复制 = 通信容错
> "If the other party doesn't respond, you're not stuck doing nothing but waiting on your porch until you die."

**含义**：通信模式本身必须是容错的。

### 原则 5：将依赖关系编码进结构
> "Whenever my independent building blocks start having dependencies among themselves, I can start codifying that into my program."

**含义**：隐式依赖是危险的，应该用显式结构（links, monitors）来表达。

### 原则 6：关键组件靠近根部，易碎组件在叶子
> "The leaves are mobile, there's a lot of them, they can all fall down in autumn, the tree stays alive."

**含义**：层次结构本身就是错误处理策略。

### 原则 7：对 Heisenbug 而言，重启胜过防御
> "Rolling back to a known stable state and trying again is unlikely to hit the weird context that causes them."

**含义**：大多数生产 bug 是瞬态的，重启是最经济的修复手段。

### 原则 8：让代码只描述"正常应该做什么"
> "It no longer contains these tons of if/else or switches or try/catch expressions. Instead, it contains legible code explaining what the code should do when everything goes right."

**含义**：错误处理从代码逻辑中剥离，由系统结构承担。

### 原则 9：先定义最坏情况，确保最坏情况可接受
> "Building interactions first, making sure the worst that can happen is still okay."

**含义**：设计从失败模式开始，而非从功能开始。

### 原则 10：运维不可替代
> "Proper system architecture and development practices can still not replace, or can be broken by inadequate operations."

**含义**：再好的架构也无法弥补糟糕的运维。

---

## 四、修辞手法与论证技巧分析

### 1. 类比密集且出人意料

文章使用了大量"反直觉类比"来制造认知张力：

| 类比 | 表面含义 | 深层含义 |
|------|----------|----------|
| 火箭爆炸 | 危险、失败 | 受控的能量释放 = 推进力 |
| 森林火灾 | 灾难 | 受控燃烧 = 预防更大的灾难 |
| 蜜蜂 | 混乱 | 高度组织化的群体智慧 |
| 登山者 | 团结 | 依赖 = 共同命运 |
| 阿波罗 11 | 古老 | 1969 年就有优先级调度，2016 年很多语言还没有 |
| 飞机 | 可靠 | 即使可靠也需要应急措施 |

**效果**：每次类比都在"这和编程有什么关系？"的疑问中展开，制造悬念，然后在解释中给出恍然大悟的满足感。

### 2. 学术引用增强权威性

- **Jim Gray (1985)**：Bohrbug/Heisenbug 术语的发明者，引用其统计数据（131/132）
- **Richard Cook**：韧性工程学者，引用其关于运维风险的观点
- **Apollo 11**：NASA 的工程实践作为历史先例

### 3. 个人经历增强可信度

- **Heroku 生产案例**：每天 120 万异常的真实数据
- **飞行经历**：两个航班的对比——一个工程救了命，一个工程没救成
- **魁北克蓝莓田**：来自家乡的亲身见闻

### 4. 递进式论证结构

```
基础构件 → 组合模式 → 现实检验 → 乐观结论
（理论）    （架构）    （诚实）    （信心）
```

先建立信心（"这些构件很强大"），再展示架构（"可以这样组合"），然后主动泼冷水（"但运维仍然关键"），最后回到乐观（"但整体仍然值得"）。这种"建立-打破-重建"的结构比单纯吹嘘更有说服力。

### 5. 假设性让步

> "This is not a language you'd use for life-critical systems"

主动承认 Erlang 的局限性，增强了其他论点的可信度。

### 6. 从论坛提问引入反面观点

> "If my configuration file is corrupted, restarting won't fix anything!"

先引用真实的反对意见，再系统性地回应（Bohrbug vs Heisenbug 论证），比自说自话更有说服力。

### 7. 数字锚定

- 131/132 bug 是 Heisenbug
- 十亿分之一概率的 bug 在 10 万 QPS 下每 3 小时出现
- 每天 50 万到 120 万异常
- 1969 年的阿波罗计算机已有优先级调度

具体数字比模糊描述更有冲击力。

---

## 五、与其他 "The Zen of" 文章的异同

### 与 Python "Zen of Python" (PEP 20) 的对比

| 维度 | Zen of Python | Zen of Erlang |
|------|---------------|---------------|
| **作者** | Tim Peters | Fred Hebert |
| **形式** | 19 条格言，每条一句话 | 一篇完整的叙事文章 |
| **长度** | ~700 字符 | ~15,000 字 |
| **风格** | 格言式、禅宗式简洁 | 叙事式、类比密集 |
| **受众** | Python 开发者 | 所有程序员（包括不使用 Erlang 的） |
| **内容** | 编程美学和风格指南 | 系统架构和容错设计哲学 |
| **可执行性** | 抽象原则，需要解读 | 具体的架构模式和工程实践 |
| **语气** | 诗意、幽默、自指 | 严肃、务实、略带自嘲 |
| **文化影响** | `import this` 成为 Python 文化符号 | Erlang 社区经典，但跨语言影响力有限 |

### 核心差异

**Zen of Python** 关注的是 **代码美学**：
> "Beautiful is better than ugly."
> "Readability counts."
> "There should be one-- and preferably only one --obvious way to do it."

**Zen of Erlang** 关注的是 **系统韧性**：
> "先构建交互，确保最坏的情况仍然可以接受。"
> "拥抱失败，将其转化为工具。"

一个说的是"代码怎么写才好看"，另一个说的是"系统怎么设计才不会死"。

### 共同点

1. **命名策略**：都借用 "Zen" 一词暗示超越技术细节的哲学智慧
2. **反直觉**：Python 的 "Errors should never pass silently" vs Erlang 的 "Let it crash"
3. **简洁性追求**：Python 用格言追求代码简洁，Erlang 用结构追求错误处理简洁
4. **社区认同**：都成为各自社区的身份标识

### 与其他 "Zen of" 的模式

技术社区有大量 "Zen of X" 文章，它们通常具有以下模式：
- 借用禅宗的"直觉领悟"而非"逻辑推导"
- 挑战常规思维
- 提供一种"重新看世界"的视角
- 在简洁的形式中蕴含深层智慧

Fred Hebert 的独特之处在于：他没有选择格言式简洁，而是用大量类比和案例来"论证"而非"宣告"。这使得文章更像一篇**技术散文**而非**禅宗公案**。

---

## 六、对技术文章写作的启示

### 1. 从反直觉的主张开始

文章以 "Let it crash" 这个令人困惑的口号开头，立即抓住注意力。好的技术文章应该有一个"等等，这不对吧？"的时刻。

**启示**：找到你主题中最反直觉的点，用它作为钩子。

### 2. 用类比构建桥梁，但类比必须出人意料

火箭、蓝莓田、登山者、阿波罗 11、战斗机——每个类比都来自完全不同的领域。平庸的技术文章用平庸的类比（"就像你家的水管..."），优秀的文章用令人惊讶的类比。

**启示**：类比的价值在于"认知距离"——距离越远，连接时的惊喜越大。

### 3. 先建立构件，再展示组合

文章先逐一介绍五种基础构件（进程、消息、链接、调度、分布式），再展示它们如何组合成监督树。这符合人类学习的自然路径。

**启示**：复杂系统应该被分解为可独立理解的构件。

### 4. 主动承认局限性

> "This is not a language you'd use for life-critical systems."
> "再好的工程也不能每次都救你。"

主动泼冷水比一味吹嘘更有说服力。

**启示**：诚实是最好的修辞策略。

### 5. 用真实数据代替模糊描述

"131/132 bug 是 Heisenbug" 比 "大多数 bug 是瞬态的" 有力得多。

**启示**：能找到数据就不要用形容词。

### 6. 用个人经历建立信任

Heroku 的案例、飞行经历、魁北克的蓝莓田——这些不是"据说"，而是"我亲身经历"。

**启示**：第一人称叙事比第三人称报告更有感染力。

### 7. 结尾回到开头

文章以 "Let it crash" 开始，以 "Let it crash" 结束，但经过全文的论证，读者对这句话的理解已经完全不同。这种"回归"结构创造了完整的叙事闭环。

**启示**：好的结尾不是总结，而是让开头的命题获得新的含义。

### 8. 设定合适的抽象层级

文章明确声明"假设听众从未使用过 Erlang"，只讲高层概念。这使得文章对非 Erlang 开发者也有价值。

**启示**：你的文章能教会不使用该技术的人什么？

### 9. 递进式论证而非平行罗列

文章的结构是：

```
困惑 → 构件 → 组合 → 现实 → 洞察
```

每一步都依赖前一步，读者在每一步都有新的收获。

**启示**：好的文章是一段旅程，不是一张清单。

### 10. 让结构本身成为论点

Erlang 的监督树本身就是"错误处理应该被烘焙进系统结构"这个论点的活证据。文章的论证方式本身就是对文章论点的示范。

**启示**：最好的技术文章让形式与内容一致。

---

## 七、核心引用

> "If we can embrace failures, crashes and exceptions and do so in a very well-controlled manner, they stop being this scary event to be avoided and instead become a powerful building block to assemble large reliable systems."

> "Use as many processes as you need, rather than as many as you can."

> "It is better to crash early and suddenly than to slowly corrupt data on a long-term basis."

> "What's more valuable is forcing every developer to think in such terms from early on."

> "Building interactions first, making sure the worst that can happen is still okay. Then there will be few faults or failures in your system to make you nervous."

---

## 八、参考资料

- 原文: https://ferd.ca/the-zen-of-erlang.html
- 作者简介: https://ferd.ca/about.html
- Learn You Some Erlang: https://learnyousomeerlang.com
- Erlang in Anger: https://erlang-in-anger.com/
- PEP 20 (Zen of Python): https://peps.python.org/pep-0020/
- Jim Gray (1985), "Why Do Computers Stop and What Can Be Done About It?"
- Richard Cook, "How Complex Systems Fail" (演讲系列可在 YouTube 找到)
