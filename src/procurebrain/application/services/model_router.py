from dataclasses import dataclass
from typing import Any

from procurebrain.config.settings import settings
from procurebrain.core.exceptions import ModelProviderError


@dataclass(slots=True)
class ModelSelection:
    provider: str
    model: str


class ModelRouter:
    def resolve_for_runtime_choice(
        self,
        choice: str | None = None,
        model: str | None = None,
    ) -> ModelSelection:
        normalized = (choice or "auto_best").lower()
        if normalized != "auto_best":
            return self.resolve(provider=normalized, model=model)

        for provider in self._runtime_priority():
            if self._is_provider_configured(provider):
                return self.resolve(provider=provider, model=model)
        return self.resolve(provider=settings.default_model_provider, model=model)

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
            try:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(model=selection.model, api_key=settings.openai_api_key)
            except Exception as exc:  # noqa: BLE001
                raise ModelProviderError(f"OpenAI model setup failed: {exc}") from exc

        if selection.provider in {"google", "gemini"}:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                return ChatGoogleGenerativeAI(
                    model=selection.model,
                    google_api_key=settings.google_api_key,
                )
            except Exception as exc:  # noqa: BLE001
                raise ModelProviderError(f"Gemini model setup failed: {exc}") from exc

        if selection.provider == "groq":
            try:
                from langchain_groq import ChatGroq
                return ChatGroq(model=selection.model, api_key=settings.groq_api_key)
            except Exception as exc:  # noqa: BLE001
                raise ModelProviderError(f"Groq model setup failed: {exc}") from exc

        raise ValueError(f"Unsupported model provider: {selection.provider}")

    def build_embedding_model(self, provider: str | None = None, model: str | None = None) -> Any:
        selection = self.resolve(provider=provider, model=model)

        if selection.provider == "openai":
            try:
                from langchain_openai import OpenAIEmbeddings
                return OpenAIEmbeddings(
                    model=model or settings.embedding_model_name,
                    api_key=settings.openai_api_key,
                )
            except Exception as exc:  # noqa: BLE001
                raise ModelProviderError(f"OpenAI embeddings setup failed: {exc}") from exc

        raise ValueError(
            "Embedding model support is currently implemented for the OpenAI provider only."
        )

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

    def _runtime_priority(self) -> list[str]:
        return ["gemini", "openai", "groq"]

    def _is_provider_configured(self, provider: str) -> bool:
        if provider == "openai":
            return bool(settings.openai_api_key)
        if provider in {"google", "gemini"}:
            return bool(settings.google_api_key)
        if provider == "groq":
            return bool(settings.groq_api_key)
        return False

    def provider_status(self) -> dict[str, dict[str, str | bool]]:
        return {
            "openai": {
                "configured": bool(settings.openai_api_key),
                "default_model": settings.openai_model_name,
            },
            "gemini": {
                "configured": bool(settings.google_api_key),
                "default_model": settings.gemini_model_name,
            },
            "groq": {
                "configured": bool(settings.groq_api_key),
                "default_model": settings.groq_model_name,
            },
            "embedding": {
                "configured": settings.embedding_provider == "openai" and bool(settings.openai_api_key),
                "default_model": settings.embedding_model_name,
            },
        }
