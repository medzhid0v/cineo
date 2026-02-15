from django.db import models


class Franchise(models.Model):
    """
    Франшиза — объединение нескольких произведений (Title)
    в логическую серию (например, трилогия или киновселенная).

    Используется для навигации между частями и определения
    порядка просмотра.
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Название франшизы",
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Описание",
    )

    class Meta:
        verbose_name = "Франшиза"
        verbose_name_plural = "Франшизы"

    def __str__(self) -> str:
        return self.name


class FranchiseItem(models.Model):
    """
    Элемент франшизы — связывает конкретный Title
    с франшизой и определяет его порядковый номер.

    Позволяет:
    - задавать порядок частей,
    - хранить примечания к конкретной части,
    - быстро получать соседние части (предыдущую/следующую).
    """

    franchise = models.ForeignKey(
        Franchise,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Франшиза",
    )
    title = models.ForeignKey(
        "media.Title",
        on_delete=models.CASCADE,
        related_name="franchise_items",
        verbose_name="Произведение",
    )
    order = models.PositiveSmallIntegerField(
        verbose_name="Порядковый номер",
    )
    note = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Примечание",
    )

    class Meta:
        verbose_name = "Элемент франшизы"
        verbose_name_plural = "Элементы франшизы"
        constraints = [
            models.UniqueConstraint(
                fields=["franchise", "title"],
                name="uq_franchise_title",
            ),
            models.UniqueConstraint(
                fields=["franchise", "order"],
                name="uq_franchise_order",
            ),
        ]
        indexes = [
            models.Index(fields=["franchise", "order"]),
        ]

    def __str__(self) -> str:
        return f"{self.franchise}: #{self.order} {self.title}"
