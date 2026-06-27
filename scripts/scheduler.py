#!/usr/bin/env python3
"""定时发布调度器 — 检查 draft 中 schedule.publish_at，到期自动发布"""

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parent.parent
DRAFTS_DIR = ROOT / "content" / "drafts"
CONFIG_DIR = ROOT / "config"


def load_schedule_config() -> dict:
    """加载 schedule.yml 配置"""
    config_path = CONFIG_DIR / "schedule.yml"
    if not config_path.exists():
        return {}
    try:
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError:
        return {}


def load_all_drafts() -> list[tuple[str, dict, Path]]:
    """加载所有草稿的 meta.yml（跳过解析失败的文件）"""
    drafts = []
    if not DRAFTS_DIR.exists():
        return drafts
    for d in sorted(DRAFTS_DIR.iterdir()):
        if d.is_dir():
            meta_path = d / "meta.yml"
            if meta_path.exists():
                try:
                    with open(meta_path) as f:
                        meta = yaml.safe_load(f)
                    if meta:
                        drafts.append((d.name, meta, d))
                except yaml.YAMLError as e:
                    print(f"⚠️  Skipping {d.name}: invalid meta.yml ({e})")
    return drafts


def is_in_publish_window(config: dict) -> bool:
    """检查当前时间是否在发布窗口内"""
    scheduler_config = config.get("scheduler", {})
    window = config.get("publish_window", {})
    start_str = window.get("start", "00:00")
    end_str = window.get("end", "23:59")
    tz_name = scheduler_config.get("timezone", "Asia/Shanghai")

    try:
        tz = ZoneInfo(tz_name)
    except (KeyError, Exception):
        tz = timezone.utc

    now = datetime.now(tz)
    current_time = now.strftime("%H:%M")

    # 处理跨午夜的窗口（如 23:00 - 06:00）
    if start_str <= end_str:
        return start_str <= current_time <= end_str
    else:
        return current_time >= start_str or current_time <= end_str


def is_due(meta: dict, config: dict) -> tuple[bool, list[str]]:
    """检查是否到达发布时间"""
    schedule = meta.get("schedule", {})
    publish_at = schedule.get("publish_at", "")
    if not publish_at:
        return False, []

    try:
        target = datetime.fromisoformat(publish_at)
        if target.tzinfo is None:
            target = target.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        if now < target:
            return False, []

        # 检查发布窗口
        if not is_in_publish_window(config):
            return False, []

        # 过滤掉已发布的平台
        platforms = schedule.get("platforms", ["juejin", "wechat"])
        published = meta.get("platforms", {})
        pending = [p for p in platforms if published.get(p, {}).get("status") != "published"]
        return bool(pending), pending

    except (ValueError, TypeError):
        return False, []


def publish_article(slug: str, platforms: list[str]):
    """调用 publish.py 发布文章"""
    for platform in platforms:
        print(f"[{datetime.now().isoformat()}] 🚀 Auto-publishing {slug} to {platform}")
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "publish.py"),
             "--slug", slug, "--platform", platform],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"   ✅ {platform} OK")
        else:
            print(f"   ❌ {platform} failed: {result.stderr[:200]}")


def run_once():
    """单次检查"""
    config = load_schedule_config()
    drafts = load_all_drafts()
    if not drafts:
        print("No drafts found.")
        return

    published_any = False
    for slug, meta, path in drafts:
        due, platforms = is_due(meta, config)
        if due:
            publish_article(slug, platforms)
            published_any = True

    if not published_any:
        print(f"[{datetime.now().isoformat()}] No articles due for publishing.")


def run_loop(interval: int = 600):
    """持续运行，每 interval 秒检查一次"""
    print(f"🕐 Scheduler started, checking every {interval}s")
    while True:
        try:
            run_once()
        except Exception as e:
            print(f"❌ Scheduler error: {e}")
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="定时发布调度器")
    parser.add_argument("--once", action="store_true", help="单次检查后退出")
    parser.add_argument("--interval", type=int, default=600, help="检查间隔（秒）")
    args = parser.parse_args()

    if args.once:
        run_once()
    else:
        run_loop(args.interval)


if __name__ == "__main__":
    main()
