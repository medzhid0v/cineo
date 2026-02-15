from pydantic import field_validator

from .base import BaseDTO


class TitleDTO(BaseDTO):
    external_id: int
    name: str
    year: int | None = None
    duration_min: int | None = None
    poster_url: str = ""
    source_url: str
    is_series: bool

    @field_validator("year", "duration_min", mode="before")
    @classmethod
    def validate_ints(cls, v):
        return cls.parse_int(v)

    @field_validator("name", "poster_url", mode="before")
    @classmethod
    def validate_strings(cls, v):
        return cls.parse_str(v)
