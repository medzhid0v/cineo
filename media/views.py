import logging

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max, Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, FormView, ListView

from media.forms import KinopoiskImportForm, SignUpForm, UserTitleStateForm
from media.models import Episode, Title, TitleCategory, UserEpisodeState, UserProgress, UserTitleState
from media.services.user_state import ensure_user_records
from media.tasks import (
    import_title_task,
    remove_from_watchlist_task,
    toggle_episode_watched_task,
    update_user_title_state_task,
)

logger = logging.getLogger(__name__)


class SignUpView(FormView):
    template_name = "auth/signup.html"
    form_class = SignUpForm

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("media:list")


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


class ImportView(LoginRequiredMixin, FormView):
    template_name = "media/import.html"
    form_class = KinopoiskImportForm

    def form_valid(self, form):
        kp_id = form.cleaned_data["kp_id"]
        import_title_task.delay(kp_id=kp_id, user_id=self.request.user.id)
        messages.success(self.request, "Импорт запущен в фоне. Обновите главную страницу через несколько секунд.")
        logger.info("Импорт поставлен в очередь user_id=%s kp_id=%s", self.request.user.id, kp_id)
        return redirect(reverse("media:list"))


class UpdateUserTitleStateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        title = get_object_or_404(Title, pk=pk)
        user_state, _ = ensure_user_records(request.user, title)
        form = UserTitleStateForm(request.POST, instance=user_state)

        if form.is_valid():
            update_user_title_state_task.delay(
                user_id=request.user.id,
                title_id=title.id,
                status=form.cleaned_data["status"],
                rating=form.cleaned_data["rating"],
                review=form.cleaned_data["review"],
            )
            logger.info("Обновление состояния поставлено в очередь user_id=%s title_id=%s", request.user.id, title.id)

        return redirect("media:detail", pk=pk)


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


class RemoveFromWatchlistView(LoginRequiredMixin, View):
    def post(self, request, pk):
        title = get_object_or_404(Title, pk=pk)
        remove_from_watchlist_task.delay(user_id=request.user.id, title_id=title.id)
        logger.info("Произведение удалено из списка user_id=%s title_id=%s", request.user.id, title.id)
        return redirect("media:list")
