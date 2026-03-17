# mypy: ignore-errors
"""HTTP client for AgentGIF API."""

from pathlib import Path
from typing import Any

import httpx

from agentgif.config import get_api_key, get_base_url


class AgentGIFError(Exception):
    """API error with status code and message."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP {status_code}: {message}")


class Client:
    """AgentGIF API client."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key or get_api_key()
        self.base_url = (base_url or get_base_url()).rstrip("/")
        self._http = httpx.Client(
            base_url=f"{self.base_url}/api/v1",
            timeout=60.0,
        )

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.api_key:
            headers["Authorization"] = f"Token {self.api_key}"
        return headers

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        response = self._http.request(method, path, headers=self._headers(), **kwargs)
        if response.status_code >= 400:
            try:
                msg = response.json().get("detail", response.text)
            except Exception:
                msg = response.text
            raise AgentGIFError(response.status_code, msg)
        return response.json()

    def upload(
        self,
        gif_path: Path,
        *,
        title: str = "",
        description: str = "",
        command: str = "",
        tags: str = "",
        cast_path: Path | None = None,
        theme: str = "",
        visibility: str = "public",
        repo_slug: str = "",
    ) -> dict[str, Any]:
        """Upload a GIF (and optional cast) to AgentGIF."""
        files: dict[str, Any] = {"gif": (gif_path.name, gif_path.open("rb"), "image/gif")}
        if cast_path:
            files["cast"] = (cast_path.name, cast_path.open("rb"), "application/octet-stream")
        data: dict[str, str] = {}
        if title:
            data["title"] = title
        if description:
            data["description"] = description
        if command:
            data["command"] = command
        if tags:
            data["tags"] = tags
        if theme:
            data["theme"] = theme
        if visibility != "public":
            data["visibility"] = visibility
        if repo_slug:
            data["repo_slug"] = repo_slug
        result: dict[str, Any] = self._request("POST", "/gifs/", files=files, data=data)
        return result

    def search(self, query: str, **params: Any) -> dict[str, Any]:
        params["q"] = query
        result: dict[str, Any] = self._request("GET", "/search/", params=params)
        return result

    def get_gif(self, gif_id: str) -> dict[str, Any]:
        result: dict[str, Any] = self._request("GET", f"/gifs/{gif_id}/")
        return result

    def list_gifs(self, **params: Any) -> dict[str, Any]:
        result: dict[str, Any] = self._request("GET", "/gifs/me/", params=params)
        return result

    def delete_gif(self, gif_id: str) -> None:
        self._request("DELETE", f"/gifs/{gif_id}/")

    def update_gif(self, gif_id: str, **fields: str) -> dict[str, Any]:
        """Update a GIF's metadata (PATCH)."""
        result: dict[str, Any] = self._request("PATCH", f"/gifs/{gif_id}/", json=fields)
        return result

    def embed_codes(self, gif_id: str) -> dict[str, str]:
        data = self.get_gif(gif_id)
        codes: dict[str, str] = data.get("embed", {})
        return codes

    def whoami(self) -> dict[str, Any]:
        result: dict[str, Any] = self._request("GET", "/users/me/")
        return result

    def badge_url(
        self,
        provider: str,
        package: str,
        *,
        metric: str = "version",
        theme: str = "",
        style: str = "",
    ) -> dict[str, Any]:
        """GET /api/v1/badge-url/ — generate badge URL + embed codes."""
        params: dict[str, str] = {"provider": provider, "package": package, "metric": metric}
        if theme:
            params["theme"] = theme
        if style and style != "default":
            params["style"] = style
        result: dict[str, Any] = self._request("GET", "/badge-url/", params=params)
        return result

    def badge_themes(self) -> dict[str, Any]:
        """GET /api/v1/themes/badges/ — list badge themes."""
        result: dict[str, Any] = self._request("GET", "/themes/badges/")
        return result

    def generate_tape(
        self,
        *,
        source_url: str = "",
        source_type: str = "",
        package_name: str = "",
        max_gifs: int = 5,
        raw_markdown: str = "",
        tape_only: bool = False,
        theme: str = "",
    ) -> dict[str, Any]:
        """POST /api/v1/gifs/generate/ — create a tape generation job."""
        payload: dict[str, Any] = {"max_gifs": max_gifs}
        if source_url:
            payload["source_url"] = source_url
        if source_type:
            payload["source_type"] = source_type
        if package_name:
            payload["package_name"] = package_name
        if raw_markdown:
            payload["source_type"] = "raw"
            payload["raw_markdown"] = raw_markdown
        if tape_only:
            payload["tape_only"] = True
        if theme:
            payload["theme"] = theme
        result: dict[str, Any] = self._request("POST", "/gifs/generate/", json=payload)
        return result

    def generate_status(self, job_id: str) -> dict[str, Any]:
        """GET /api/v1/gifs/generate/<job_id>/ — poll job status."""
        result: dict[str, Any] = self._request("GET", f"/gifs/generate/{job_id}/")
        return result

    def cli_version(self) -> dict[str, Any]:
        """GET /api/v1/cli/version/ — check for CLI updates."""
        result: dict[str, Any] = self._request("GET", "/cli/version/")
        return result
