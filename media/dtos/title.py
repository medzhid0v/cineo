from pydantic import Field, field_validator

from .base import BaseDTO


class TitleDTO(BaseDTO):
    external_id: int
    name: str
    year: int | None = None
    duration_min: int | None = None
    poster_url: str = ""
    source_url: str
    is_series: bool
    category: str = "other"

    # Расширенные метаданные
    original_name: str = ""
    description: str = ""
    short_description: str = ""
    slogan: str = ""
    imdb_id: str = ""
    rating_kp: float | None = None
    rating_imdb: float | None = None
    age_limit: str = ""
    genres: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)
    cover_url: str = ""
    start_year: int | None = None
    end_year: int | None = None

    @field_validator("year", "duration_min", "start_year", "end_year", mode="before")
    @classmethod
    def validate_ints(cls, v):
        return cls.parse_int(v)

    @field_validator(
        "name",
        "poster_url",
        "original_name",
        "description",
        "short_description",
        "slogan",
        "imdb_id",
        "age_limit",
        "cover_url",
        mode="before",
    )
    @classmethod
    def validate_strings(cls, v):
        return cls.parse_str(v)

    @field_validator("genres", "countries", mode="before")
    @classmethod
    def validate_lists(cls, v):
        return cls.parse_list(v)
