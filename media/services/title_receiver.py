import logging

from django.db import transaction

from media.dtos import SeasonsDTO, TitleDTO
from media.models import Episode, Season, Title
from media.services.user_state import ensure_user_records

logger = logging.getLogger(__name__)


@transaction.atomic
def update_or_create_title(user_id: int, title_dto: TitleDTO, seasons_dto: SeasonsDTO) -> tuple[Title, bool]:
    title, created = Title.objects.update_or_create(
        kp_id=title_dto.external_id,
        defaults={
            "category": title_dto.category,
            "is_series": title_dto.is_series,
            "name": title_dto.name,
            "year": title_dto.year,
            "duration_min": title_dto.duration_min,
            "poster_url": title_dto.poster_url,
            "kp_url": title_dto.source_url,
        },
    )

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
    return title, created
