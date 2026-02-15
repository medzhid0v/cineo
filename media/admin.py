from django.contrib import admin

from media.models import (
    Title,
)

admin.site.register(
    [
        Title,
    ]
)