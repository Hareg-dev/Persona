from pathlib import Path

from procurebrain.domain.sources.entities import SourceRecord


class SourceDomainService:
    def create_web_source(
        self,
        url: str,
        title: str,
        content: str,
        chat_id: str | None = None,
        metadata: dict | None = None,
    ) -> SourceRecord:
        return SourceRecord(
            source_type="url",
            title=title.strip(),
            content=content.strip(),
            uri=url,
            chat_id=chat_id,
            metadata=metadata or {},
        )

    def create_pdf_source(
        self,
        file_path: str,
        title: str,
        content: str,
        chat_id: str | None = None,
        metadata: dict | None = None,
    ) -> SourceRecord:
        return SourceRecord(
            source_type="pdf",
            title=title.strip() or Path(file_path).name,
            content=content.strip(),
            uri=file_path,
            chat_id=chat_id,
            metadata=metadata or {},
        )
