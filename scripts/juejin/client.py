"""掘金 API 客户端（非官方逆向 API）"""

import mimetypes
import time
from dataclasses import dataclass, field
from pathlib import Path

import requests

# 请求超时（秒）
REQUEST_TIMEOUT = 30


@dataclass
class ArticleMeta:
    """文章元数据，对应掘金 publish API 的请求体"""

    title: str
    mark_content: str
    category_id: str = "6809637769959178254"  # 后端
    tag_ids: list[str] = field(default_factory=list)
    brief_content: str = ""
    cover_image: str = ""
    is_original: bool = True
    edit_type: int = 10  # Markdown
    is_english: int = 0
    column_ids: str = ""
    article_id: str = ""  # 非空表示更新


class JuejinClient:
    """掘金 API 客户端"""

    BASE_URL = "https://api.juejin.cn"

    def __init__(self, cookie: str, request_delay: float = 1.0):
        self.request_delay = request_delay
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Cookie": cookie,
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Referer": "https://juejin.cn/",
                "X-Agent": "Juejin/Web",
            }
        )

    def _post(self, path: str, body: dict) -> dict:
        """统一 POST 请求，含限流和超时"""
        time.sleep(self.request_delay)
        resp = self.session.post(f"{self.BASE_URL}{path}", json=body, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if data.get("err_no") != 0:
            raise JuejinAPIError(
                err_no=data.get("err_no"),
                err_msg=data.get("err_msg", "unknown"),
                path=path,
            )
        return data

    def verify_auth(self) -> bool:
        """验证登录状态"""
        try:
            result = self._post("/user_api/v1/user/get_info", {})
            return bool(result.get("data"))
        except (JuejinAPIError, requests.RequestException):
            return False

    def upload_image(self, image_path: str) -> str:
        """上传图片到掘金 CDN，返回 URL"""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # 检测 MIME 类型
        mime_type, _ = mimetypes.guess_type(str(path))
        if not mime_type or not mime_type.startswith("image/"):
            mime_type = "image/png"

        time.sleep(self.request_delay)
        with open(path, "rb") as f:
            files = {"file": (path.name, f, mime_type)}
            # 上传接口用 multipart，需要临时覆盖 Content-Type
            headers = {k: v for k, v in self.session.headers.items() if k != "Content-Type"}
            resp = self.session.post(
                f"{self.BASE_URL}/upload_api/v1/upload/image",
                files=files,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

        resp.raise_for_status()
        data = resp.json()
        if data.get("err_no") != 0:
            raise JuejinAPIError(
                err_no=data.get("err_no"),
                err_msg=data.get("err_msg", "upload failed"),
                path="/upload_api/v1/upload/image",
            )
        return data["data"]["url"]

    def save_draft(self, article: ArticleMeta) -> str:
        """保存草稿，返回 draft_id"""
        body = {
            "article_id": article.article_id,
            "category_id": article.category_id,
            "tag_ids": article.tag_ids,
            "title": article.title,
            "mark_content": article.mark_content,
            "html_content": "san_markdown",
            "cover_image": article.cover_image,
            "brief_content": article.brief_content,
            "link_url": "",
            "edit_type": article.edit_type,
            "is_english": article.is_english,
            "is_original": 1 if article.is_original else 0,
            "import_tag": 0,
            "auto_saver": 1,
            "sync_to_org": False,
            "column_ids": article.column_ids,
            "theme_ids": "",
            "pics": [],
        }
        result = self._post("/content_api/v1/article_draft/save_draft", body)
        return result["data"]["draft_id"]

    def publish(self, article: ArticleMeta, draft_id: str = "") -> str:
        """发布文章，返回 article_id"""
        body = {
            "article_id": article.article_id,
            "draft_id": draft_id,
            "category_id": article.category_id,
            "tag_ids": article.tag_ids,
            "title": article.title,
            "mark_content": article.mark_content,
            "html_content": "san_markdown",
            "cover_image": article.cover_image,
            "brief_content": article.brief_content,
            "link_url": "",
            "edit_type": article.edit_type,
            "is_english": article.is_english,
            "is_original": 1 if article.is_original else 0,
            "import_tag": 0,
            "auto_saver": 1,
            "sync_to_org": False,
            "column_ids": article.column_ids,
            "theme_ids": "",
            "pics": [],
        }
        result = self._post("/content_api/v1/article/publish", body)
        return result["data"].get("article_id", "")

    def update(self, article_id: str, article: ArticleMeta) -> bool:
        """更新已发布的文章（不修改传入的 article 对象）"""
        body = {
            "article_id": article_id,
            "category_id": article.category_id,
            "tag_ids": article.tag_ids,
            "title": article.title,
            "mark_content": article.mark_content,
            "html_content": "san_markdown",
            "cover_image": article.cover_image,
            "brief_content": article.brief_content,
            "link_url": "",
            "edit_type": article.edit_type,
            "is_english": article.is_english,
            "is_original": 1 if article.is_original else 0,
            "import_tag": 0,
            "auto_saver": 1,
            "sync_to_org": False,
            "column_ids": article.column_ids,
            "theme_ids": "",
            "pics": [],
        }
        self._post("/content_api/v1/article/update", body)
        return True

    def list_tags(self, keyword: str, category_id: str = "") -> list[dict]:
        """搜索标签"""
        body = {"key_word": keyword, "limit": 20}
        if category_id:
            body["category_id"] = category_id
        result = self._post("/tag_api/v1/query_tag_list", body)
        return result.get("data", [])

    def list_categories(self) -> list[dict]:
        """获取所有分类"""
        result = self._post("/tag_api/v1/query_category_briefs", {})
        return result.get("data", [])


class JuejinAPIError(Exception):
    """掘金 API 错误"""

    def __init__(self, err_no: int, err_msg: str, path: str = ""):
        self.err_no = err_no
        self.err_msg = err_msg
        self.path = path
        super().__init__(f"Juejin API error {err_no}: {err_msg} (path={path})")
