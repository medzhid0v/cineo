from django.db import models


class Episode(models.Model):
    """
    Эпизод (серия) сезона.

    Принадлежит конкретному Season и хранит порядковый номер,
    название серии, длительность и дату выхода.
    """

    season = models.ForeignKey(
        "media.Season",
        on_delete=models.CASCADE,
        related_name="episodes",
        verbose_name="Сезон",
    )
    number = models.PositiveSmallIntegerField(
        verbose_name="Номер серии",
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Название серии",
    )
    duration_min = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Длительность (мин)",
    )
    air_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата выхода",
    )

    class Meta:
        verbose_name = "Серия"
        verbose_name_plural = "Серии"
        ordering = ["number"]

        constraints = [
            models.UniqueConstraint(
                fields=["season", "number"],
                name="uq_season_episode_number",
            ),
        ]
        indexes = [
            models.Index(fields=["season", "number"]),
        ]

    def __str__(self) -> str:
        base = f"S{self.season.number:02d}E{self.number:02d}"
        return f"{base} {self.name}".strip()
