import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View

from media.models import Episode, Title
from media.tasks import (
    toggle_episode_watched_task,
)

logger = logging.getLogger(__name__)


class ToggleEpisodeWatchedView(LoginRequiredMixin, View):
    def post(self, request, pk, episode_id):
        title = get_object_or_404(Title, pk=pk)
        episode = get_object_or_404(Episode, pk=episode_id, season__title=title)
        watched = request.POST.get("watched") == "1"
        toggle_episode_watched_task.delay(user_id=request.user.id, episode_id=episode.id, watched=watched)
        logger.info(
            "Статус эпизода обновлен user_id=%s title_id=%s episode_id=%s watched=%s",
            request.user.id,
            title.id,
            episode.id,
            watched,
        )
        return HttpResponseRedirect(reverse("media:detail", kwargs={"pk": pk}))
