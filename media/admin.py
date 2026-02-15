from django.contrib import admin

from media.models import (
    Title,
    Franchise,
    FranchiseItem,
    Season,
    Episode,
    UserTitleState,
    UserProgress,
)

admin.site.register(
    [
        Title,
        Franchise,
        FranchiseItem,
        Season,
        Episode,
        UserTitleState,
        UserProgress,
    ]
)
