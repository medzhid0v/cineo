import logging

from django.db import transaction

from media.models import Episode, Season, Title, TitleCategory
from media.services.providers import MediaProvider
from media.services.user_state import ensure_user_records

logger = logging.getLogger(__name__)


@transaction.atomic
def import_title_by_external_id(*, external_id: int, provider: MediaProvider, user_id: int) -> Title:
    dto = provider.get_title(external_id)

    category = dto.category if dto.category in TitleCategory.values else TitleCategory.OTHER
    if category == "movie":
        category = TitleCategory.FILM

    title, _ = Title.objects.update_or_create(
        kp_id=dto.external_id,
        defaults={
            "category": category,
            "is_series": dto.is_series,
            "name": dto.name,
            "year": dto.year,
            "duration_min": dto.duration_min,
            "poster_url": dto.poster_url,
            "kp_url": dto.source_url,
        },
    )

    logger.info("Импортирован тайтл kp_id=%s category=%s name=%s", dto.external_id, category, dto.name)

    if title.is_series:
        seasons_dto = provider.get_seasons(external_id)
        for s in seasons_dto.seasons:
            season, _ = Season.objects.update_or_create(
                title=title,
                number=s.number,
                defaults={"episodes_count": len(s.episodes) or None},
            )
            for ep in s.episodes:
                Episode.objects.update_or_create(
                    season=season,
                    number=ep.episode_number,
                    defaults={
                        "name": ep.name,
                        "duration_min": ep.duration_min,
                        "air_date": ep.air_date,
                    },
                )

    ensure_user_records(user_id=user_id, title_id=title.id)
    logger.info("Созданы пользовательские записи user_id=%s title_id=%s", user_id, title.id)
    return title
