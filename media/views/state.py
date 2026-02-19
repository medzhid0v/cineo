import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from media.forms import UserTitleStateForm
from media.models import Title
from media.services.user_state import ensure_user_records
from media.tasks import (
    update_user_title_state_task,
)

logger = logging.getLogger(__name__)


class UpdateUserTitleStateView(LoginRequiredMixin, View):
    """
    Это обработчик POST-запроса, который обновляет:
     - статус просмотра (planned / watching / completed…)
     - оценку (0–10 или None)
     - отзыв

    для конкретного пользователя и конкретного Title.
    """

    def post(self, request, pk):
        title = get_object_or_404(Title, pk=pk)
        user_state, _ = ensure_user_records(request.user, title)
        form = UserTitleStateForm(request.POST, instance=user_state)

        if form.is_valid():
            update_user_title_state_task(
                user_id=request.user.id,
                title_id=title.id,
                status=form.cleaned_data["status"],
                rating=form.cleaned_data["rating"],
                review=form.cleaned_data["review"],
            )
            logger.info("Обновление состояния title_id=%s user_id=%s", request.user.id, title.id)

        return redirect("media:detail", pk=pk)
