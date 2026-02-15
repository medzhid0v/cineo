class KinopoiskError(RuntimeError):
    """Базовая ошибка интеграции с Kinopoisk API."""


class KinopoiskAuthError(KinopoiskError):
    """Нет API-ключа или ошибка авторизации."""


class KinopoiskHTTPError(KinopoiskError):
    """HTTP-ошибка при запросе к API."""


class KinopoiskParseError(KinopoiskError):
    """Неожиданный формат ответа API."""
