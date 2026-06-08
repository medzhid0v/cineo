from pydantic import Field, field_validator

from .base import BaseDTO


class SearchResultDTO(BaseDTO):
    """Один элемент результата поиска по названию."""

    external_id: int
    name: str
    year: int | None = None
    poster_url: str = ""
    is_series: bool = False
    rating: float | None = None
    description: str = ""

    @field_validator("year", mode="before")
    @classmethod
    def validate_ints(cls, v):
        return cls.parse_int(v)

    @field_validator("name", "poster_url", "description", mode="before")
    @classmethod
    def validate_strings(cls, v):
        return cls.parse_str(v)


class SearchResultsDTO(BaseDTO):
    total: int = 0
    results: list[SearchResultDTO] = Field(default_factory=list)
