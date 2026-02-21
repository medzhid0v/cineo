from typing import Any

import httpx

from .errors import KinopoiskAuthError, KinopoiskHTTPError, KinopoiskParseError


class KinopoiskClient:
    """
    Низкоуровневый HTTP-клиент для kinopoiskapiunofficial.tech.

    Возвращает "сырые" ответы (dict), без нормализации под доменные DTO.
    """

    BASE_URL = "https://kinopoiskapiunofficial.tech/api"

    def __init__(self, api_key: str, timeout: float = 15.0) -> None:
        if not api_key:
            raise KinopoiskAuthError("API_KEY is not set")

        self.api_key = api_key
        self.timeout = timeout

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.BASE_URL}{path}"
        headers = {"X-API-KEY": self.api_key, "accept": "application/json"}

        try:
            with httpx.Client(timeout=self.timeout, headers=headers) as client:
                r = client.get(url, params=params)
        except httpx.RequestError as e:
            raise KinopoiskHTTPError(f"Request error: {e}") from e

        if r.status_code in (401, 403):
            raise KinopoiskAuthError(f"Auth error {r.status_code}: {r.text}")
        if r.status_code >= 400:
            raise KinopoiskHTTPError(f"HTTP error {r.status_code}: {r.text}")

        try:
            return r.json()
        except Exception as e:
            raise KinopoiskParseError(f"Invalid JSON: {e}") from e

    def fetch_film(self, kp_id: int) -> dict[str, Any]:
        return self._get(f"/v2.2/films/{kp_id}")

    def fetch_seasons(self, kp_id: int) -> dict[str, Any]:
        return self._get(f"/v2.2/films/{kp_id}/seasons")
