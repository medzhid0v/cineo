import logging

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from media.models import Title, UserTablePreferences
from media.tasks import receive_title_task
from media.usecases import (
    GetStatsInput,
    GetStatsUsecase,
    GetTitleListInput,
    GetTitleListUsecase,
    RemoveFromWatchlistInput,
    RemoveFromWatchlistUsecase,
    SearchTitlesInput,
    SearchTitlesUsecase,
    SignUpInput,
    SignUpUsecase,
    ToggleEpisodeWatchedInput,
    ToggleEpisodeWatchedUsecase,
    UpdateUserTitleStateInput,
    UpdateUserTitleStateUsecase,
)
from media.usecases.title import GetTitleDetailInput, GetTitleDetailUsecase

from .serializers import (
    AddTitleSerializer,
    TablePreferencesSerializer,
    TitleDetailSerializer,
    TitleListSerializer,
    ToggleEpisodeSerializer,
    UpdateStateSerializer,
    UserTitleStateSerializer,
)

logger = logging.getLogger(__name__)

# Доступные колонки таблицы (ключи совпадают с полями TitleListSerializer).
AVAILABLE_COLUMNS = [
    {"key": "poster_url", "label": "Постер"},
    {"key": "name", "label": "Название"},
    {"key": "year", "label": "Год"},
    {"key": "category_display", "label": "Категория"},
    {"key": "user_status_display", "label": "Статус"},
    {"key": "user_rating", "label": "Моя оценка"},
    {"key": "rating_kp", "label": "Рейтинг КП"},
    {"key": "rating_imdb", "label": "Рейтинг IMDb"},
    {"key": "duration_min", "label": "Длительность"},
    {"key": "genres", "label": "Жанры"},
    {"key": "countries", "label": "Страны"},
    {"key": "age_limit", "label": "Возраст"},
    {"key": "progress_label", "label": "Прогресс"},
    {"key": "last_viewed_at", "label": "Последний просмотр"},
]
DEFAULT_COLUMNS = ["poster_url", "name", "year", "category_display", "user_status_display", "user_rating", "rating_kp"]


class LibraryPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 500


# ============ Auth ============


@method_decorator(ensure_csrf_cookie, name="get")
class MeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Заодно проставляет csrf-cookie для SPA.
        if not request.user.is_authenticated:
            return Response({"authenticated": False}, status=status.HTTP_200_OK)
        return Response(
            {
                "authenticated": True,
                "id": request.user.id,
                "username": request.user.username,
                "is_staff": request.user.is_staff,
            }
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get("username", "")
    password = request.data.get("password", "")
    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response({"detail": "Неверный логин или пароль."}, status=status.HTTP_401_UNAUTHORIZED)
    login(request, user)
    return Response({"id": user.id, "username": user.username})


@api_view(["POST"])
def logout_view(request):
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([AllowAny])
def signup_view(request):
    username = (request.data.get("username") or "").strip()
    password = request.data.get("password") or ""
    if len(username) < 3:
        return Response({"detail": "Логин слишком короткий (минимум 3 символа)."}, status=status.HTTP_400_BAD_REQUEST)
    if len(password) < 6:
        return Response({"detail": "Пароль слишком короткий (минимум 6 символов)."}, status=status.HTTP_400_BAD_REQUEST)
    if get_user_model().objects.filter(username=username).exists():
        return Response({"detail": "Пользователь с таким логином уже существует."}, status=status.HTTP_409_CONFLICT)
    try:
        user = SignUpUsecase().execute(SignUpInput(username=username, password=password))
    except IntegrityError:
        return Response({"detail": "Пользователь с таким логином уже существует."}, status=status.HTTP_409_CONFLICT)
    login(request, user)
    return Response({"id": user.id, "username": user.username}, status=status.HTTP_201_CREATED)


# ============ Stats ============


@api_view(["GET"])
def stats_view(request):
    result = GetStatsUsecase().execute(GetStatsInput(user_id=request.user.id))
    return Response(
        {
            "total": result.total,
            "watched": result.watched,
            "average_rating": result.average_rating,
            "by_category": result.by_category,
            "by_status": result.by_status,
        }
    )


# ============ Titles ============


@api_view(["GET"])
def titles_list_view(request):
    result = GetTitleListUsecase().execute(
        GetTitleListInput(
            user_id=request.user.id,
            category=request.GET.get("category"),
            status=request.GET.get("status"),
            q=request.GET.get("q"),
        )
    )
    paginator = LibraryPagination()
    page = paginator.paginate_queryset(result.queryset, request)
    data = TitleListSerializer(page, many=True).data
    response = paginator.get_paginated_response(data)
    response.data["filters"] = {
        "category": result.category,
        "status": result.status,
        "q": result.q,
        "categories": [{"value": v, "label": label} for v, label in result.categories],
        "statuses": [{"value": v, "label": label} for v, label in result.statuses],
    }
    return response


@api_view(["GET"])
def title_detail_view(request, pk):
    result = GetTitleDetailUsecase().execute(GetTitleDetailInput(user_id=request.user.id, title_id=pk))
    serializer = TitleDetailSerializer(
        result.title,
        context={
            "user_state": result.user_state,
            "progress": result.progress,
            "watched_episode_ids": result.watched_episode_ids,
        },
    )
    # total/watched прокидываем через атрибуты сериализуемого объекта
    result.title.total_episodes = result.total_episodes
    result.title.watched_episodes = result.watched_episodes
    return Response(serializer.data)


@api_view(["POST"])
def add_title_view(request):
    serializer = AddTitleSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    source_id = serializer.validated_data["source_id"]
    receive_title_task.delay(source_id=source_id, user_id=request.user.id)
    logger.info("ReceiveTitle queued via API [user_id=%s source_id=%s]", request.user.id, source_id)
    return Response({"queued": True, "source_id": source_id}, status=status.HTTP_202_ACCEPTED)


@api_view(["POST"])
def update_state_view(request, pk):
    get_object_or_404(Title, pk=pk)
    serializer = UpdateStateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    vd = serializer.validated_data

    user_state = UpdateUserTitleStateUsecase().execute(
        UpdateUserTitleStateInput(
            user_id=request.user.id,
            title_id=pk,
            status=vd["status"],
            rating=vd.get("rating"),
            review=vd.get("review", ""),
            started_at=vd.get("started_at"),
            finished_at=vd.get("finished_at"),
            started_at_provided="started_at" in request.data,
            finished_at_provided="finished_at" in request.data,
        )
    )
    return Response(UserTitleStateSerializer(user_state).data)


@api_view(["POST"])
def toggle_episode_view(request, pk):
    """Синхронное переключение «просмотрено» — для мгновенного отклика UI."""
    serializer = ToggleEpisodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    state = ToggleEpisodeWatchedUsecase().execute(
        ToggleEpisodeWatchedInput(
            user_id=request.user.id,
            episode_id=serializer.validated_data["episode_id"],
            watched=serializer.validated_data["watched"],
        )
    )
    return Response({"episode_id": state.episode_id, "watched": state.watched})


@api_view(["DELETE", "POST"])
def remove_title_view(request, pk):
    """Синхронное удаление из списка пользователя (Title остаётся в общей БД)."""
    get_object_or_404(Title, pk=pk)
    RemoveFromWatchlistUsecase().execute(RemoveFromWatchlistInput(user_id=request.user.id, title_id=pk))
    return Response(status=status.HTTP_204_NO_CONTENT)


# ============ Search ============


@api_view(["GET"])
def search_view(request):
    query = request.GET.get("q", "")
    if not query.strip():
        return Response({"total": 0, "results": []})
    page = int(request.GET.get("page", 1) or 1)
    result = SearchTitlesUsecase().execute(SearchTitlesInput(query=query, page=page))
    return Response(
        {
            "total": result.total,
            "results": [r.model_dump() for r in result.results],
        }
    )


# ============ Table preferences ============


class PreferencesView(APIView):
    def _serialize(self, prefs: UserTablePreferences) -> dict:
        return {
            "visible_columns": prefs.visible_columns or DEFAULT_COLUMNS,
            "page_size": prefs.page_size,
            "view_mode": prefs.view_mode,
            "available_columns": AVAILABLE_COLUMNS,
            "default_columns": DEFAULT_COLUMNS,
        }

    def get(self, request):
        prefs, _ = UserTablePreferences.objects.get_or_create(
            user=request.user,
            defaults={"visible_columns": DEFAULT_COLUMNS},
        )
        return Response(self._serialize(prefs))

    def put(self, request):
        serializer = TablePreferencesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prefs, _ = UserTablePreferences.objects.get_or_create(
            user=request.user,
            defaults={"visible_columns": DEFAULT_COLUMNS},
        )
        for field, value in serializer.validated_data.items():
            setattr(prefs, field, value)
        prefs.save()
        return Response(self._serialize(prefs))
