from pathlib import Path

import plotly.express as px

from procurebrain.application.services.tts_adapter import TtsAdapter, TtsRequest


class MediaOutputService:
    def __init__(self, tts_adapter: TtsAdapter | None = None) -> None:
        self.tts_adapter = tts_adapter or TtsAdapter()

    def save_markdown(self, output_dir: str, filename: str, content: str) -> Path:
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        target = path / filename
        target.write_text(content, encoding="utf-8")
        return target

    def save_mermaid(self, output_dir: str, filename: str, content: str) -> Path:
        return self.save_markdown(output_dir=output_dir, filename=filename, content=content)

    def save_bar_chart(
        self,
        output_dir: str,
        filename: str,
        labels: list[str],
        values: list[float],
        title: str,
    ) -> Path:
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        figure = px.bar(x=labels, y=values, title=title)
        target = path / filename
        figure.write_html(str(target))
        return target

    def save_optional_chart_image(
        self,
        output_dir: str,
        filename: str,
        labels: list[str],
        values: list[float],
        title: str,
    ) -> Path | None:
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        figure = px.bar(x=labels, y=values, title=title)
        target = path / filename
        try:
            figure.write_image(str(target))
            return target
        except Exception:  # noqa: BLE001
            return None

    def build_tts_script(self, text: str, language: str, tone: str) -> dict:
        return {
            "language": language,
            "tone": tone,
            "text": text,
        }

    def save_tts_request(
        self,
        output_dir: str,
        filename: str,
        text: str,
        language: str,
        tone: str,
        voice: str = "default",
    ) -> Path:
        return self.tts_adapter.save_request(
            output_dir=output_dir,
            filename=filename,
            request=TtsRequest(text=text, language=language, tone=tone, voice=voice),
        )

    def save_optional_audio(
        self,
        output_dir: str,
        filename: str,
        text: str,
        language: str,
        tone: str,
        voice: str = "default",
    ) -> Path | None:
        try:
            import pyttsx3  # type: ignore

            path = Path(output_dir)
            path.mkdir(parents=True, exist_ok=True)
            target = path / filename
            engine = pyttsx3.init()
            engine.save_to_file(text, str(target))
            engine.runAndWait()
            return target
        except Exception:  # noqa: BLE001
            return None
