from rest_framework import serializers

from media.models import Episode, Season, Title, UserTitleState, WatchStatus


def _first_user_state(title: Title) -> UserTitleState | None:
    """Берёт состояние текущего пользователя из prefetch to_attr (current_user_states)."""
    states = getattr(title, "current_user_states", None)
    if states:
        return states[0]
    return None


def _first_user_progress(title: Title):
    progress = getattr(title, "current_user_progress", None)
    if progress:
        return progress[0]
    return None


class TitleListSerializer(serializers.ModelSerializer):
    """Строка библиотеки для таблицы/сетки (с данными состояния пользователя)."""

    category_display = serializers.CharField(source="get_category_display", read_only=True)
    user_status = serializers.SerializerMethodField()
    user_status_display = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    progress_label = serializers.SerializerMethodField()
    last_viewed_at = serializers.DateTimeField(read_only=True, allow_null=True)

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "original_name",
            "year",
            "category",
            "category_display",
            "is_series",
            "poster_url",
            "duration_min",
            "rating_kp",
            "rating_imdb",
            "genres",
            "countries",
            "age_limit",
            "start_year",
            "end_year",
            "user_status",
            "user_status_display",
            "user_rating",
            "progress_label",
            "last_viewed_at",
            "created_at",
        )

    def get_user_status(self, obj) -> str | None:
        state = _first_user_state(obj)
        return state.status if state else None

    def get_user_status_display(self, obj) -> str | None:
        state = _first_user_state(obj)
        return state.get_status_display() if state else None

    def get_user_rating(self, obj) -> int | None:
        state = _first_user_state(obj)
        return state.rating if state else None

    def get_progress_label(self, obj) -> str | None:
        progress = _first_user_progress(obj)
        if progress and progress.current_season_number and progress.current_episode_number:
            return f"S{progress.current_season_number:02d}E{progress.current_episode_number:02d}"
        return None


class EpisodeSerializer(serializers.ModelSerializer):
    watched = serializers.SerializerMethodField()

    class Meta:
        model = Episode
        fields = ("id", "number", "name", "duration_min", "air_date", "watched")

    def get_watched(self, obj) -> bool:
        watched_ids = self.context.get("watched_episode_ids", set())
        return obj.id in watched_ids


class SeasonSerializer(serializers.ModelSerializer):
    episodes = EpisodeSerializer(many=True, read_only=True)

    class Meta:
        model = Season
        fields = ("id", "number", "episodes_count", "episodes")


class UserTitleStateSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = UserTitleState
        fields = ("status", "status_display", "rating", "review", "started_at", "finished_at", "updated_at")


class TitleDetailSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    seasons = SeasonSerializer(many=True, read_only=True)
    user_state = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    total_episodes = serializers.IntegerField(read_only=True)
    watched_episodes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "original_name",
            "year",
            "category",
            "category_display",
            "is_series",
            "poster_url",
            "cover_url",
            "kp_url",
            "imdb_id",
            "duration_min",
            "rating_kp",
            "rating_imdb",
            "genres",
            "countries",
            "age_limit",
            "slogan",
            "description",
            "short_description",
            "start_year",
            "end_year",
            "seasons",
            "user_state",
            "progress",
            "total_episodes",
            "watched_episodes",
        )

    def get_user_state(self, obj):
        state = self.context.get("user_state")
        return UserTitleStateSerializer(state).data if state else None

    def get_progress(self, obj):
        progress = self.context.get("progress")
        if not progress:
            return None
        return {
            "current_season_number": progress.current_season_number,
            "current_episode_number": progress.current_episode_number,
            "last_watched_at": progress.last_watched_at,
        }


# ---- Входные сериализаторы (валидация запросов) ----


class AddTitleSerializer(serializers.Serializer):
    source_id = serializers.IntegerField(min_value=1)


class UpdateStateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=WatchStatus.choices)
    rating = serializers.IntegerField(min_value=0, max_value=10, required=False, allow_null=True)
    review = serializers.CharField(required=False, allow_blank=True, default="")
    started_at = serializers.DateField(required=False, allow_null=True)
    finished_at = serializers.DateField(required=False, allow_null=True)


class ToggleEpisodeSerializer(serializers.Serializer):
    episode_id = serializers.IntegerField(min_value=1)
    watched = serializers.BooleanField()


class TablePreferencesSerializer(serializers.Serializer):
    visible_columns = serializers.ListField(child=serializers.CharField(), required=False)
    page_size = serializers.IntegerField(min_value=10, max_value=500, required=False)
    view_mode = serializers.ChoiceField(choices=["table", "grid"], required=False)
