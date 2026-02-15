from datetime import date
from typing import Any

from media.dtos import EpisodeDTO, SeasonDTO, SeasonsDTO, TitleDTO


class KinopoiskParser:
    """
    Отвечает только за преобразование сырого JSON
    от Kinopoisk API в доменные DTO.
    """

    @staticmethod
    def parse_title(data: dict[str, Any], external_id: int) -> TitleDTO:
        name = KinopoiskParser._parse_name(data, external_id)
        year = KinopoiskParser._parse_int(data.get("year"))
        duration = KinopoiskParser._parse_int(data.get("filmLength"))
        poster = KinopoiskParser._parse_poster(data)
        is_series = KinopoiskParser._parse_is_series(data)

        return TitleDTO(
            external_id=int(external_id),
            name=name,
            year=year,
            duration_min=duration,
            poster_url=poster,
            source_url=KinopoiskParser._build_kp_url(external_id),
            is_series=is_series,
            category=KinopoiskParser._parse_category(data, is_series),
        )

    @staticmethod
    def parse_seasons(data: dict[str, Any]) -> SeasonsDTO:
        total = KinopoiskParser._parse_int(data.get("total"))
        items = data.get("items") or []

        seasons: list[SeasonDTO] = []

        for s in items:
            season_number = KinopoiskParser._parse_int(s.get("number"))
            if not season_number:
                continue

            episodes_raw = s.get("episodes") or []
            episodes: list[EpisodeDTO] = []

            for ep in episodes_raw:
                episode_number = KinopoiskParser._parse_int(ep.get("episodeNumber"))
                if not episode_number:
                    continue

                episodes.append(
                    EpisodeDTO(
                        season_number=season_number,
                        episode_number=episode_number,
                        name=KinopoiskParser._parse_episode_name(ep),
                        duration_min=KinopoiskParser._parse_int(ep.get("duration")),
                        air_date=KinopoiskParser._parse_date(ep.get("releaseDate")),
                    )
                )

            seasons.append(SeasonDTO(number=season_number, episodes=episodes))

        return SeasonsDTO(total=total, seasons=seasons)

    @staticmethod
    def _parse_name(data: dict[str, Any], external_id: int) -> str:
        name = ((data.get("nameRu") or "") or (data.get("nameEn") or "") or (data.get("nameOriginal") or "")).strip()
        return name or f"KP#{external_id}"

    @staticmethod
    def _parse_episode_name(data: dict[str, Any]) -> str:
        return (data.get("nameRu") or data.get("nameEn") or "").strip()

    @staticmethod
    def _parse_poster(data: dict[str, Any]) -> str:
        return (data.get("posterUrl") or data.get("posterUrlPreview") or "").strip()

    @staticmethod
    def _parse_is_series(data: dict[str, Any]) -> bool:
        api_type = (data.get("type") or "").upper()
        return bool(data.get("serial")) or api_type in {
            "TV_SERIES",
            "MINI_SERIES",
            "TV_SHOW",
            "ANIME_SERIES",
        }

    @staticmethod
    def _parse_category(data: dict[str, Any], is_series: bool) -> str:
        genres = {str(i.get("genre", "")).lower() for i in data.get("genres", [])}
        api_type = (data.get("type") or "").upper()

        if "аниме" in genres or "anime" in genres or "ANIME" in api_type:
            return "anime"
        if "мультфильм" in genres or "cartoon" in genres or "animated" in genres:
            return "cartoon"
        if is_series:
            return "series"
        if api_type in {"FILM", "VIDEO"}:
            return "movie"
        return "other"

    @staticmethod
    def _parse_int(value: Any) -> int | None:
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_date(value: Any) -> date | None:
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _build_kp_url(external_id: int) -> str:
        return f"https://www.kinopoisk.ru/film/{external_id}/"
