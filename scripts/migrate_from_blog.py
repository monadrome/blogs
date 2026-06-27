#!/usr/bin/env python3
"""从 blog 项目迁移文章到 self-media/content/archive/"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yaml


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """解析 YAML frontmatter"""
    match = re.match(r"^---\n(.*?\n)---\n(.*)", content, re.DOTALL)
    if not match:
        return {}, content
    try:
        meta = yaml.safe_load(match.group(1))
        return meta or {}, match.group(2)
    except yaml.YAMLError:
        return {}, content


def slug_from_filename(filename: str) -> str:
    """从文件名生成 slug：2023-03-15_Title.md → 2023-03-15-title"""
    name = filename.replace(".md", "")
    # 替换空格和特殊字符为连字符
    slug = re.sub(r"[^a-zA-Z0-9一-鿿-]", "-", name)
    slug = re.sub(r"-+", "-", slug).strip("-").lower()
    return slug


def migrate_article(src: Path, archive_dir: Path):
    """迁移单篇文章"""
    content = src.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)

    slug = slug_from_filename(src.name)
    dst_dir = archive_dir / slug
    dst_dir.mkdir(parents=True, exist_ok=True)

    # 保存 article.md（只保留正文，去掉 frontmatter）
    article_path = dst_dir / "article.md"
    article_path.write_text(body, encoding="utf-8")

    # 生成 meta.yml
    meta_data = {
        "title": meta.get("title", src.stem),
        "slug": slug,
        "summary": meta.get("summary", ""),
        "author": "EricLin",
        "created": meta.get("date", ""),
        "language": "zh-CN",
        "original": True,
        "category": "后端",
        "tags": [],
        "migrated_from": "blog",
        "original_url": meta.get("url", ""),
        "views": meta.get("views", 0),
        "likes": meta.get("likes", 0),
        "platforms": {
            "juejin": {
                "status": "published",
                "url": meta.get("url", ""),
            },
            "wechat": {"status": "draft"},
            "git": {"status": "draft"},
        },
        "assets": {"cover": "", "images": [], "slides": ""},
    }
    meta_path = dst_dir / "meta.yml"
    with open(meta_path, "w", encoding="utf-8") as f:
        yaml.dump(meta_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    return slug


def main():
    if len(sys.argv) < 2:
        print("Usage: python migrate_from_blog.py /path/to/blog/articles/")
        sys.exit(1)

    blog_articles_dir = Path(sys.argv[1])
    if not blog_articles_dir.exists():
        print(f"❌ Directory not found: {blog_articles_dir}")
        sys.exit(1)

    archive_dir = Path(__file__).resolve().parent.parent / "content" / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    md_files = sorted(blog_articles_dir.glob("*.md"))
    print(f"📂 Found {len(md_files)} articles in {blog_articles_dir}")

    migrated = 0
    for src in md_files:
        try:
            slug = migrate_article(src, archive_dir)
            print(f"   ✅ {src.name} → archive/{slug}/")
            migrated += 1
        except Exception as e:
            print(f"   ❌ {src.name}: {e}")

    print(f"\n📊 Migrated {migrated}/{len(md_files)} articles to {archive_dir}")


if __name__ == "__main__":
    main()
