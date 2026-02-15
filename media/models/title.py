from django.db import models


class TitleType(models.TextChoices):
    MOVIE = "movie", "Movie"
    SERIES = "series", "Series"


class TitleCategory(models.TextChoices):
    MOVIE = "movie", "Фильм"
    SERIES = "series", "Сериал"
    ANIME = "anime", "Аниме"
    CARTOON = "cartoon", "Мультфильм"
    OTHER = "other", "Другое"


class Title(models.Model):
    """
    Базовая сущность медиакаталога (Title).

    Представляет собой произведение — фильм или сериал.

    Важно:
        Title хранит только «контентные» данные.
        Пользовательские данные (статусы, прогресс) должны храниться в отдельных моделях.
    """

    type = models.CharField(
        max_length=16,
        choices=TitleType.choices,
        db_index=True,
        verbose_name="Тип",
    )
    category = models.CharField(
        max_length=16,
        choices=TitleCategory.choices,
        default=TitleCategory.OTHER,
        db_index=True,
        verbose_name="Категория",
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Название",
    )
    year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Год",
    )
    duration_min = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Длительность",
    )
    poster_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        verbose_name="Ссылка на постер",
    )
    kp_id = models.PositiveIntegerField(
        unique=True,
        null=True,
        blank=True,
        verbose_name="КиноПоиск ID",
    )
    kp_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        verbose_name="КиноПоиск URL",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"
        ordering = ["-year", "name"]

        indexes = [
            models.Index(fields=["type"]),
            models.Index(fields=["kp_id"]),
            models.Index(fields=["year"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.year})" if self.year else self.name
