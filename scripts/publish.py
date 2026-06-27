#!/usr/bin/env python3
"""统一发布入口 — 发布文章到掘金/公众号/Git"""

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
DRAFTS_DIR = CONTENT_DIR / "drafts"
PUBLISHED_DIR = CONTENT_DIR / "published"
DATA_DIR = ROOT / "data"
LOG_FILE = DATA_DIR / "publish-log.jsonl"
CONFIG_DIR = ROOT / "config"


def load_platform_config() -> dict:
    """加载 platforms.yml 配置"""
    config_path = CONFIG_DIR / "platforms.yml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    return {}


def load_categories() -> dict:
    """加载 categories.yml，返回 {分类名: category_id} 映射"""
    config_path = CONFIG_DIR / "categories.yml"
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        data = yaml.safe_load(f) or {}
    # 构建 name → id 映射
    mapping = {}
    for name, info in data.get("categories", {}).items():
        mapping[name] = info.get("id", "")
        for alias in info.get("aliases", []):
            mapping[alias] = info.get("id", "")
    return mapping


def resolve_category_id(meta: dict, platform_config: dict) -> str:
    """将 meta.yml 中的 category 字符串解析为掘金 category_id"""
    # 优先用 meta 中的 category_id（数字形式）
    if "category_id" in meta:
        return meta["category_id"]
    # 其次从 category 字符串映射
    category_name = meta.get("category", "")
    if category_name:
        categories = load_categories()
        if category_name in categories:
            return categories[category_name]
    # 最后用平台配置或环境变量默认值
    juejin_config = platform_config.get("platforms", {}).get("juejin", {})
    return juejin_config.get("default_category", os.environ.get("JUEJIN_DEFAULT_CATEGORY", ""))


def load_env():
    """加载 .env 文件到环境变量"""
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


def load_meta(slug: str) -> dict:
    """加载文章元数据（自动搜索 drafts/ 和 published/）"""
    for dir_ in [DRAFTS_DIR, PUBLISHED_DIR]:
        meta_path = dir_ / slug / "meta.yml"
        if meta_path.exists():
            with open(meta_path) as f:
                return yaml.safe_load(f) or {}
    print(f"❌ meta.yml not found for slug: {slug}")
    sys.exit(1)


def find_article_dir(slug: str) -> Path:
    """查找文章目录（drafts 或 published）"""
    for dir_ in [DRAFTS_DIR, PUBLISHED_DIR]:
        if (dir_ / slug).exists():
            return dir_ / slug
    print(f"❌ Article directory not found for slug: {slug}")
    sys.exit(1)


def save_meta(slug: str, meta: dict):
    """保存文章元数据（自动定位当前目录）"""
    article_dir = find_article_dir(slug)
    meta_path = article_dir / "meta.yml"
    with open(meta_path, "w") as f:
        yaml.dump(meta, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def log_publish(slug: str, platform: str, status: str, detail: str = ""):
    """记录发布日志"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "slug": slug,
        "platform": platform,
        "status": status,
        "detail": detail,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def publish_juejin(slug: str, meta: dict, article_path: Path, platform_config: dict) -> bool:
    """发布到掘金"""
    from juejin import ArticleMeta, JuejinClient, JuejinAPIError

    cookie = os.environ.get("JUEJIN_COOKIE", "")
    if not cookie:
        print("❌ JUEJIN_COOKIE not set in .env")
        return False

    juejin_config = platform_config.get("platforms", {}).get("juejin", {})
    client = JuejinClient(cookie, request_delay=juejin_config.get("request_delay", 1.0))
    if not client.verify_auth():
        print("❌ Juejin cookie expired. Please refresh in browser.")
        return False

    # 上传封面图
    cover_url = ""
    cover_path = DRAFTS_DIR / slug / meta.get("assets", {}).get("cover", "")
    if cover_path.exists():
        print("📤 Uploading cover image...")
        try:
            cover_url = client.upload_image(str(cover_path))
            print(f"   ✅ Cover uploaded: {cover_url}")
        except Exception as e:
            print(f"   ⚠️  Cover upload failed: {e}")

    # 上传内嵌图片并替换路径
    content = article_path.read_text()
    images_dir = DRAFTS_DIR / slug / "images"
    if images_dir.exists():
        for img in sorted(images_dir.iterdir()):
            if img.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"):
                local_ref = f"images/{img.name}"
                if local_ref in content:
                    try:
                        cdn_url = client.upload_image(str(img))
                        content = content.replace(local_ref, cdn_url)
                        print(f"   ✅ Replaced {local_ref} → CDN")
                    except Exception as e:
                        print(f"   ⚠️  Image upload failed ({img.name}): {e}")

    # 验证必填字段
    title = meta.get("title", "").strip()
    if not title:
        print("❌ title is empty in meta.yml")
        return False
    if not content.strip():
        print("❌ article.md is empty")
        return False

    # 构建文章对象
    article = ArticleMeta(
        title=title,
        mark_content=content,
        category_id=resolve_category_id(meta, platform_config),
        tag_ids=meta.get("tag_ids", []),
        brief_content=meta.get("summary", ""),
        cover_image=cover_url,
        is_original=meta.get("original", True),
        article_id=meta.get("platforms", {}).get("juejin", {}).get("article_id", ""),
    )

    try:
        # 保存草稿
        print("📝 Saving draft...")
        draft_id = client.save_draft(article)
        print(f"   ✅ Draft saved: {draft_id}")

        # 发布
        print("🚀 Publishing...")
        article_id = client.publish(article, draft_id)
        print(f"   ✅ Published! article_id={article_id}")

        # 更新 meta
        meta.setdefault("platforms", {}).setdefault("juejin", {}).update(
            {
                "status": "published",
                "article_id": article_id,
                "draft_id": draft_id,
                "published_at": datetime.now(timezone.utc).isoformat(),
                "url": f"https://juejin.cn/post/{article_id}",
            }
        )
        log_publish(slug, "juejin", "success", f"article_id={article_id}")
        return True

    except JuejinAPIError as e:
        print(f"   ❌ Juejin API error: {e}")
        log_publish(slug, "juejin", "failed", str(e))
        return False


def publish_wechat(slug: str, meta: dict, article_path: Path) -> bool:
    """发布到微信公众号（委托 baoyu-post-to-wechat）"""
    print("📢 WeChat publishing delegates to /baoyu-post-to-wechat skill")
    print("   Run: /baoyu-post-to-wechat with the article file")
    print(f"   File: {article_path}")
    log_publish(slug, "wechat", "pending", "delegated to skill")
    return True


def publish_git(slug: str, meta: dict) -> bool:
    """Git 自动提交"""
    auto_push = os.environ.get("GIT_AUTO_PUSH", "false").lower() == "true"
    remote = os.environ.get("GIT_REMOTE", "origin")
    branch = os.environ.get("GIT_BRANCH", "main")

    # 移动文章到 published/
    src = DRAFTS_DIR / slug
    dst = PUBLISHED_DIR / slug
    if dst.exists():
        print(f"⚠️  Published dir already exists: {dst}")
    else:
        PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        print(f"📁 Moved to published/{slug}/")

    # git add + commit
    try:
        subprocess.run(["git", "add", f"content/published/{slug}/"], cwd=ROOT, check=True)
        title = meta.get("title", slug)
        subprocess.run(
            ["git", "commit", "-m", f"publish: {title}"],
            cwd=ROOT,
            check=True,
        )
        print("   ✅ Git committed")

        if auto_push:
            subprocess.run(["git", "push", remote, branch], cwd=ROOT, check=True)
            print(f"   ✅ Pushed to {remote}/{branch}")

        log_publish(slug, "git", "success")
        return True

    except subprocess.CalledProcessError as e:
        print(f"   ❌ Git error: {e}")
        log_publish(slug, "git", "failed", str(e))
        return False


def show_status(slug: str, meta: dict):
    """显示发布状态"""
    platforms = meta.get("platforms", {})
    print(f"\n📊 发布状态: {meta.get('title', slug)}")
    print(f"   Slug: {slug}")
    print()
    for name, info in platforms.items():
        status = info.get("status", "unknown")
        icon = {"published": "✅", "draft": "📝", "failed": "❌"}.get(status, "❓")
        url = info.get("url", "")
        published_at = info.get("published_at", "")
        print(f"   {icon} {name}: {status}")
        if url:
            print(f"      URL: {url}")
        if published_at:
            print(f"      Published: {published_at}")
    print()


def main():
    parser = argparse.ArgumentParser(description="发布文章到多平台")
    parser.add_argument("--slug", required=True, help="文章 slug（目录名）")
    parser.add_argument("--platform", choices=["juejin", "wechat", "git"], help="指定平台（默认全部）")
    parser.add_argument("--status", action="store_true", help="查看发布状态")
    parser.add_argument("--sync-open-source", action="store_true", help="发布后同步到开源博客")
    args = parser.parse_args()

    load_env()
    platform_config = load_platform_config()
    meta = load_meta(args.slug)

    article_dir = find_article_dir(args.slug)
    article_path = article_dir / "article.md"

    if args.status:
        show_status(args.slug, meta)
        return

    if not article_path.exists():
        print(f"❌ article.md not found: {article_path}")
        sys.exit(1)

    # 确定要发布的平台（检查 enabled 标志）
    if args.platform:
        platforms_to_publish = [args.platform]
    else:
        all_platforms = platform_config.get("platforms", {})
        platforms_to_publish = [
            p for p in ["juejin", "wechat", "git"]
            if all_platforms.get(p, {}).get("enabled", True)
        ]

    # 跳过已发布的平台
    published = meta.get("platforms", {})
    platforms_to_publish = [
        p for p in platforms_to_publish
        if published.get(p, {}).get("status") != "published"
    ]
    if not platforms_to_publish:
        print("✅ All platforms already published.")
        return

    results = {}

    for platform in platforms_to_publish:
        print(f"\n{'='*50}")
        print(f"📢 Publishing to: {platform}")
        print(f"{'='*50}")

        if platform == "juejin":
            results["juejin"] = publish_juejin(args.slug, meta, article_path, platform_config)
        elif platform == "wechat":
            results["wechat"] = publish_wechat(args.slug, meta, article_path)
        elif platform == "git":
            # git 最后执行，先保存 meta（因为 git 会移动目录）
            save_meta(args.slug, meta)
            results["git"] = publish_git(args.slug, meta)

    # 保存更新后的 meta（git 模式下已在上面保存过）
    if any(results.values()):
        if "git" not in results or not results.get("git"):
            save_meta(args.slug, meta)

    # 汇总
    print(f"\n{'='*50}")
    print("📊 发布结果汇总")
    print(f"{'='*50}")
    for platform, success in results.items():
        icon = "✅" if success else "❌"
        print(f"   {icon} {platform}")

    # 同步到开源博客
    if args.sync_open_source and any(results.values()):
        print(f"\n{'='*50}")
        print("🔄 同步到开源博客")
        print(f"{'='*50}")
        try:
            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "sync_to_open_source.py"), "--article", args.slug],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"   ❌ 同步失败: {e}")


if __name__ == "__main__":
    main()
