from urllib.parse import urlparse


class WebNormalizer:
    def normalize_metadata(self, url: str) -> dict:
        parsed = urlparse(url)
        return {
            "domain": parsed.netloc,
            "scheme": parsed.scheme,
            "path": parsed.path,
        }
