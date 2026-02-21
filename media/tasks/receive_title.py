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
def receive_title_task(*, source_id: int, user_id: int) -> None:
    logger.info("ReceiveTitle started [user_id=%s source_id=%s]", user_id, source_id)
    uc = ReceiveTitleUsecase()
    uc.execute(
        ReceiveTitleInput(
            user_id=user_id,
            source_id=source_id,
        )
    )
