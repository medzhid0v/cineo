import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import FormView

from media.forms import UpdateUserTitleStateForm
from media.models import Title
from media.services.user_state import ensure_user_records
from media.usecases.update_user_title_state import UpdateUserTitleStateInput, UpdateUserTitleStateUsecase

logger = logging.getLogger(__name__)


class UpdateUserTitleStateView(LoginRequiredMixin, FormView):
    """
    Это обработчик POST-запроса, который обновляет:
     - статус просмотра (planned / watching / completed…)
     - оценку (0–10 или None)
     - отзыв

    для конкретного пользователя и конкретного Title.
    """

    form_class = UpdateUserTitleStateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        title = get_object_or_404(Title, pk=self.kwargs["pk"])
        user_state, _ = ensure_user_records(self.request.user, title)
        # Обновляем из БД, чтобы получить актуальные значения
        user_state.refresh_from_db()
        kwargs["instance"] = user_state
        # Сохраняем начальные значения для сравнения в form_valid
        self._initial_started_at = user_state.started_at
        self._initial_finished_at = user_state.finished_at
        return kwargs

    def form_valid(self, form):
        title = get_object_or_404(Title, pk=self.kwargs["pk"])

        # Получаем начальные значения из формы (которые были при инициализации)
        initial_started_at = getattr(self, "_initial_started_at", None)
        initial_finished_at = getattr(self, "_initial_finished_at", None)

        # Получаем новые значения из формы
        new_started_at = form.cleaned_data.get("started_at")
        new_finished_at = form.cleaned_data.get("finished_at")

        # Проверяем, изменились ли значения по сравнению с начальными
        started_at_changed = new_started_at != initial_started_at
        finished_at_changed = new_finished_at != initial_finished_at

        uc = UpdateUserTitleStateUsecase()
        uc.execute(
            UpdateUserTitleStateInput(
                user_id=self.request.user.id,
                title_id=title.id,
                status=form.cleaned_data["status"],
                rating=form.cleaned_data.get("rating"),
                review=form.cleaned_data.get("review", ""),
                started_at=new_started_at,
                finished_at=new_finished_at,
                started_at_provided=started_at_changed,
                finished_at_provided=finished_at_changed,
            )
        )

        logger.info(
            "User title state updated [user_id=%s title_id=%s]",
            self.request.user.id,
            title.id,
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("media:detail", kwargs={"pk": self.kwargs["pk"]})
