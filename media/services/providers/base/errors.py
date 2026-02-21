class ProviderError(Exception):
    """Базовая ошибка источника."""


class TitleNotFound(ProviderError):
    """Тайтл не найден в этом источнике."""


class ProviderUnavailable(ProviderError):
    """Источник недоступен (таймаут, 5xx, бан, и т.п.)."""


class ProviderRateLimited(ProviderError):
    """Лимит запросов."""
