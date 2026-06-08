from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    # auth
    path("me/", views.MeView.as_view(), name="me"),
    path("auth/login/", views.login_view, name="login"),
    path("auth/logout/", views.logout_view, name="logout"),
    path("auth/signup/", views.signup_view, name="signup"),
    # stats
    path("stats/", views.stats_view, name="stats"),
    # search (внешний провайдер)
    path("search/", views.search_view, name="search"),
    # table preferences
    path("preferences/", views.PreferencesView.as_view(), name="preferences"),
    # titles
    path("titles/", views.titles_list_view, name="titles-list"),
    path("titles/add/", views.add_title_view, name="titles-add"),
    path("titles/<int:pk>/", views.title_detail_view, name="title-detail"),
    path("titles/<int:pk>/state/", views.update_state_view, name="title-state"),
    path("titles/<int:pk>/toggle-episode/", views.toggle_episode_view, name="title-toggle-episode"),
    path("titles/<int:pk>/remove/", views.remove_title_view, name="title-remove"),
]
