from bs4 import BeautifulSoup
import trafilatura


class WebExtractor:
    def extract(self, html: str, url: str | None = None) -> tuple[str, str]:
        extracted = trafilatura.extract(
            html,
            url=url,
            include_comments=False,
            include_links=False,
        )
        title = self._extract_title(html)
        content = extracted or self._fallback_extract(html)
        return title, content.strip()

    def _extract_title(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        return "Untitled page"

    def _fallback_extract(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)
