#!/usr/bin/env python3
"""
同步已发布文章到开源博客仓库

功能：
1. 将 content/published/ 下的文章同步到开源博客仓库
2. 自动生成 INDEX.md
3. 可选自动 commit + push
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

# 项目根目录
ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
PUBLISHED_DIR = CONTENT_DIR / "published"
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
LOG_FILE = DATA_DIR / "sync-log.jsonl"


def load_config() -> dict:
    """加载开源博客配置"""
    config_path = CONFIG_DIR / "open_source.yml"
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        sys.exit(1)
    with open(config_path) as f:
        return yaml.safe_load(f) or {}


def load_env():
    """加载 .env 文件"""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def log_sync(slug: str, status: str, detail: str = ""):
    """记录同步日志"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "slug": slug,
        "status": status,
        "detail": detail,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def clone_or_pull_repo(config: dict) -> Path:
    """克隆或更新开源博客仓库"""
    github_repo = config.get("github_repo", "")
    if not github_repo:
        print("❌ github_repo 未配置")
        sys.exit(1)

    local_dir = config.get("local_dir", "")
    if not local_dir:
        # 自动生成本地目录
        repo_name = github_repo.split("/")[-1].replace(".git", "")
        local_dir = ROOT / ".cache" / repo_name

    local_dir = Path(local_dir)

    if local_dir.exists():
        # 更新
        print(f"📥 更新仓库: {local_dir}")
        subprocess.run(["git", "pull"], cwd=local_dir, check=True, capture_output=True)
    else:
        # 克隆
        print(f"📥 克隆仓库: {github_repo}")
        local_dir.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", github_repo, str(local_dir)], check=True, capture_output=True)

    return local_dir


def load_article_meta(article_dir: Path) -> dict:
    """加载文章元数据"""
    meta_path = article_dir / "meta.yml"
    if not meta_path.exists():
        return {}
    with open(meta_path) as f:
        return yaml.safe_load(f) or {}


def should_sync(meta: dict, config: dict) -> bool:
    """判断是否应该同步"""
    sync_rules = config.get("sync_rules", {})

    # 检查平台状态
    platforms = meta.get("platforms", {})
    target_platforms = sync_rules.get("platforms", ["juejin"])

    for platform in target_platforms:
        platform_info = platforms.get(platform, {})
        status = platform_info.get("status", "")
        if status == "published":
            return True

    return False


def format_frontmatter(meta: dict, config: dict) -> str:
    """格式化 frontmatter"""
    template = config.get("frontmatter_template", "")
    if not template:
        # 默认模板
        template = """---
title: "{title}"
date: {date}
url: {url}
category: {category}
tags: [{tags}]
---
"""

    # 获取掘金 URL
    juejin_url = meta.get("platforms", {}).get("juejin", {}).get("url", "")
    original_stats = meta.get("original_stats", {})

    return template.format(
        title=meta.get("title", ""),
        date=meta.get("created", ""),
        url=juejin_url,
        juejin_url=juejin_url,
        views=original_stats.get("views", 0),
        likes=original_stats.get("likes", 0),
        collects=original_stats.get("collects", 0),
        category=meta.get("category", ""),
        tags=", ".join(meta.get("tags", [])),
    )


def sync_article(article_dir: Path, target_dir: Path, config: dict) -> bool:
    """同步单篇文章"""
    meta = load_article_meta(article_dir)

    if not should_sync(meta, config):
        return False

    article_path = article_dir / "article.md"
    if not article_path.exists():
        return False

    # 生成目标文件名
    date = meta.get("created", "")
    title = meta.get("title", "")
    slug = meta.get("slug", article_dir.name)
    filename = f"{date}_{title}.md" if date else f"{title}.md"

    target_path = target_dir / filename

    # 读取文章内容
    content = article_path.read_text(encoding='utf-8')

    # 生成 frontmatter
    frontmatter = format_frontmatter(meta, config)

    # 写入目标文件
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(frontmatter + "\n" + content)

    return True


def generate_index(target_dir: Path, articles: list[dict]):
    """生成 INDEX.md"""
    index_path = target_dir / "INDEX.md"

    # 按日期排序
    articles.sort(key=lambda x: x.get("date", ""), reverse=True)

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("# 文章索引\n\n")
        f.write(f"共 {len(articles)} 篇文章\n\n")
        f.write("| # | 日期 | 标题 | 分类 |\n")
        f.write("|---|------|------|------|\n")
        for i, article in enumerate(articles, 1):
            f.write(f"| {i} | {article['date']} | [{article['title']}]({article['filename']}) | {article['category']} |\n")


def git_commit_and_push(local_dir: Path, config: dict):
    """Git commit 和 push"""
    commit_prefix = config.get("commit_prefix", "docs: ")
    auto_push = config.get("auto_push", False)
    branch = config.get("branch", "main")

    # git add
    subprocess.run(["git", "add", "."], cwd=local_dir, check=True)

    # git commit
    commit_msg = f"{commit_prefix}同步文章 {datetime.now().strftime('%Y-%m-%d')}"
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=local_dir, check=True)

    print(f"  ✅ Git committed: {commit_msg}")

    # git push
    if auto_push:
        subprocess.run(["git", "push", "origin", branch], cwd=local_dir, check=True)
        print(f"  ✅ Pushed to origin/{branch}")


def main():
    parser = argparse.ArgumentParser(description="同步文章到开源博客")
    parser.add_argument("--dry-run", action="store_true", help="试运行，不实际写入")
    parser.add_argument("--no-git", action="store_true", help="不执行 git 操作")
    parser.add_argument("--article", help="只同步指定文章的 slug")
    args = parser.parse_args()

    # 加载配置
    load_env()
    config = load_config()
    open_source_config = config.get("open_source", {})

    if not open_source_config.get("enabled", False):
        print("❌ 开源博客同步未启用")
        sys.exit(1)

    # 克隆或更新仓库
    if not args.dry_run:
        local_dir = clone_or_pull_repo(open_source_config)
        articles_dir = local_dir / open_source_config.get("articles_dir", "articles")
        articles_dir.mkdir(parents=True, exist_ok=True)
    else:
        local_dir = None
        articles_dir = None

    # 获取所有已发布文章
    if not PUBLISHED_DIR.exists():
        print("❌ 没有已发布的文章")
        sys.exit(1)

    article_dirs = sorted([d for d in PUBLISHED_DIR.iterdir() if d.is_dir()])
    print(f"📁 找到 {len(article_dirs)} 篇已发布文章")

    # 同步
    success = 0
    failed = 0
    skipped = 0
    synced_articles = []

    for article_dir in article_dirs:
        if args.article and article_dir.name != args.article:
            continue

        try:
            meta = load_article_meta(article_dir)

            if not should_sync(meta, open_source_config):
                skipped += 1
                continue

            if args.dry_run:
                print(f"  📝 [DRY RUN] {article_dir.name}")
                success += 1
                continue

            if sync_article(article_dir, articles_dir, open_source_config):
                success += 1
                print(f"  ✅ {article_dir.name}")
                synced_articles.append({
                    "date": meta.get("created", ""),
                    "title": meta.get("title", ""),
                    "filename": f"{meta.get('created', '')}_{meta.get('title', '')}.md",
                    "category": meta.get("category", ""),
                })
                log_sync(article_dir.name, "success")
            else:
                skipped += 1

        except Exception as e:
            failed += 1
            print(f"  ❌ {article_dir.name}: {e}")
            log_sync(article_dir.name, "failed", str(e))

    # 生成索引
    if not args.dry_run and synced_articles:
        generate_index(articles_dir, synced_articles)

    # Git 操作
    if not args.dry_run and not args.no_git and synced_articles:
        print("\n📦 Git 操作...")
        git_commit_and_push(local_dir, open_source_config)

    # 汇总
    print(f"\n{'='*50}")
    print(f"📊 同步完成")
    print(f"  成功: {success}")
    print(f"  跳过: {skipped}")
    print(f"  失败: {failed}")
    if not args.dry_run:
        print(f"  目标: {local_dir}")


if __name__ == "__main__":
    main()
