# scripts/ — CLAUDE.md

Publishing and automation scripts for the self-media project.

## Script Responsibilities

| Script | Purpose |
|--------|---------|
| `publish.py` | Unified publishing entry point. Dispatches to platform-specific modules (juejin, wechat, git). Handles category resolution, .env loading, publish logging, and moving articles from drafts/ to published/. |
| `scheduler.py` | Scheduled publishing daemon. Scans `content/drafts/*/meta.yml` for `schedule.publish_at` fields, and invokes `publish.py` when the scheduled time arrives. Supports `--once` flag for single-run mode. |
| `git_sync.py` | Auto-commits published content to git. Runs `git add content/published/` + `git commit`. Respects `GIT_AUTO_PUSH` env var for auto-push. |
| `migrate_from_blog.py` | One-time migration tool. Converts articles from the legacy blog project into self-media format, parsing YAML frontmatter and creating the standard directory structure under `content/archive/`. |

## juejin/ Package

The `juejin/` package implements the Juejin (juejin.cn) publishing API:

- **`client.py`** — `JuejinClient` class wrapping the unofficial reverse-engineered API
  - `JuejinClient(cookie, request_delay=1.0)` — constructor with session setup
  - `ArticleMeta` dataclass — article payload (title, mark_content, category_id, tag_ids, etc.)
  - Methods: create/update drafts, publish articles, upload images
  - Built-in rate limiting via `request_delay`
  - Base URL: `https://api.juejin.cn`
- **`__init__.py`** — Package marker

Usage pattern:
```python
from juejin.client import JuejinClient, ArticleMeta

client = JuejinClient(cookie=os.environ["JUEJIN_COOKIE"])
meta = ArticleMeta(title="...", mark_content="...", category_id="...")
client.publish(meta)
```

## wechat/ Package

Currently a **placeholder** — the directory exists but contains no implementation yet. WeChat Official Account publishing will be added in a future iteration. The platform config and meta.yml schema already include wechat fields in preparation.

## How to Add a New Platform Publisher

1. Create a new package directory: `scripts/<platform_name>/`
2. Add `__init__.py` and `client.py` with a client class following the juejin pattern
3. Implement at minimum: `create_draft()`, `publish()`, `upload_image()`
4. Add platform config to `config/platforms.yml`
5. Add platform fields to `content/_templates/meta.yml` under `platforms.<name>`
6. Register the platform in `publish.py`'s dispatch logic
7. Add env vars to `.env.example`

## Environment Variable Dependencies

All variables are loaded from `.env` (see `.env.example`):

| Variable | Used By | Purpose |
|----------|---------|---------|
| `JUEJIN_COOKIE` | juejin/ client | Juejin login cookie (must be refreshed periodically) |
| `WECHAT_APP_ID` | wechat/ client | WeChat Official Account API app ID |
| `WECHAT_APP_SECRET` | wechat/ client | WeChat Official Account API secret |
| `OPENAI_API_KEY` | Image generation | Used by baoyu-imagine skill for AI images |
| `GIT_AUTO_PUSH` | git_sync.py | Set to "true" to auto-push after commit |
| `JUEJIN_DEFAULT_CATEGORY` | publish.py | Fallback category ID if not in meta.yml |

## Common Commands

```bash
# Publish to all platforms
python scripts/publish.py --slug <article-slug>

# Publish to specific platform
python scripts/publish.py --slug <article-slug> --platform juejin

# Check publish status
python scripts/publish.py --slug <article-slug> --status

# Run scheduler once (development)
python scripts/scheduler.py --once

# Install launchd scheduled task (macOS)
launchctl load scheduler/com.self-media.publish.plist

# Migrate legacy blog articles
python scripts/migrate_from_blog.py /path/to/blog/articles/
```
