---
name: self-media-publish
description: "发布文章到多平台（掘金/公众号/Git）"
version: "1.0.0"
metadata:
  author: EricLin
---

# self-media-publish

将 content/drafts/ 中的文章发布到配置的平台。

## 触发词

- "发布文章"
- "publish article"
- "发布到掘金"
- "发布到公众号"

## 工作流程

### 1. 选择文章

列出 `content/drafts/` 中所有草稿：

```bash
ls content/drafts/
```

让用户选择要发布的文章 slug。

### 2. 检查就绪状态

读取 `content/drafts/<slug>/meta.yml`，检查：
- [ ] title 不为空
- [ ] summary 不为空
- [ ] article.md 存在且有内容
- [ ] 封面图存在（公众号要求）

### 3. 执行发布

```bash
# 发布到所有已配置平台
python scripts/publish.py --slug <slug>

# 只发布到特定平台
python scripts/publish.py --slug <slug> --platform juejin
python scripts/publish.py --slug <slug> --platform wechat
python scripts/publish.py --slug <slug> --platform git
```

### 4. 验证发布结果

读取更新后的 meta.yml，确认各平台 status 已更新为 `published`。

## 注意事项

- 掘金 cookie 过期时会报错，提示用户在浏览器中刷新 cookie
- 公众号需要封面图，如果缺少会提示先生成
- Git 发布会自动 commit + push（如果 GIT_AUTO_PUSH=true）
- 只有 Git 平台会将文章从 drafts/ 移到 published/；单独发布掘金/公众号时文章留在 drafts/
- 已发布的平台会被自动跳过（检查 meta.yml 中各平台的 status 字段）
- 分类映射：meta.yml 中的 `category: "后端"` 会通过 config/categories.yml 自动转为掘金 category_id

## 错误处理

| 错误 | 处理 |
|------|------|
| Cookie 过期 | 提示用户在浏览器登录掘金后复制新 cookie |
| 图片上传失败 | 跳过该图片，继续发布（不影响正文） |
| 公众号 API 错误 | 检查 app_id/app_secret 配置 |
| Git push 失败 | 提示手动 push 或检查 remote 配置 |
| meta.yml 为空 | 报错退出，提示检查文件格式 |
