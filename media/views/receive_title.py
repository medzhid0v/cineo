import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView

from media.forms import ReceiveTitleForm
from media.tasks import receive_title_task

logger = logging.getLogger(__name__)


class ReceiveTitleView(LoginRequiredMixin, FormView):
    template_name = "media/import.html"
    form_class = ReceiveTitleForm

    def form_valid(self, form):
        source_id = form.cleaned_data["source_id"]

        receive_title_task.delay(source_id=source_id, user_id=self.request.user.id)

        logger.info(
            "ReceiveTitle queued [user_id=%s source_id=%s]",
            self.request.user.id,
            source_id,
        )

        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True})

        return redirect(reverse("media:list"))
