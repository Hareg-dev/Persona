from dataclasses import dataclass
from typing import Any

from procurebrain.config.settings import settings


@dataclass(slots=True)
class ModelSelection:
    provider: str
    model: str


class ModelRouter:
    def resolve(
        self,
        provider: str | None = None,
        model: str | None = None,
    ) -> ModelSelection:
        chosen_provider = (provider or settings.default_model_provider).lower()
        chosen_model = model or self._default_model_for_provider(chosen_provider)
        return ModelSelection(provider=chosen_provider, model=chosen_model)

    def build_chat_model(self, provider: str | None = None, model: str | None = None) -> Any:
        selection = self.resolve(provider=provider, model=model)

        if selection.provider == "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(model=selection.model, api_key=settings.openai_api_key)

        if selection.provider in {"google", "gemini"}:
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(
                model=selection.model,
                google_api_key=settings.google_api_key,
            )

        if selection.provider == "groq":
            from langchain_groq import ChatGroq

            return ChatGroq(model=selection.model, api_key=settings.groq_api_key)

        raise ValueError(f"Unsupported model provider: {selection.provider}")

    def _default_model_for_provider(self, provider: str) -> str:
        defaults = {
            "openai": settings.openai_model_name,
            "google": settings.gemini_model_name,
            "gemini": settings.gemini_model_name,
            "groq": settings.groq_model_name,
        }
        if provider not in defaults:
            raise ValueError(f"Unsupported model provider: {provider}")
        return defaults[provider]
