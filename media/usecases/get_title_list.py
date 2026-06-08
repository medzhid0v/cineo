from dataclasses import dataclass
from typing import Optional

from django.db.models import Max, Prefetch, Q, QuerySet

from media.models import Title, TitleCategory, UserProgress, UserTitleState, WatchStatus
from media.usecases.base_usecase import BaseUsecase


@dataclass(frozen=True)
class GetTitleListInput:
    user_id: int
    category: Optional[str] = None
    status: Optional[str] = None
    q: Optional[str] = None


@dataclass(frozen=True)
class GetTitleListOutput:
    queryset: QuerySet[Title]
    category: str
    status: str
    q: str
    categories: list[tuple[str, str]]
    statuses: list[tuple[str, str]]


class GetTitleListUsecase(BaseUsecase[GetTitleListInput, GetTitleListOutput]):
    """Список тайтлов пользователя с фильтрами по категории/статусу и поиском по названию."""

    def execute(self, data: GetTitleListInput) -> GetTitleListOutput:
        states = UserTitleState.objects.filter(user_id=data.user_id)
        progress = UserProgress.objects.filter(user_id=data.user_id)

        queryset = (
            Title.objects.filter(user_states__user_id=data.user_id)
            .annotate(
                last_viewed_at=Max("user_progress__last_watched_at"),
                user_started_at=Max("user_states__started_at"),
                user_finished_at=Max("user_states__finished_at"),
            )
            .prefetch_related(
                Prefetch("user_states", queryset=states, to_attr="current_user_states"),
                Prefetch("user_progress", queryset=progress, to_attr="current_user_progress"),
            )
            .distinct()
            .order_by("-user_finished_at", "-user_started_at", "-created_at", "-last_viewed_at")
        )

        category = data.category if data.category in TitleCategory.values else ""
        if category:
            queryset = queryset.filter(category=category)

        status = data.status if data.status in WatchStatus.values else ""
        if status:
            queryset = queryset.filter(user_states__user_id=data.user_id, user_states__status=status)

        q = (data.q or "").strip()
        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(original_name__icontains=q))

        return GetTitleListOutput(
            queryset=queryset,
            category=category,
            status=status,
            q=q,
            categories=TitleCategory.choices,
            statuses=WatchStatus.choices,
        )
