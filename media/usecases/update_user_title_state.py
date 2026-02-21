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
    started_at_provided: bool = False
    finished_at_provided: bool = False


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

        # Сохраняем текущие значения из БД перед возможными изменениями
        current_started_at = user_state.started_at
        current_finished_at = user_state.finished_at

        # started_at: обновляем только если поле было явно передано в форме И значение изменилось
        # Если поле не было в POST - оставляем текущее значение из БД
        if data.started_at_provided:
            # Поле было изменено пользователем - используем значение из формы (может быть None для очистки)
            user_state.started_at = data.started_at
        else:
            # Поле не было изменено - оставляем текущее значение из БД
            # Применяем автоматическую логику только если статус WATCHING и дата еще не установлена
            if data.status == WatchStatus.WATCHING and not current_started_at:
                user_state.started_at = timezone.localdate()
            else:
                user_state.started_at = current_started_at

        # finished_at: аналогично для finished_at
        if data.finished_at_provided:
            user_state.finished_at = data.finished_at
        else:
            if data.status == WatchStatus.COMPLETED and not current_finished_at:
                user_state.finished_at = timezone.localdate()
            else:
                user_state.finished_at = current_finished_at

        user_state.save(update_fields=["status", "rating", "review", "started_at", "finished_at", "updated_at"])
        # Обновляем объект из БД, чтобы убедиться, что все значения синхронизированы
        user_state.refresh_from_db()

    @transaction.atomic
    def execute(self, data: UpdateUserTitleStateInput) -> UserTitleState:
        # если ensure_user_records внутри делает get_or_create — user/title можно не тянуть целиком,
        # но оставлю максимально совместимо с твоим текущим кодом.
        user = get_user_model().objects.get(pk=data.user_id)
        title = Title.objects.get(pk=data.title_id)

        user_state, _ = ensure_user_records(user_id=user.id, title_id=title.id)
        self._apply(user_state, data)
        return user_state
