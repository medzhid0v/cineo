from dataclasses import dataclass, field

from django.db.models import Avg, Count

from media.models import Title, TitleCategory, UserTitleState, WatchStatus
from media.usecases.base_usecase import BaseUsecase


@dataclass(frozen=True)
class GetStatsInput:
    user_id: int


@dataclass(frozen=True)
class GetStatsOutput:
    total: int
    watched: int
    average_rating: float | None
    by_category: dict[str, int] = field(default_factory=dict)
    by_status: dict[str, int] = field(default_factory=dict)


class GetStatsUsecase(BaseUsecase[GetStatsInput, GetStatsOutput]):
    """Агрегаты библиотеки пользователя для дашборда: всего / просмотрено / средний рейтинг."""

    def execute(self, data: GetStatsInput) -> GetStatsOutput:
        states = UserTitleState.objects.filter(user_id=data.user_id)

        total = states.count()
        watched = states.filter(status=WatchStatus.COMPLETED).count()
        average_rating = states.filter(rating__isnull=False).aggregate(avg=Avg("rating"))["avg"]

        by_status = {row["status"]: row["n"] for row in states.values("status").annotate(n=Count("id"))}
        # Гарантируем все статусы в ответе (даже с нулём) — удобно для UI.
        by_status = {value: by_status.get(value, 0) for value, _ in WatchStatus.choices}

        category_rows = (
            Title.objects.filter(user_states__user_id=data.user_id)
            .values("category")
            .annotate(n=Count("id", distinct=True))
        )
        by_category_raw = {row["category"]: row["n"] for row in category_rows}
        by_category = {value: by_category_raw.get(value, 0) for value, _ in TitleCategory.choices}

        return GetStatsOutput(
            total=total,
            watched=watched,
            average_rating=round(average_rating, 2) if average_rating is not None else None,
            by_category=by_category,
            by_status=by_status,
        )
