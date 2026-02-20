import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView

from media.forms import KinopoiskImportForm
from media.tasks import (
    import_title_task,
)

logger = logging.getLogger(__name__)


class ImportView(LoginRequiredMixin, FormView):
    template_name = "media/import.html"
    form_class = KinopoiskImportForm

    def form_valid(self, form):
        kp_id = form.cleaned_data["kp_id"]
        import_title_task.delay(kp_id=kp_id, user_id=self.request.user.id)
        messages.success(self.request, "Импорт запущен в фоне. Обновите главную страницу через несколько секунд.")
        logger.info("Импорт поставлен в очередь user_id=%s kp_id=%s", self.request.user.id, kp_id)

        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True})

        return redirect(reverse("media:list"))
