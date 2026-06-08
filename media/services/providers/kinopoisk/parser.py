from datetime import date
from typing import Any

from media.dtos import EpisodeDTO, SearchResultDTO, SearchResultsDTO, SeasonDTO, SeasonsDTO, TitleDTO
from media.models import TitleCategory

_SERIES_TYPES = {"TV_SERIES", "MINI_SERIES", "TV_SHOW", "ANIME_SERIES"}


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
            original_name=data.get("nameOriginal") or "",
            description=data.get("description") or "",
            short_description=data.get("shortDescription") or "",
            slogan=data.get("slogan") or "",
            imdb_id=data.get("imdbId") or "",
            rating_kp=KinopoiskParser._parse_float(data.get("ratingKinopoisk")),
            rating_imdb=KinopoiskParser._parse_float(data.get("ratingImdb")),
            age_limit=data.get("ratingAgeLimits") or "",
            genres=KinopoiskParser._parse_names(data.get("genres"), key="genre"),
            countries=KinopoiskParser._parse_names(data.get("countries"), key="country"),
            cover_url=(data.get("coverUrl") or data.get("logoUrl") or ""),
            start_year=KinopoiskParser._parse_int(data.get("startYear")),
            end_year=KinopoiskParser._parse_int(data.get("endYear")),
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
    def parse_search(data: dict[str, Any]) -> SearchResultsDTO:
        total = KinopoiskParser._parse_int(data.get("searchFilmsCountResult")) or 0
        films = data.get("films") or []

        results: list[SearchResultDTO] = []
        for f in films:
            film_id = KinopoiskParser._parse_int(f.get("filmId"))
            if not film_id:
                continue

            name = ((f.get("nameRu") or "") or (f.get("nameEn") or "")).strip() or f"KP#{film_id}"
            api_type = (f.get("type") or "").upper()

            results.append(
                SearchResultDTO(
                    external_id=film_id,
                    name=name,
                    year=KinopoiskParser._parse_search_year(f.get("year")),
                    poster_url=(f.get("posterUrlPreview") or f.get("posterUrl") or ""),
                    is_series=api_type in _SERIES_TYPES,
                    rating=KinopoiskParser._parse_float(f.get("rating")),
                    description=f.get("description") or "",
                )
            )

        return SearchResultsDTO(total=total, results=results)

    @staticmethod
    def _parse_search_year(value: Any) -> int | None:
        # В поиске year иногда приходит диапазоном "2019-2021" — берём первый год.
        if isinstance(value, str) and "-" in value:
            value = value.split("-", 1)[0]
        return KinopoiskParser._parse_int(value)

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
    def _parse_category(data: dict[str, Any], is_series: bool) -> TitleCategory:
        genres = {str(i.get("genre", "")).lower() for i in data.get("genres", [])}
        api_type = (data.get("type") or "").upper()

        if "аниме" in genres or "anime" in genres or api_type == "ANIME":
            return TitleCategory.ANIME
        if "мультфильм" in genres or "cartoon" in genres or "animated" in genres:
            return TitleCategory.CARTOON
        if is_series:
            return TitleCategory.SERIES
        if api_type in {"FILM", "VIDEO"}:
            return TitleCategory.FILM

        return TitleCategory.OTHER

    @staticmethod
    def _parse_int(value: Any) -> int | None:
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_float(value: Any) -> float | None:
        if value in (None, ""):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_names(items: Any, *, key: str) -> list[str]:
        """Извлекает список названий из структуры вида [{genre: 'драма'}, ...]."""
        if not isinstance(items, list):
            return []
        result: list[str] = []
        for item in items:
            if isinstance(item, dict):
                value = str(item.get(key, "")).strip()
                if value:
                    result.append(value)
        return result

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
