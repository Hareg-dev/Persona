from io import BytesIO

from pypdf import PdfReader


class PdfParser:
    def parse(self, payload: bytes) -> tuple[str, dict]:
        reader = PdfReader(BytesIO(payload))
        pages = [page.extract_text() or "" for page in reader.pages]
        metadata = {
            "page_count": len(reader.pages),
            "title": getattr(reader.metadata, "title", None) if reader.metadata else None,
        }
        return "\n\n".join(page.strip() for page in pages if page.strip()), metadata
