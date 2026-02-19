import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max, Prefetch
from django.views.generic import ListView

from media.models import Title, TitleCategory, UserProgress, UserTitleState

logger = logging.getLogger(__name__)


class TitleListView(LoginRequiredMixin, ListView):
    model = Title
    template_name = "media/title_list.html"
    context_object_name = "titles"

    def get_queryset(self):
        category = self.request.GET.get("category")
        states = UserTitleState.objects.filter(user=self.request.user)
        progress = UserProgress.objects.filter(user=self.request.user)

        queryset = (
            Title.objects.filter(user_states__user=self.request.user)
            .annotate(last_viewed_at=Max("user_progress__last_watched_at"))
            .prefetch_related(
                Prefetch("user_states", queryset=states, to_attr="current_user_states"),
                Prefetch("user_progress", queryset=progress, to_attr="current_user_progress"),
            )
            .distinct()
            .order_by("-created_at", "-last_viewed_at")
        )

        if category in TitleCategory.values:
            queryset = queryset.filter(category=category)

        logger.debug("Получен список произведений user_id=%s category=%s", self.request.user.id, category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.request.GET.get("category", "")
        context["categories"] = TitleCategory.choices
        return context
