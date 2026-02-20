from dataclasses import dataclass
from datetime import date
from typing import Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from media.models import Title, UserTitleState, WatchStatus
from media.services.user_state import ensure_user_records
from media.usecases.base_usecase import BaseUsecase


@dataclass(frozen=True)
class UpdateUserTitleStateInput:
    user_id: int
    title_id: int
    status: str
    rating: Optional[int]
    review: str
    started_at: Optional[date] = None
    finished_at: Optional[date] = None


class UpdateUserTitleStateUsecase(BaseUsecase[UpdateUserTitleStateInput, UserTitleState]):
    """
    Usecase: обновить статус/рейтинг/отзыв/даты для конкретного user + title.
    Вся логика обновления хранится тут, чтобы её можно было дергать из view и из Celery tasks.
    """

    @staticmethod
    def _apply(user_state: UserTitleState, data: UpdateUserTitleStateInput) -> None:
        user_state.status = data.status
        user_state.rating = data.rating
        user_state.review = data.review

        # started_at
        if data.started_at is not None:
            user_state.started_at = data.started_at
        elif data.status == WatchStatus.WATCHING and not user_state.started_at:
            user_state.started_at = timezone.localdate()

        # finished_at
        if data.finished_at is not None:
            user_state.finished_at = data.finished_at
        elif data.status == WatchStatus.COMPLETED and not user_state.finished_at:
            user_state.finished_at = timezone.localdate()

        user_state.save(update_fields=["status", "rating", "review", "started_at", "finished_at", "updated_at"])

    @transaction.atomic
    def execute(self, data: UpdateUserTitleStateInput) -> UserTitleState:
        # если ensure_user_records внутри делает get_or_create — user/title можно не тянуть целиком,
        # но оставлю максимально совместимо с твоим текущим кодом.
        user = get_user_model().objects.get(pk=data.user_id)
        title = Title.objects.get(pk=data.title_id)

        user_state, _ = ensure_user_records(user, title)
        self._apply(user_state, data)
        return user_state
