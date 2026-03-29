from duckduckgo_search import DDGS

from procurebrain.application.services.cache import TTLCacheService
from procurebrain.config.settings import settings
from procurebrain.core.exceptions import SearchError
from procurebrain.core.retry import retry_sync


class WebSearchTool:
    def __init__(self, cache: TTLCacheService[list[dict]] | None = None) -> None:
        self.cache = cache or TTLCacheService[list[dict]](ttl_seconds=settings.cache_ttl_seconds)

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        cache_key = f"search::{query}::{max_results}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        def _run() -> list[dict]:
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=max_results)
                return [
                    {
                        "title": item.get("title", ""),
                        "url": item.get("href", ""),
                        "snippet": item.get("body", ""),
                    }
                    for item in results
                    if item.get("href")
                ]

        try:
            results = retry_sync(_run, retries=3, base_delay=0.4)
            self.cache.set(cache_key, results)
            return results
        except Exception as exc:  # noqa: BLE001
            raise SearchError(f"Search failed for query '{query}': {exc}") from exc
