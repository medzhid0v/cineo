from dataclasses import dataclass
from typing import Optional

from django.db.models import Max, Prefetch, QuerySet

from media.models import Title, TitleCategory, UserProgress, UserTitleState
from media.usecases.base_usecase import BaseUsecase


@dataclass(frozen=True)
class GetTitleListInput:
    user_id: int
    category: Optional[str] = None


@dataclass(frozen=True)
class GetTitleListOutput:
    queryset: QuerySet[Title]
    category: str
    categories: list[tuple[str, str]]


class GetTitleListUsecase(BaseUsecase[GetTitleListInput, GetTitleListOutput]):
    """Usecase для получения списка тайтлов пользователя с фильтрацией по категории."""

    def execute(self, data: GetTitleListInput) -> GetTitleListOutput:
        states = UserTitleState.objects.filter(user_id=data.user_id)
        progress = UserProgress.objects.filter(user_id=data.user_id)

        queryset = (
            Title.objects.filter(user_states__user_id=data.user_id)
            .annotate(last_viewed_at=Max("user_progress__last_watched_at"))
            .prefetch_related(
                Prefetch("user_states", queryset=states, to_attr="current_user_states"),
                Prefetch("user_progress", queryset=progress, to_attr="current_user_progress"),
            )
            .distinct()
            .order_by("-created_at", "-last_viewed_at")
        )

        category = data.category if data.category in TitleCategory.values else ""
        if category:
            queryset = queryset.filter(category=category)

        return GetTitleListOutput(
            queryset=queryset,
            category=category,
            categories=TitleCategory.choices,
        )
