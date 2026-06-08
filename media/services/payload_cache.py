import hashlib
from typing import Any

from media.models import PayloadKind, ProviderPayload

# external_id для поисковых записей вычисляется из хэша запроса
# (search-ответы не привязаны к конкретному внешнему ID).
_SEARCH_HASH_BITS = 7  # 28 бит — безопасно влезает в PositiveIntegerField


def _query_to_id(query: str) -> int:
    digest = hashlib.sha1(query.strip().lower().encode("utf-8")).hexdigest()
    return int(digest[:_SEARCH_HASH_BITS], 16)


def get_payload(provider: str, external_id: int, kind: str) -> dict[str, Any] | None:
    """Возвращает закэшированный сырой ответ или None."""
    row = ProviderPayload.objects.filter(
        provider=provider,
        external_id=external_id,
        kind=kind,
    ).first()
    return row.payload if row else None


def store_payload(provider: str, external_id: int, kind: str, payload: dict[str, Any]) -> None:
    """Сохраняет/обновляет сырой ответ в кэше."""
    ProviderPayload.objects.update_or_create(
        provider=provider,
        external_id=external_id,
        kind=kind,
        defaults={"payload": payload},
    )


def get_search_payload(provider: str, query: str) -> dict[str, Any] | None:
    return get_payload(provider, _query_to_id(query), PayloadKind.SEARCH)


def store_search_payload(provider: str, query: str, payload: dict[str, Any]) -> None:
    ProviderPayload.objects.update_or_create(
        provider=provider,
        external_id=_query_to_id(query),
        kind=PayloadKind.SEARCH,
        defaults={"payload": payload, "query": query.strip()},
    )
