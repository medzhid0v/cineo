from django.db import models


class TitleType(models.TextChoices):
    MOVIE = "movie", "Movie"
    SERIES = "series", "Series"


class Title(models.Model):
    type = models.CharField(max_length=16, choices=TitleType.choices, db_index=True, verbose_name="Тип",)

    name = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField(null=True, blank=True)

    # Для фильмов — длительность фильма, для сериалов — можно хранить среднюю/типовую
    duration_min = models.PositiveSmallIntegerField(null=True, blank=True)

    poster_url = models.URLField(max_length=500, blank=True, default="")

    kp_id = models.PositiveIntegerField(unique=True, null=True, blank=True)
    kp_url = models.URLField(max_length=500, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["type"]),
            models.Index(fields=["kp_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.year})" if self.year else self.name
