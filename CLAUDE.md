# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

技术博客内容管理中心 — 从写作到多平台发布的完整工作流。包含 105 篇历史文章（从掘金导出）和两个 companion 项目提供可运行代码示例。

## Project Structure

```
blog/
├── content/                            # 内容仓库（核心）
│   ├── _templates/                     # 文章模板
│   ├── drafts/                         # 草稿区（写作中）
│   ├── published/                      # 已发布区
│   └── archive/                        # 105 篇历史文章
│
├── blog-demo/                          # companion (Groovy, Spring Boot 3.2.3)
├── parfun/                             # companion (Java 21, Spring Boot 3.5.4)
│
├── scripts/                            # Python 工具链
│   ├── publish.py                      # 统一发布入口
│   ├── scheduler.py                    # 定时调度器
│   ├── sync_to_open_source.py          # 同步到开源博客
│   ├── migrate_articles.py             # 迁移历史文章
│   ├── git_sync.py                     # Git 自动提交
│   └── juejin/                         # 掘金 API 客户端
│
├── config/                             # 配置文件
│   ├── platforms.yml                   # 平台配置
│   ├── categories.yml                  # 掘金分类映射
│   ├── schedule.yml                    # 调度配置
│   └── open_source.yml                 # 开源博客配置
│
├── .claude/skills/                     # 所有 skills
│   ├── blog-writer/                    # 写技术博客
│   ├── source-code-reader/             # 写源码解读
│   ├── baoyu-post-to-wechat/           # 公众号发布
│   └── ... (其他内容创作 skills)
│
├── scheduler/                          # macOS launchd 配置
├── articles/                           # 历史文章原始文件（待迁移）
├── src/                                # Spring Boot 应用
├── build.gradle
└── CLAUDE.md
```

## Content Lifecycle

```
写作 (blog-writer skill)
  │
  ▼
content/drafts/<slug>/
  │
  ├─ article.md
  ├─ meta.yml
  └─ images/
  │
  ▼
处理管道
  │
  ├─ 自动配图 (baoyu-article-illustrator)
  ├─ 自动修改 ref
  ├─ 去 AI 味润色 (remove-ai-flavor)
  │
  ▼
发布
  │
  ├─ 掘金（定时）
  ├─ 公众号（委托 baoyu-post-to-wechat）
  └─ 同步到开源博客
  │
  ▼
content/published/<slug>/
```

## Build & Test Commands

### Root project (Spring Boot)
```bash
./gradlew build          # Build
./gradlew test           # Run tests (JUnit 5)
./gradlew bootRun        # Start Spring Boot app (port 8080)
```

### blog-demo (Groovy)
```bash
cd blog-demo
./gradlew build
./gradlew test
./gradlew bootRun
```

### parfun (Java)
```bash
cd parfun
./gradlew build
./gradlew test
# Most classes have their own main method — run directly from IDE
```

## Publishing Commands

```bash
# 迁移历史文章（首次）
python scripts/migrate_articles.py

# 发布文章到所有平台
python scripts/publish.py --slug <article-slug>

# 只发布到掘金
python scripts/publish.py --slug <article-slug> --platform juejin

# 发布后同步到开源博客
python scripts/publish.py --slug <article-slug> --sync-open-source

# 查看发布状态
python scripts/publish.py --slug <article-slug> --status

# 同步所有已发布文章到开源博客
python scripts/sync_to_open_source.py

# 启动定时调度器
python scripts/scheduler.py --once

# 安装 launchd 定时任务
launchctl load scheduler/com.blog.publish.plist
```

## Configuration

### .env (copy from .env.example)
```bash
# 掘金
JUEJIN_COOKIE="sessionid=xxx; sessionid_ss=xxx; passport_csrf_token=xxx"

# 微信公众号
WECHAT_APP_ID="wx..."
WECHAT_APP_SECRET="..."

# 开源博客同步
OPEN_SOURCE_GITHUB_REPO="https://github.com/username/blog.git"
OPEN_SOURCE_AUTO_PUSH="false"

# 定时调度
SCHEDULER_ENABLED="false"
SCHEDULER_INTERVAL="600"
```

### config/open_source.yml
```yaml
open_source:
  enabled: true
  github_repo: ""  # GitHub 仓库地址
  branch: "main"
  auto_commit: true
  auto_push: false
```

## Skills

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `blog-writer` | "写博客：xxx" | 写技术博客，输出到 content/drafts/ |
| `source-code-reader` | "写博客：源码解读 xxx" | 写源码解读文章 |
| `baoyu-post-to-wechat` | `/baoyu-post-to-wechat` | 发布到微信公众号 |
| `remove-ai-flavor` | `/remove-ai-flavor` | 去 AI 味润色 |
| `baoyu-article-illustrator` | `/baoyu-article-illustrator` | 自动生成文章配图 |

## Articles

- **历史文章**: `articles/` — 105 篇从掘金导出（2023-2026）
- **归档**: `content/archive/` — 迁移后的格式
- **索引**: `INDEX.md` — 按阅读量排序

### Article Format

```yaml
---
title: "Article Title"
date: YYYY-MM-DD
url: https://juejin.cn/post/xxx
views: number
likes: number
collects: number
source: nuxt|html
---
```

## Content Themes (by frequency)

- **CompletableFuture & async programming** — source code analysis, pitfalls, best practices
- **Guava library** — immutable collections, utilities, Forwarding classes
- **Concurrent programming** — thread pools, locks, COW, ConcurrentHashMap
- **Functional programming** — Vavr/Javaslang, monads, lazy evaluation
- **Java fundamentals** — generics, collections, reference types, JVM internals
- **Design patterns & code quality** — Builder pattern, fluent interfaces, refactoring

## Git Workflow

- Main branch: `main`
- Articles and code are committed together
- Sub-projects (`blog-demo/`, `parfun/`) are part of this repo
- Use `--sync-open-source` to sync published articles to open source blog

## Language

项目文档和代码注释以中文为主，与用户交互默认使用中文。
