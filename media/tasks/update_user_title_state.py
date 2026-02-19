from celery import shared_task
from django.contrib.auth import get_user_model

from media.models import Title
from media.services.user_state import apply_user_state_form, ensure_user_records


@shared_task
def update_user_title_state_task(user_id: int, title_id: int, status: str, rating, review: str) -> None:
    """Обновляет статус просмотра, рейтинг и ревью пользователя для тайтла."""
    user = get_user_model().objects.get(pk=user_id)
    title = Title.objects.get(pk=title_id)
    user_state, _ = ensure_user_records(user, title)
    apply_user_state_form(user_state, status=status, rating=rating, review=review)
