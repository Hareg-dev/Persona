from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(slots=True)
class TtsRequest:
    text: str
    language: str
    tone: str
    voice: str = "default"


class TtsAdapter:
    """
    Foundation for future integration with tools like Coqui TTS.
    For now, this saves a machine-readable request artifact.
    """

    def save_request(self, output_dir: str, filename: str, request: TtsRequest) -> Path:
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        target = path / filename
        target.write_text(
            json.dumps(
                {
                    "text": request.text,
                    "language": request.language,
                    "tone": request.tone,
                    "voice": request.voice,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return target
