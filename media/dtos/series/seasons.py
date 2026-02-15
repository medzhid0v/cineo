from pydantic import Field, field_validator

from media.dtos.base import BaseDTO

from .season import SeasonDTO


class SeasonsDTO(BaseDTO):
    total: int | None = None
    seasons: list[SeasonDTO] = Field(default_factory=list)

    @field_validator("total", mode="before")
    @classmethod
    def validate_total(cls, v):
        return cls.parse_int(v)

    @field_validator("seasons", mode="before")
    @classmethod
    def validate_seasons(cls, v):
        if v in (None, ""):
            return []
        if isinstance(v, list):
            return v
        return []
