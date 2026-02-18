from django.contrib import admin

from media.models import (
    Episode,
    Franchise,
    FranchiseItem,
    Season,
    Title,
    UserEpisodeState,
    UserProgress,
    UserTitleState,
)


class SeasonInline(admin.TabularInline):
    model = Season
    extra = 0


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "year", "kp_id", "created_at")
    list_filter = ("category", "year", "created_at")
    search_fields = ("name", "kp_id")
    ordering = ("-created_at",)
    inlines = [SeasonInline]


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("title", "number", "episodes_count")
    list_filter = ("number",)
    search_fields = ("title__name",)


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("season", "number", "name", "duration_min", "air_date")
    list_filter = ("air_date",)
    search_fields = ("name", "season__title__name")


@admin.register(UserTitleState)
class UserTitleStateAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "status", "rating", "updated_at")
    list_filter = ("status", "updated_at")
    search_fields = ("user__username", "title__name")


@admin.register(UserEpisodeState)
class UserEpisodeStateAdmin(admin.ModelAdmin):
    list_display = ("user", "episode", "watched", "watched_at")
    list_filter = ("watched",)
    search_fields = ("user__username", "episode__name", "episode__season__title__name")


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "title",
        "current_season_number",
        "current_episode_number",
        "last_watched_at",
    )
    search_fields = ("user__username", "title__name")


admin.site.register(Franchise)
admin.site.register(FranchiseItem)
