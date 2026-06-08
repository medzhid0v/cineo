from django.db import models


class PayloadKind(models.TextChoices):
    """Тип закэшированного ответа провайдера (соответствует эндпоинту API)."""

    FILM = "film", "Фильм"
    SEASONS = "seasons", "Сезоны"
    SEARCH = "search", "Поиск"


class ProviderPayload(models.Model):
    """
    Кэш «сырых» ответов внешнего провайдера метаданных.

    Хранит неизменённый JSON ответа API, привязанный к
    (provider, external_id, kind). Позволяет:

    - не повторять запрос к API при повторном добавлении тайтла
      (в т.ч. другим пользователем) после удаления из UI;
    - переразбирать данные новой версией парсера без обращения к сети.

    Для поисковых ответов (kind=search) external_id не применим —
    ключом служит query (хэшируется в external_id вызывающим кодом
    либо используется отдельная запись с external_id=0 и lookup-полем).
    """

    provider = models.CharField(
        max_length=32,
        db_index=True,
        verbose_name="Провайдер",
    )
    external_id = models.PositiveIntegerField(
        verbose_name="Внешний ID",
    )
    kind = models.CharField(
        max_length=16,
        choices=PayloadKind.choices,
        verbose_name="Тип ответа",
    )
    query = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Поисковый запрос",
        help_text="Заполняется только для kind=search.",
    )
    payload = models.JSONField(
        verbose_name="Сырой ответ (JSON)",
    )

    fetched_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Когда получено",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Когда создано",
    )

    class Meta:
        verbose_name = "Ответ провайдера"
        verbose_name_plural = "Ответы провайдеров (кэш)"
        ordering = ["-fetched_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "external_id", "kind"],
                name="uq_provider_payload",
            ),
        ]
        indexes = [
            models.Index(fields=["provider", "kind"]),
            models.Index(fields=["provider", "query"]),
        ]

    def __str__(self) -> str:
        return f"{self.provider}:{self.kind}#{self.external_id}"
