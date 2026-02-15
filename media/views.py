from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, FormView, ListView

from media.forms import KinopoiskImportForm
from media.models import Title
from media.services.importer import import_title_by_external_id
from media.services.providers.kinopoisk import KinopoiskProvider


class TitleListView(LoginRequiredMixin, ListView):
    model = Title
    template_name = "media/title_list.html"
    context_object_name = "titles"


class TitleDetailView(LoginRequiredMixin, DetailView):
    model = Title
    template_name = "media/title_detail.html"
    context_object_name = "title"


class ImportView(LoginRequiredMixin, FormView):
    template_name = "media/import.html"
    form_class = KinopoiskImportForm

    def form_valid(self, form):
        kp_id = form.cleaned_data["kp_id"]
        provider = KinopoiskProvider()
        title = import_title_by_external_id(kp_id, provider)

        return redirect(reverse("media:detail", kwargs={"pk": title.pk}))
