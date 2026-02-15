from django.db import models


class Season(models.Model):
    """
    Сезон сериала.

    Связан с Title (где type=series) и определяет порядковый номер сезона.
    Может хранить общее количество эпизодов, если детальная информация
    по сериям не заведена.
    """

    title = models.ForeignKey(
        "media.Title",
        on_delete=models.CASCADE,
        related_name="seasons",
        verbose_name="Произведение",
    )
    number = models.PositiveSmallIntegerField(
        verbose_name="Номер сезона",
    )
    episodes_count = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Количество серий",
    )

    class Meta:
        verbose_name = "Сезон"
        verbose_name_plural = "Сезоны"
        ordering = ["number"]

        constraints = [
            models.UniqueConstraint(
                fields=["title", "number"],
                name="uq_title_season_number",
            ),
        ]
        indexes = [
            models.Index(fields=["title", "number"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} — Сезон {self.number}"
