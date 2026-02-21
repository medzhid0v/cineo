import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View

from media.models import Episode, Title
from media.tasks import toggle_episode_watched_task
from media.usecases.title.get_title_detail import GetTitleDetailInput, GetTitleDetailUsecase
from media.usecases.toggle_episode_watched import ToggleEpisodeWatchedInput, ToggleEpisodeWatchedUsecase

logger = logging.getLogger(__name__)


class ToggleEpisodeWatchedView(LoginRequiredMixin, View):
    def post(self, request, pk, episode_id):
        title = get_object_or_404(Title, pk=pk)
        episode = get_object_or_404(Episode, pk=episode_id, season__title=title)
        watched = request.POST.get("watched") == "1"

        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        if is_ajax:
            # Для AJAX выполняем синхронно для немедленного ответа
            usecase = ToggleEpisodeWatchedUsecase()
            usecase.execute(
                ToggleEpisodeWatchedInput(
                    user_id=request.user.id,
                    episode_id=episode.id,
                    watched=watched,
                )
            )
        else:
            # Для обычных запросов используем асинхронную задачу
            toggle_episode_watched_task.delay(user_id=request.user.id, episode_id=episode.id, watched=watched)

        logger.info(
            "Статус эпизода обновлен user_id=%s title_id=%s episode_id=%s watched=%s",
            request.user.id,
            title.id,
            episode.id,
            watched,
        )

        if is_ajax:
            # Подсчитываем обновленные данные через usecase
            detail_usecase = GetTitleDetailUsecase()
            result = detail_usecase.execute(
                GetTitleDetailInput(
                    user_id=request.user.id,
                    title_id=title.id,
                )
            )

            return JsonResponse(
                {
                    "watched": watched,
                    "watched_episodes": result.watched_episodes,
                    "total_episodes": result.total_episodes,
                }
            )

        return HttpResponseRedirect(reverse("media:detail", kwargs={"pk": pk}))
