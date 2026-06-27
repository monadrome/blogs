#!/usr/bin/env python3
"""
迁移 articles/ 下的历史文章到 content/archive/ 格式

将：
  articles/2024-09-08_文章标题.md
  ↓
  content/archive/2024-09-08-文章标题/
    ├── article.md
    └── meta.yml
"""

import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

# 项目根目录
ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = ROOT / "articles"
ARCHIVE_DIR = ROOT / "content" / "archive"


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """解析 YAML frontmatter"""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if not match:
        return {}, content

    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        meta = {}

    return meta, match.group(2)


def sanitize_slug(title: str) -> str:
    """将标题转换为 slug"""
    # 移除特殊字符，保留中文、英文、数字、连字符
    slug = re.sub(r'[^\w一-鿿-]', '-', title)
    # 合并多个连字符
    slug = re.sub(r'-+', '-', slug)
    # 移除首尾连字符
    slug = slug.strip('-')
    return slug


def extract_date(filename: str) -> str:
    """从文件名提取日期"""
    match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
    return match.group(1) if match else ""


def migrate_article(filepath: Path) -> bool:
    """迁移单篇文章"""
    content = filepath.read_text(encoding='utf-8')
    frontmatter, body = parse_frontmatter(content)

    # 提取日期
    date = extract_date(filepath.stem)
    if not date:
        date = frontmatter.get('date', '')

    # 提取标题
    title = frontmatter.get('title', filepath.stem)
    if not title:
        # 尝试从文件名提取
        title = re.sub(r'^\d{4}-\d{2}-\d{2}_', '', filepath.stem)

    # 生成 slug
    slug = f"{date}-{sanitize_slug(title)}" if date else sanitize_slug(title)

    # 创建目标目录
    target_dir = ARCHIVE_DIR / slug
    target_dir.mkdir(parents=True, exist_ok=True)

    # 创建 meta.yml
    meta = {
        'title': title,
        'slug': slug,
        'summary': '',
        'author': 'EricLin',
        'created': date,
        'language': 'zh-CN',
        'original': True,
        'category': '后端',
        'tags': [],
        'platforms': {
            'juejin': {
                'status': 'published',
                'article_id': '',
                'draft_id': '',
                'published_at': '',
                'url': frontmatter.get('url', ''),
            },
            'wechat': {
                'status': 'draft',
                'media_id': '',
                'published_at': '',
                'url': '',
            },
            'github': {
                'status': 'draft',
                'commit_hash': '',
                'pushed_at': '',
            },
        },
        'assets': {
            'cover': '',
            'images': [],
            'slides': '',
        },
        'schedule': {
            'publish_at': '',
            'platforms': ['juejin', 'wechat'],
        },
        # 保留原始统计数据
        'original_stats': {
            'views': frontmatter.get('views', 0),
            'likes': frontmatter.get('likes', 0),
            'collects': frontmatter.get('collects', 0),
            'source': frontmatter.get('source', ''),
        },
    }

    # 写入 meta.yml
    meta_path = target_dir / "meta.yml"
    with open(meta_path, 'w', encoding='utf-8') as f:
        yaml.dump(meta, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # 写入 article.md
    article_path = target_dir / "article.md"
    article_path.write_text(body, encoding='utf-8')

    return True


def main():
    """主函数"""
    if not ARTICLES_DIR.exists():
        print(f"❌ 文章目录不存在: {ARTICLES_DIR}")
        sys.exit(1)

    # 确保目标目录存在
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # 获取所有文章
    articles = sorted(ARTICLES_DIR.glob("*.md"))
    print(f"📁 找到 {len(articles)} 篇文章")

    # 迁移
    success = 0
    failed = 0
    for article in articles:
        try:
            if migrate_article(article):
                success += 1
                print(f"  ✅ {article.name}")
            else:
                failed += 1
                print(f"  ❌ {article.name}")
        except Exception as e:
            failed += 1
            print(f"  ❌ {article.name}: {e}")

    # 汇总
    print(f"\n{'='*50}")
    print(f"📊 迁移完成")
    print(f"  成功: {success}")
    print(f"  失败: {failed}")
    print(f"  目标: {ARCHIVE_DIR}")


if __name__ == "__main__":
    main()
