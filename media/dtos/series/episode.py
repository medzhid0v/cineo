from datetime import date

from pydantic import field_validator

from media.dtos.base import BaseDTO


class EpisodeDTO(BaseDTO):
    season_number: int
    episode_number: int
    name: str = ""
    duration_min: int | None = None
    air_date: date | None = None

    @field_validator("duration_min", mode="before")
    @classmethod
    def validate_ints(cls, v):
        return cls.parse_int(v)

    @field_validator("name")
    @classmethod
    def validate_strings(cls, v):
        return cls.parse_str(v)
