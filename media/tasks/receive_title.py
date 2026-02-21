import logging

from celery import shared_task

from media.usecases.receive_title import ReceiveTitleInput, ReceiveTitleUsecase

logger = logging.getLogger(__name__)


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def receive_title_task(*, source_id: int, user_id: int) -> dict:
    uc = ReceiveTitleUsecase()
    res = uc.execute(
        ReceiveTitleInput(
            user_id=user_id,
            source_id=source_id,
        )
    )
    return res
