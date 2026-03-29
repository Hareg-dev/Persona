import httpx

from procurebrain.application.services.cache import TTLCacheService
from procurebrain.config.settings import settings
from procurebrain.core.exceptions import FetchError
from procurebrain.core.retry import retry_async


class WebFetcher:
    def __init__(self, cache: TTLCacheService[str] | None = None) -> None:
        self.cache = cache or TTLCacheService[str](ttl_seconds=settings.cache_ttl_seconds)

    async def fetch_text(self, url: str, timeout: float = 20.0) -> str:
        cache_key = f"fetch::{url}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        async def _run() -> str:
            async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text

        try:
            result = await retry_async(_run, retries=3, base_delay=0.5)
            self.cache.set(cache_key, result)
            return result
        except Exception as exc:  # noqa: BLE001
            raise FetchError(f"Failed to fetch '{url}': {exc}") from exc
