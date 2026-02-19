import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from media.forms import UserTitleStateForm
from media.models import Episode, Title, UserEpisodeState
from media.services.user_state import ensure_user_records

logger = logging.getLogger(__name__)


class TitleDetailView(LoginRequiredMixin, DetailView):
    model = Title
    template_name = "media/title_detail.html"
    context_object_name = "title"

    def get_queryset(self):
        return Title.objects.prefetch_related("seasons__episodes")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = self.object
        user_state, progress = ensure_user_records(self.request.user, title)

        watched_states = UserEpisodeState.objects.filter(
            user=self.request.user,
            episode__season__title=title,
            watched=True,
        ).select_related("episode")
        watched_ids = set(watched_states.values_list("episode_id", flat=True))

        episodes_qs = Episode.objects.filter(season__title=title)
        total_episodes = episodes_qs.count()
        watched_episodes = len(watched_ids)

        context.update(
            {
                "user_state": user_state,
                "progress": progress,
                "state_form": UserTitleStateForm(instance=user_state),
                "watched_episode_ids": watched_ids,
                "total_episodes": total_episodes,
                "watched_episodes": watched_episodes,
            }
        )
        return context
