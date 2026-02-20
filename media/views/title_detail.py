import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from media.forms import UpdateUserTitleStateForm
from media.models import Title
from media.usecases.get_title_detail import GetTitleDetailInput, GetTitleDetailUsecase

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

        usecase = GetTitleDetailUsecase()
        result = usecase.execute(
            GetTitleDetailInput(
                user_id=self.request.user.id,
                title_id=title.id,
            )
        )

        state_form = UpdateUserTitleStateForm(instance=result.user_state)

        context.update(
            {
                "user_state": result.user_state,
                "progress": result.progress,
                "state_form": state_form,
                "watched_episode_ids": result.watched_episode_ids,
                "total_episodes": result.total_episodes,
                "watched_episodes": result.watched_episodes,
            }
        )
        return context
