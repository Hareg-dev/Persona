from pathlib import Path


class PdfLoader:
    def read_bytes(self, file_path: str) -> bytes:
        return Path(file_path).read_bytes()
