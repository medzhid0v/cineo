from django.db import transaction

from media.models import Episode, Season, Title, TitleCategory, TitleType
from media.services.providers import MediaProvider
from media.services.user_state import ensure_user_records


@transaction.atomic
def import_title_by_external_id(external_id: int, provider: MediaProvider, user) -> Title:
    dto = provider.get_title(external_id)

    title_type = TitleType.SERIES if dto.is_series else TitleType.MOVIE
    category = dto.category if dto.category in TitleCategory.values else TitleCategory.OTHER

    title, _ = Title.objects.update_or_create(
        kp_id=dto.external_id,
        defaults={
            "type": title_type,
            "category": category,
            "name": dto.name,
            "year": dto.year,
            "duration_min": dto.duration_min,
            "poster_url": dto.poster_url,
            "kp_url": dto.source_url,
        },
    )

    if title.type == TitleType.SERIES:
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

    ensure_user_records(user, title)
    return title
