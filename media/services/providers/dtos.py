from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class TitleDTO:
    external_id: int
    name: str
    year: int | None
    duration_min: int | None
    poster_url: str
    source_url: str
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
