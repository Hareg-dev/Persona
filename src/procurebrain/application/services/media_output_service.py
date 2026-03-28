from pathlib import Path

import plotly.express as px


class MediaOutputService:
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

    def build_tts_script(self, text: str, language: str, tone: str) -> dict:
        return {
            "language": language,
            "tone": tone,
            "text": text,
        }
