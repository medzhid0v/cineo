import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from media.services.importer import import_title_by_external_id
from media.services.providers.kinopoisk import KinopoiskProvider

logger = logging.getLogger(__name__)


@shared_task
def import_title_task(kp_id: int, user_id: int) -> int:
    """Импортирует тайтл из Кинопоиска по kp_id и привязывает к пользователю."""
    user = get_user_model().objects.get(pk=user_id)
    provider = KinopoiskProvider()
    title = import_title_by_external_id(kp_id, provider, user)
    logger.info("Импорт завершен user_id=%s title_id=%s", user_id, title.id)
    return title.id
