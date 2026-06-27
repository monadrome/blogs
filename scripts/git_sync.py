#!/usr/bin/env python3
"""Git 自动提交 — 将 published/ 中的内容提交到 git"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_env():
    """加载 .env"""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def git_commit(message: str, paths: list[str] | None = None) -> bool:
    """执行 git add + commit"""
    try:
        if paths:
            for p in paths:
                subprocess.run(["git", "add", p], cwd=ROOT, check=True)
        else:
            subprocess.run(["git", "add", "content/published/"], cwd=ROOT, check=True)

        # 检查是否有变更
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=ROOT,
            capture_output=True,
        )
        if result.returncode == 0:
            print("No changes to commit.")
            return False

        subprocess.run(["git", "commit", "-m", message], cwd=ROOT, check=True)
        print(f"✅ Committed: {message}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        return False


def git_push() -> bool:
    """推送到远程"""
    auto_push = os.environ.get("GIT_AUTO_PUSH", "false").lower() == "true"
    if not auto_push:
        print("GIT_AUTO_PUSH=false, skipping push.")
        return True

    remote = os.environ.get("GIT_REMOTE", "origin")
    branch = os.environ.get("GIT_BRANCH", "main")
    try:
        subprocess.run(["git", "push", remote, branch], cwd=ROOT, check=True)
        print(f"✅ Pushed to {remote}/{branch}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Push failed: {e}")
        return False


def main():
    load_env()
    today = datetime.now().strftime("%Y-%m-%d")
    message = f"publish: {today} batch"

    if len(sys.argv) > 1:
        message = sys.argv[1]

    if git_commit(message):
        git_push()


if __name__ == "__main__":
    main()
