from __future__ import annotations

from datetime import date

from media.services.providers import (
    MediaProvider,
    TitleDTO,
    SeasonsDTO,
    SeasonDTO,
    EpisodeDTO,
)
from .client import KinopoiskClient


class KinopoiskProvider(MediaProvider):
    """
    Провайдер метаданных Kinopoisk.

    Делает:
    - вызывает KinopoiskClient
    - нормализует ответы в общие DTO (providers/dtos.py)
    """

    source = "kinopoisk"

    def __init__(self, client: KinopoiskClient | None = None) -> None:
        self.client = client or KinopoiskClient()

    @staticmethod
    def _build_kp_url(kp_id: int) -> str:
        return f"https://www.kinopoisk.ru/film/{kp_id}/"

    def get_title(self, external_id: int) -> TitleDTO:
        data = self.client.fetch_film(external_id)

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
            name = f"KP#{external_id}"

        # year иногда приходит строкой; страхуемся
        try:
            year_int = int(year) if year else None
        except (TypeError, ValueError):
            year_int = None

        try:
            duration_int = int(duration_min) if duration_min else None
        except (TypeError, ValueError):
            duration_int = None

        return TitleDTO(
            external_id=int(external_id),
            name=name,
            year=year_int,
            duration_min=duration_int,
            poster_url=poster_url,
            source_url=self._build_kp_url(int(external_id)),
            is_series=is_series,
        )

    def get_seasons(self, external_id: int) -> SeasonsDTO:
        data = self.client.fetch_seasons(external_id)

        total = data.get("total")
        items = data.get("items") or []
        seasons: list[SeasonDTO] = []

        for s in items:
            season_num = s.get("number")
            if not season_num:
                continue

            try:
                season_num_int = int(season_num)
            except (TypeError, ValueError):
                continue

            episodes_raw = s.get("episodes") or []
            episodes: list[EpisodeDTO] = []

            for ep in episodes_raw:
                ep_num = ep.get("episodeNumber")
                if not ep_num:
                    continue

                try:
                    ep_num_int = int(ep_num)
                except (TypeError, ValueError):
                    continue

                # releaseDate может быть "YYYY-MM-DD"
                air_date = None
                rd = ep.get("releaseDate")
                if rd:
                    try:
                        air_date = date.fromisoformat(rd)
                    except ValueError:
                        air_date = None

                ep_name = (ep.get("nameRu") or ep.get("nameEn") or "").strip()
                dur = ep.get("duration")
                try:
                    dur_int = int(dur) if dur else None
                except (TypeError, ValueError):
                    dur_int = None

                episodes.append(
                    EpisodeDTO(
                        season_number=season_num_int,
                        episode_number=ep_num_int,
                        name=ep_name,
                        duration_min=dur_int,
                        air_date=air_date,
                    )
                )

            seasons.append(SeasonDTO(number=season_num_int, episodes=episodes))

        try:
            total_int = int(total) if total else None
        except (TypeError, ValueError):
            total_int = None

        return SeasonsDTO(total=total_int, seasons=seasons)
