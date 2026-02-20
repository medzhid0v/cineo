import logging

from celery import shared_task

from media.usecases.receive_title import ReceiveTitle, ReceiveTitleUsecase

logger = logging.getLogger(__name__)


@shared_task
def receive_title_task(*, source_id: int, user_id: int) -> None:
    """Импортирует тайтл из Кинопоиска по kp_id и привязывает к пользователю."""
    uc = ReceiveTitleUsecase()
    uc.execute(
        ReceiveTitle(
            request_user_id=user_id,
            source_id=source_id,
        )
    )
