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

    def save_optional_pdf(self, output_dir: str, filename: str, content: str) -> Path | None:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except Exception:  # noqa: BLE001
            return None

        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        target = path / filename
        pdf = canvas.Canvas(str(target), pagesize=A4)
        width, height = A4
        cursor_y = height - 50
        for raw_line in content.splitlines() or [content]:
            line = raw_line.strip() or " "
            pdf.drawString(40, cursor_y, line[:110])
            cursor_y -= 16
            if cursor_y < 40:
                pdf.showPage()
                cursor_y = height - 50
        pdf.save()
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
        target = path / filename
        try:
            figure = px.bar(x=labels, y=values, title=title)
            figure.write_html(str(target))
        except Exception:  # noqa: BLE001
            rows = "\n".join(
                f"<tr><td>{label}</td><td>{value}</td></tr>"
                for label, value in zip(labels, values, strict=False)
            )
            target.write_text(
                (
                    "<html><head><meta charset='utf-8'><title>{title}</title></head><body>"
                    f"<h1>{title}</h1><table border='1' cellspacing='0' cellpadding='6'>"
                    "<tr><th>Label</th><th>Value</th></tr>"
                    f"{rows}</table></body></html>"
                ),
                encoding="utf-8",
            )
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
        target = path / filename
        try:
            figure = px.bar(x=labels, y=values, title=title)
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
