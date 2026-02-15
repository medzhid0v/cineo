from pydantic import Field, field_validator

from media.dtos.base import BaseDTO

from .episode import EpisodeDTO


class SeasonDTO(BaseDTO):
    number: int
    episodes: list[EpisodeDTO] = Field(default_factory=list)

    @field_validator("number", mode="before")
    @classmethod
    def validate_number(cls, v):
        parsed = cls.parse_int(v)
        if parsed is None:
            raise ValueError("Season number is required")
        return parsed

    @field_validator("episodes", mode="before")
    @classmethod
    def validate_episodes(cls, v):
        return cls.parse_list(v)
