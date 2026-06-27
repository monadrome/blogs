# Rust 设计哲学文章调研

> 注意：以下内容基于 AI 训练知识，未能实时验证所有 URL，请以实际网站为准。

---

## 1. "The Zen of Rust"（社区格言集）

**存在形式：** 没有一篇由 Rust 核心人物撰写的单一权威文章。存在的是社区策展的格言集合，受 Python PEP 20 启发。各种版本在 GitHub 仓库（如 `rust-zen` crate、社区 gist）和博客文章中流传。

**结构：** 格言式——简短、精炼的声明，类似 PEP 20。通常 10-20 条。

**常见核心格言：**
- "If it compiles, it works."（能编译就能跑）
- "Fearless concurrency."（无畏并发）
- "Make illegal states unrepresentable."（让非法状态不可表示）
- "Explicit is better than implicit."（显式优于隐式）
- "Prefer composition over inheritance."（组合优于继承）
- "Zero-cost abstractions."（零成本抽象）
- "Fail fast, fail loud."（快速失败，大声失败）

**代码示例：** 无——纯声明式语句

**篇幅：** 极短（通常不超过 1000 字）

---

## 2. "Fearless Concurrency with Rust" — Aaron Turon (2015)

**URL：** `https://blog.rust-lang.org/2015/02/13/Fearless-Concurrency.html`

**发表时间：** Rust 1.0 beta 发布前后，发表在官方 Rust Blog

**结构：** 长篇论述文（非格言式）。围绕问题→解决方案的叙事弧展开。

**核心设计原则：**
- Rust 的所有权和类型系统在编译时防止数据竞争
- 三个关键 trait：`Send`、`Sync` 和借用检查器协同工作
- 线程安全是类型级保证，不是运行时检查
- "Fearless concurrency" 成为 Rust 的标志性口号

**修辞手法：**
- 从问题切入（数据竞争难以检测），然后展示 Rust 的方案
- 使用具体代码示例演示编译时保证
- 对比 Rust 的方式和其他语言的运行时方式

**篇幅：** ~3000-5000 字（长篇技术文章）

**代码密度：** 中等——演示 `Send`/`Sync` trait 和数据竞争防护

**结尾：** 强调 Rust 的安全保证自然延伸到并发编程，使编写正确的并发代码变得实用

---

## 3. Rust API Guidelines (rust-lang.github.io/api-guidelines)

**URL：** `https://rust-lang.github.io/api-guidelines/`

**结构：** 参考文档，按简短助记码组织（C-CONVENTIONS、C-COMMON-TRAITS、C-VALIDATE、C-INTEROP 等）。每条准则有代码、标题、描述和示例。

**核心设计原则：**
- **人体工程学优先：** API 应该易用且直觉化
- **类型安全与正确性：** 利用类型系统在编译时防止错误
- **零成本抽象：** 高层 API 不应带来运行时开销
- **可预测性与一致性：** 命名、错误处理、trait 实现应遵循既定模式
- **所有权与借用惯用法：** 尊重所有权模型；提供 owned 和 borrowed 变体
- **前向兼容性：** 设计可演进的 API（如 `#[non_exhaustive]`）
- **文档：** 每个公开项都应有文档和示例

**篇幅：** 书级参考（~20,000+ 字）

**代码密度：** 极高——几乎每条准则都有代码示例

---

## 4. "Rust's Golden Rule"（Niko Matsakis / 借用检查器哲学）

**来源：** 常归因于 Rust 语言团队负责人 Niko Matsakis 在 `smallcultfollowing.com` 博客和 Rust RFC 讨论中的阐述。

**核心原则：**
> 在任意时刻，你可以拥有一个可变引用，或者任意数量的不可变引用——但不能同时拥有两者。

这是借用检查器强制执行的基本不变量，在编译时防止数据竞争并确保内存安全。

**修辞手法：**
- 展示引用生命周期的可视化图表
- 简单类比（图书馆借书、白板马克笔）
- 从简单示例到边缘情况的渐进复杂度

---

## 5. Rust Design Patterns (rust-unofficial/patterns)

**URL：** `https://rust-unofficial.github.io/patterns/`

**结构：** 书格式，包含惯用法、设计模式、反模式和函数式编程模式章节。

**核心章节：**
- **惯用法：** 使用 Default trait、turbofish 语法、`mem::take`/`mem::replace`
- **设计模式：** Builder、Newtype、RAII、Visitor、Observer
- **反模式：** 应该避免的做法
- **函数式模式：** 闭包密集型惯用法

**篇幅：** 书级（~15,000+ 字）

**代码密度：** 极高——每个模式都包含完整代码示例

---

## 6. rustc-dev-guide（编译器设计原则）

**URL：** `https://rustc-dev-guide.rust-lang.org/`

**核心编译器设计原则：**
- "Do the right thing"——优先选择正确、经过深思熟虑的行为
- "Minimize surprise"——行为应该是可预测的
- 优先正确性而非速度（编译器和编译产物都是）
- "Slow but correct" 先行，后续优化
- 编译器应该是可教学的，其决策应该是可解释的

---

## 横向对比

| 文章/资源 | 结构 | 篇幅 | 代码密度 | 受众 | 结尾方式 |
|---|---|---|---|---|---|
| Zen of Rust（社区） | 格言列表 | <1000 字 | 无 | 新手 | 开放式 |
| Fearless Concurrency（Turon） | 长篇论述 | 3000-5000 字 | 中等 | 系统程序员 | 愿景声明 |
| API Guidelines | 参考编码 | 书级 | 极高 | 库作者 | 活态参考 |
| Golden Rule（Matsakis） | 概念解释 | 嵌入在文章中 | 中等 | 学习者 | 规则重述 |
| Design Patterns（非官方） | 书格式 | 书级 | 极高 | 中级开发者 | 模式目录 |
| rustc-dev-guide | 贡献者指南 | 书级 | 中等 | 编译器贡献者 | 持续指南 |

---

## 参考来源

- `https://blog.rust-lang.org/`（官方博客）
- `https://rust-lang.github.io/api-guidelines/`（API 准则）
- `https://rust-unofficial.github.io/patterns/`（设计模式书）
- `https://rustc-dev-guide.rust-lang.org/`（编译器指南）
- `https://doc.rust-lang.org/book/`（The Rust Book）
- `https://smallcultfollowing.com/`（Niko Matsakis 博客）
