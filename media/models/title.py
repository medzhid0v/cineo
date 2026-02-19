from django.db import models


class TitleCategory(models.TextChoices):
    FILM = "film", "Фильм"
    SERIES = "series", "Сериал"
    ANIME = "anime", "Аниме"
    CARTOON = "cartoon", "Мультфильм"
    OTHER = "other", "Другое"


class Title(models.Model):
    """
    Базовая сущность медиакаталога (Title).

    Представляет собой произведение — фильм, сериал и др.

    Важно:
        Title хранит только «контентные» данные.
        Пользовательские данные (статусы, прогресс) должны храниться в отдельных моделях.
    """

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
    is_series = models.BooleanField(
        default=False,
        verbose_name="Сериал (есть сезоны/серии)",
        help_text="Истина для сериалов и аниме-сериалов — подтягиваются сезоны и серии.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["kp_id"]),
            models.Index(fields=["year"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.year})" if self.year else self.name
