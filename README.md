# blog

技术博客内容管理中心 — 从写作到多平台发布的完整工作流。

## 功能

- 📝 **文章写作** — 技术博客、源码解读
- 🎨 **自动配图** — 封面图、文章配图
- 📢 **多平台发布** — 稀土掘金、微信公众号
- ⏰ **定时发布** — 设定时间，自动发布
- 🔄 **开源同步** — 同步到 GitHub 开源博客
- 💻 **Companion 项目** — 可运行的代码示例

## 快速开始

### 1. 安装依赖

```bash
# Python 依赖
pip install requests pyyaml

# Java 项目
./gradlew build
```

### 2. 配置凭证

```bash
cp .env.example .env
# 编辑 .env，填入：
#   JUEJIN_COOKIE — 掘金登录 cookie
#   WECHAT_APP_ID / WECHAT_APP_SECRET — 公众号（可选）
#   OPEN_SOURCE_GITHUB_REPO — 开源博客仓库地址（可选）
```

### 3. 迁移历史文章（首次）

```bash
python scripts/migrate_articles.py
# 将 articles/ 下的 105 篇文章迁移到 content/archive/
```

### 4. 写一篇文章

```bash
# 使用 Claude Code skill
/blog-writer "Java 虚拟线程实战"

# 或手动创建
cp content/_templates/article.md content/drafts/my-article/article.md
cp content/_templates/meta.yml content/drafts/my-article/meta.yml
```

### 5. 发布

```bash
# 发布到所有已启用平台
python scripts/publish.py --slug my-article

# 只发布到掘金
python scripts/publish.py --slug my-article --platform juejin

# 发布后同步到开源博客
python scripts/publish.py --slug my-article --sync-open-source

# 查看发布状态
python scripts/publish.py --slug my-article --status
```

### 6. 同步到开源博客

```bash
# 同步所有已发布文章
python scripts/sync_to_open_source.py

# 试运行
python scripts/sync_to_open_source.py --dry-run
```

### 7. 定时发布

编辑 `meta.yml` 中的 `schedule` 字段：

```yaml
schedule:
  publish_at: "2026-06-28T09:00:00+08:00"
  platforms: ["juejin", "wechat"]
```

启动调度器：

```bash
# 单次检查
python scripts/scheduler.py --once

# 持续运行
python scripts/scheduler.py

# macOS 原生定时任务
launchctl load scheduler/com.blog.publish.plist
```

## 项目结构

```
blog/
├── content/                            # 内容仓库
│   ├── _templates/                     # 文章模板
│   ├── drafts/                         # 草稿
│   ├── published/                      # 已发布
│   └── archive/                        # 历史文章
├── blog-demo/                          # companion (Groovy)
├── parfun/                             # companion (Java)
├── scripts/                            # Python 工具链
│   ├── publish.py                      # 统一发布入口
│   ├── scheduler.py                    # 定时调度器
│   ├── sync_to_open_source.py          # 同步到开源博客
│   └── juejin/                         # 掘金 API
├── config/                             # 配置文件
├── .claude/skills/                     # Claude Code skills
├── scheduler/                          # macOS launchd
├── articles/                           # 历史文章原始文件
└── src/                                # Spring Boot 应用
```

## Companion 项目

### blog-demo

Groovy + Spring Boot 3.2.3 — 可运行的 Spring Boot 示例

```bash
cd blog-demo
./gradlew bootRun
```

### parfun

Java 21 + Spring Boot 3.5.4 — 并行编程和函数式编程实验

```bash
cd parfun
# 大部分类有自己的 main 方法，直接从 IDE 运行
```

## 配置参考

### config/platforms.yml

```yaml
platforms:
  juejin:
    enabled: true
    request_delay: 1.0
    default_category: "6809637769959178254"
  wechat:
    enabled: true
  git:
    enabled: true
    auto_push: false
```

### config/open_source.yml

```yaml
open_source:
  enabled: true
  github_repo: "https://github.com/username/blog.git"
  branch: "main"
  auto_commit: true
  auto_push: false
```

## Skills

| Skill | 用途 |
|-------|------|
| `/blog-writer` | 写技术博客 |
| `/source-code-reader` | 写源码解读 |
| `/baoyu-post-to-wechat` | 发布到公众号 |
| `/remove-ai-flavor` | 去 AI 味润色 |
| `/baoyu-article-illustrator` | 自动生成文章配图 |

## License

Private use only.
