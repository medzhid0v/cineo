import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from media.usecases.get_title_list import GetTitleListInput, GetTitleListUsecase

logger = logging.getLogger(__name__)


class TitleListView(LoginRequiredMixin, ListView):
    model = None
    template_name = "media/title_list.html"
    context_object_name = "titles"

    def get_usecase_result(self):
        """Получает результат usecase один раз для использования в get_queryset и get_context_data."""
        if not hasattr(self, "_usecase_result"):
            usecase = GetTitleListUsecase()
            self._usecase_result = usecase.execute(
                GetTitleListInput(
                    user_id=self.request.user.id,
                    category=self.request.GET.get("category"),
                )
            )
            logger.debug(
                "Получен список произведений user_id=%s category=%s",
                self.request.user.id,
                self._usecase_result.category,
            )
        return self._usecase_result

    def get_queryset(self):
        return self.get_usecase_result().queryset

    def get_context_data(self, **kwargs):
        result = self.get_usecase_result()
        context = super().get_context_data(**kwargs)
        context["category"] = result.category
        context["categories"] = result.categories
        return context
