class TextChunker:
    def chunk(self, text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
        cleaned = text.strip()
        if not cleaned:
            return []

        chunks: list[str] = []
        start = 0
        while start < len(cleaned):
            end = min(start + chunk_size, len(cleaned))
            chunks.append(cleaned[start:end])
            if end == len(cleaned):
                break
            start = max(end - overlap, 0)
        return chunks
