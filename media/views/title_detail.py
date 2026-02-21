import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from media.forms import UpdateUserTitleStateForm
from media.models import Title
from media.usecases.title import GetTitleDetailInput, GetTitleDetailUsecase

logger = logging.getLogger(__name__)


class TitleDetailView(LoginRequiredMixin, View):
    """
    Detailed view for a title (movie or TV series).
    """

    model = Title
    template_name = "media/title_detail.html"
    context_object_name = "title"

    def get(self, request, pk: int, *args, **kwargs):
        usecase = GetTitleDetailUsecase()
        result = usecase.execute(
            GetTitleDetailInput(
                user_id=request.user.id,
                title_id=pk,
            )
        )

        context = {
            "title": result.title,
            "user_state": result.user_state,
            "progress": result.progress,
            "state_form": UpdateUserTitleStateForm(instance=result.user_state),
            "watched_episode_ids": result.watched_episode_ids,
            "total_episodes": result.total_episodes,
            "watched_episodes": result.watched_episodes,
        }
        return render(request, self.template_name, context)
