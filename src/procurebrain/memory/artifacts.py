from datetime import datetime, timezone
import json
from pathlib import Path
import re


class ArtifactStore:
    def __init__(self, root_dir: str = "./data/artifacts") -> None:
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def save_source(
        self,
        source_id: str,
        title: str,
        content: str,
        chat_id: str | None = None,
        metadata: dict | None = None,
    ) -> Path:
        folder = self._resolve_folder(chat_id=chat_id, kind="sources")
        slug = self._slugify(title)
        timestamp = self._timestamp()
        markdown_path = folder / f"{timestamp}_{slug}_{source_id}.md"
        json_path = folder / f"{timestamp}_{slug}_{source_id}.json"
        markdown_path.write_text(f"# {title}\n\n{content}\n", encoding="utf-8")
        json_path.write_text(json.dumps(metadata or {}, indent=2), encoding="utf-8")
        return markdown_path

    def save_message(
        self,
        chat_id: str,
        role: str,
        content: str,
        message_id: str,
        metadata: dict | None = None,
    ) -> Path:
        folder = self._resolve_folder(chat_id=chat_id, kind="messages")
        timestamp = self._timestamp()
        markdown_path = folder / f"{timestamp}_{role}_{message_id}.md"
        json_path = folder / f"{timestamp}_{role}_{message_id}.json"
        markdown_path.write_text(f"# {role}\n\n{content}\n", encoding="utf-8")
        json_path.write_text(json.dumps(metadata or {}, indent=2), encoding="utf-8")
        return markdown_path

    def _resolve_folder(self, chat_id: str | None, kind: str) -> Path:
        scope = chat_id or "global"
        folder = self.root / scope / kind
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    def _slugify(self, value: str) -> str:
        normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
        return normalized or "artifact"
