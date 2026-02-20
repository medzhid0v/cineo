import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from media.models import Title
from media.tasks import remove_from_watchlist_task

logger = logging.getLogger(__name__)


class RemoveFromWatchlistView(LoginRequiredMixin, View):
    def post(self, request, pk):
        title = get_object_or_404(Title, pk=pk)
        remove_from_watchlist_task.delay(user_id=request.user.id, title_id=title.id)
        logger.info("Произведение удалено из списка user_id=%s title_id=%s", request.user.id, title.id)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True})

        return redirect("media:list")
