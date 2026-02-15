from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True)
class FilmDTO:
    """Нормализованные данные о фильме/сериале из Kinopoisk API."""

    kp_id: int
    name: str
    year: int | None
    duration_min: int | None
    poster_url: str
    kp_url: str
    is_series: bool


@dataclass(frozen=True)
class EpisodeDTO:
    season_number: int
    episode_number: int
    name: str
    duration_min: int | None
    air_date: date | None


@dataclass(frozen=True)
class SeasonDTO:
    number: int
    episodes: list[EpisodeDTO]


@dataclass(frozen=True)
class SeasonsDTO:
    total: int | None
    seasons: list[SeasonDTO]


# Если захочешь хранить "сырой" ответ для дебага
@dataclass(frozen=True)
class RawResponseDTO:
    data: dict[str, Any]
