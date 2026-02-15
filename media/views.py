from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, FormView, ListView

from media.forms import KinopoiskImportForm, SignUpForm, UserTitleStateForm
from media.models import Episode, Title, TitleCategory, UserEpisodeState, UserProgress, UserTitleState
from media.services.importer import import_title_by_external_id
from media.services.providers.kinopoisk import KinopoiskProvider
from media.services.user_state import apply_user_state_form, ensure_user_records, toggle_episode_watched


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
            .prefetch_related(
                Prefetch("user_states", queryset=states, to_attr="current_user_states"),
                Prefetch("user_progress", queryset=progress, to_attr="current_user_progress"),
            )
            .distinct()
            .order_by("-updated_at")
        )

        if category in TitleCategory.values:
            queryset = queryset.filter(category=category)

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
        provider = KinopoiskProvider()
        title = import_title_by_external_id(kp_id, provider, self.request.user)
        return redirect(reverse("media:detail", kwargs={"pk": title.pk}))


class UpdateUserTitleStateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        title = get_object_or_404(Title, pk=pk)
        user_state, _ = ensure_user_records(request.user, title)
        form = UserTitleStateForm(request.POST, instance=user_state)

        if form.is_valid():
            apply_user_state_form(
                user_state,
                status=form.cleaned_data["status"],
                rating=form.cleaned_data["rating"],
                review=form.cleaned_data["review"],
            )

        return redirect("media:detail", pk=pk)


class ToggleEpisodeWatchedView(LoginRequiredMixin, View):
    def post(self, request, pk, episode_id):
        title = get_object_or_404(Title, pk=pk)
        episode = get_object_or_404(Episode, pk=episode_id, season__title=title)
        watched = request.POST.get("watched") == "1"
        toggle_episode_watched(user=request.user, episode=episode, watched=watched)
        return HttpResponseRedirect(reverse("media:detail", kwargs={"pk": pk}))


class RemoveFromWatchlistView(LoginRequiredMixin, View):
    def post(self, request, pk):
        title = get_object_or_404(Title, pk=pk)
        episode_states = UserEpisodeState.objects.filter(user=request.user, episode__season__title=title)
        episode_states.delete()
        UserProgress.objects.filter(user=request.user, title=title).delete()
        UserTitleState.objects.filter(user=request.user, title=title).delete()
        return redirect("media:list")
