from typing import Callable

from django.conf import settings

from media.services.providers import (
    KinopoiskClient,
    KinopoiskProvider,
)
from media.services.providers.base import BaseProvider

ProviderBuilder = Callable[[], BaseProvider]


class ProviderFactory:
    _registry: dict[str, ProviderBuilder] = {
        "kinopoisk": lambda: KinopoiskProvider(client=KinopoiskClient(api_key=settings.PROVIDER_API_KEY)),
    }

    @classmethod
    def init_provider(cls, slug: str) -> BaseProvider:
        try:
            return cls._registry[slug]()
        except KeyError:
            raise ValueError(f"Unknown provider slug: {slug}")
