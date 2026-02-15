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

admin.site.register(
    [
        Title,
        Franchise,
        FranchiseItem,
        Season,
        Episode,
        UserTitleState,
        UserEpisodeState,
        UserProgress,
    ]
)
