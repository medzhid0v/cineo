import os
from datetime import date
from typing import Any

import httpx

from .dtos import FilmDTO, SeasonsDTO, SeasonDTO, EpisodeDTO
from .errors import KinopoiskAuthError, KinopoiskHTTPError, KinopoiskParseError


class KinopoiskClient:
    """
    Клиент для kinopoiskapiunofficial.tech.

    Авторизация: заголовок X-API-KEY.
    """

    BASE_URL = "https://kinopoiskapiunofficial.tech/api"

    def __init__(self, api_key: str | None = None, timeout: float = 15.0) -> None:
        self.api_key = api_key or os.environ.get("KINOPOISK_API_KEY")
        if not self.api_key:
            raise KinopoiskAuthError("KINOPOISK_API_KEY is not set")
        self.timeout = timeout

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.BASE_URL}{path}"
        headers = {"X-API-KEY": self.api_key, "accept": "application/json"}

        try:
            with httpx.Client(timeout=self.timeout, headers=headers) as client:
                r = client.get(url, params=params)
        except httpx.RequestError as e:
            raise KinopoiskHTTPError(f"Request error: {e}") from e

        if r.status_code == 401 or r.status_code == 403:
            raise KinopoiskAuthError(f"Auth error {r.status_code}: {r.text}")
        if r.status_code >= 400:
            raise KinopoiskHTTPError(f"HTTP error {r.status_code}: {r.text}")

        try:
            return r.json()
        except Exception as e:
            raise KinopoiskParseError(f"Invalid JSON: {e}") from e

    @staticmethod
    def _build_kp_url(kp_id: int) -> str:
        return f"https://www.kinopoisk.ru/film/{kp_id}/"

    def get_film(self, kp_id: int) -> FilmDTO:
        data = self._get(f"/v2.2/films/{kp_id}")

        name = (
            (data.get("nameRu") or "")
            or (data.get("nameEn") or "")
            or (data.get("nameOriginal") or "")
        ).strip()

        year = data.get("year")
        duration_min = data.get("filmLength")
        poster_url = (
            data.get("posterUrl") or data.get("posterUrlPreview") or ""
        ).strip()

        api_type = (data.get("type") or "").upper()
        is_series = bool(data.get("serial")) or api_type in {
            "TV_SERIES",
            "MINI_SERIES",
            "TV_SHOW",
        }

        if not name:
            name = f"KP#{kp_id}"

        return FilmDTO(
            kp_id=kp_id,
            name=name,
            year=int(year) if year else None,
            duration_min=int(duration_min) if duration_min else None,
            poster_url=poster_url,
            kp_url=self._build_kp_url(kp_id),
            is_series=is_series,
        )

    def get_seasons(self, kp_id: int) -> SeasonsDTO:
        data = self._get(f"/v2.2/films/{kp_id}/seasons")

        total = data.get("total")
        items = data.get("items") or []
        seasons: list[SeasonDTO] = []

        for s in items:
            season_num = s.get("number")
            if not season_num:
                continue

            episodes_raw = s.get("episodes") or []
            episodes: list[EpisodeDTO] = []

            for ep in episodes_raw:
                ep_num = ep.get("episodeNumber")
                if not ep_num:
                    continue

                air_date = None
                rd = ep.get("releaseDate")
                if rd:
                    try:
                        air_date = date.fromisoformat(rd)
                    except ValueError:
                        air_date = None

                ep_name = (ep.get("nameRu") or ep.get("nameEn") or "").strip()

                episodes.append(
                    EpisodeDTO(
                        season_number=int(season_num),
                        episode_number=int(ep_num),
                        name=ep_name,
                        duration_min=ep.get("duration"),
                        air_date=air_date,
                    )
                )

            seasons.append(SeasonDTO(number=int(season_num), episodes=episodes))

        return SeasonsDTO(
            total=int(total) if total else None,
            seasons=seasons,
        )
