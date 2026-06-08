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

    @classmethod
    def default(cls) -> BaseProvider:
        """Возвращает провайдер по умолчанию из настроек (settings.DEFAULT_PROVIDER)."""
        return cls.init_provider(settings.DEFAULT_PROVIDER)
