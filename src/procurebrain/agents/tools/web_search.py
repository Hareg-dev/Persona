from duckduckgo_search import DDGS


class WebSearchTool:
    def search(self, query: str, max_results: int = 5) -> list[dict]:
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
