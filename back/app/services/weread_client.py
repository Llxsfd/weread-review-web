from typing import Any

import httpx


class WeReadError(RuntimeError):
    pass


class WeReadUpgradeRequired(WeReadError):
    pass


class WeReadApiError(WeReadError):
    pass


class WeReadClient:
    def __init__(
        self,
        *,
        api_key: str,
        skill_version: str,
        base_url: str = "https://i.weread.qq.com/api/agent/gateway",
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = api_key
        self.skill_version = skill_version
        self.base_url = base_url
        self.http_client = http_client

    async def request(self, api_name: str, **params: Any) -> dict[str, Any]:
        payload = {
            "api_name": api_name,
            "skill_version": self.skill_version,
            **params,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        if self.http_client is not None:
            response = await self.http_client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            return self._parse_response(response.json())

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            return self._parse_response(response.json())

    async def fetch_notebooks(self, *, count: int = 100, last_sort: int | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"count": count}
        if last_sort is not None:
            params["lastSort"] = last_sort
        return await self.request("/user/notebooks", **params)

    async def fetch_book_highlights(self, book_id: str) -> dict[str, Any]:
        return await self.request("/book/bookmarklist", bookId=book_id)

    async def fetch_book_info(self, book_id: str) -> dict[str, Any]:
        return await self.request("/book/info", bookId=book_id)

    async def fetch_my_reviews(self, book_id: str, *, count: int = 100, synckey: int = 0) -> dict[str, Any]:
        return await self.request("/review/list/mine", bookid=book_id, count=count, synckey=synckey)

    def _parse_response(self, payload: dict[str, Any]) -> dict[str, Any]:
        upgrade_info = payload.get("upgrade_info")
        if upgrade_info:
            message = upgrade_info.get("message") or "WeRead skill upgrade required"
            raise WeReadUpgradeRequired(message)

        errcode = payload.get("errcode")
        if errcode not in (None, 0):
            message = payload.get("errmsg") or f"WeRead API error: {errcode}"
            raise WeReadApiError(message)

        return payload
