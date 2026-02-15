from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class WatchStatus(models.TextChoices):
    PLANNED = "planned", "Запланировано"
    WATCHING = "watching", "Смотрю"
    COMPLETED = "completed", "Просмотрено"
    DROPPED = "dropped", "Заброшено"
    ON_HOLD = "on_hold", "На паузе"


class UserTitleState(models.Model):
    """
    Пользовательское состояние произведения.

    Хранит:
    - статус просмотра,
    - пользовательский рейтинг,
    - текстовый отзыв,
    - даты начала и завершения просмотра.

    Одна запись на пользователя и произведение.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    title = models.ForeignKey(
        "media.Title",
        on_delete=models.CASCADE,
        related_name="user_states",
        verbose_name="Произведение",
    )

    status = models.CharField(
        max_length=16,
        choices=WatchStatus.choices,
        default=WatchStatus.PLANNED,
        verbose_name="Статус",
    )
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Оценка",
    )
    review = models.TextField(
        blank=True,
        default="",
        verbose_name="Отзыв",
    )

    started_at = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата начала просмотра",
    )
    finished_at = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата завершения",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Состояние просмотра"
        verbose_name_plural = "Состояния просмотра"
        ordering = ["-updated_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "title"],
                name="uq_user_title_state",
            ),
            models.CheckConstraint(
                condition=models.Q(rating__isnull=True) | models.Q(rating__gte=0, rating__lte=10),
                name="ck_user_title_state_rating_0_10",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} — {self.title} [{self.get_status_display()}]"


class UserProgress(models.Model):
    """
    Прогресс просмотра пользователя.

    Для фильмов:
        - position_seconds

    Для сериалов:
        - текущий сезон и серия,
        - позиция внутри серии.

    Одна запись на пользователя и произведение.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    title = models.ForeignKey(
        "media.Title",
        on_delete=models.CASCADE,
        related_name="user_progress",
        verbose_name="Произведение",
    )

    # Для фильмов
    position_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Позиция (сек)",
    )

    # Для сериалов
    current_season_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Текущий сезон",
    )
    current_episode_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Текущая серия",
    )
    current_episode_position_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Позиция в серии (сек)",
    )

    last_watched_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Последний просмотр",
    )

    class Meta:
        verbose_name = "Прогресс просмотра"
        verbose_name_plural = "Прогресс просмотра"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "title"],
                name="uq_user_title_progress",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} — {self.title} (прогресс)"


class UserEpisodeState(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    episode = models.ForeignKey(
        "media.Episode",
        on_delete=models.CASCADE,
        related_name="user_states",
        verbose_name="Эпизод",
    )
    watched = models.BooleanField(default=False, verbose_name="Просмотрено")
    watched_at = models.DateTimeField(null=True, blank=True, verbose_name="Когда просмотрено")

    class Meta:
        verbose_name = "Состояние эпизода"
        verbose_name_plural = "Состояния эпизодов"
        constraints = [
            models.UniqueConstraint(fields=["user", "episode"], name="uq_user_episode_state"),
        ]
        indexes = [models.Index(fields=["user", "watched"])]

    def __str__(self) -> str:
        return f"{self.user} — {self.episode}"
