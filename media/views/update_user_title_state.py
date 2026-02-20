import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from media.forms import UpdateUserTitleStateForm
from media.models import Title
from media.services.user_state import ensure_user_records
from media.usecases.update_user_title_state import UpdateUserTitleStateInput, UpdateUserTitleStateUsecase

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
        form = UpdateUserTitleStateForm(request.POST, instance=user_state)

        if form.is_valid():
            data = UpdateUserTitleStateInput(
                user_id=request.user.id,
                title_id=title.id,
                status=form.cleaned_data["status"],
                rating=form.cleaned_data.get("rating"),
                review=form.cleaned_data.get("review", ""),
                started_at=form.cleaned_data.get("started_at"),
                finished_at=form.cleaned_data.get("finished_at"),
            )

            UpdateUserTitleStateUsecase().execute(data)

            logger.info(
                "User title state updated [user_id=%s title_id=%s]",
                request.user.id,
                title.id,
            )

        return redirect("media:detail", pk=pk)
