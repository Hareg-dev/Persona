from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from procurebrain.application.services.model_router import ModelRouter
from procurebrain.domain.chat.entities import ChatMessage
from procurebrain.skills.service import SkillService


class ChatOrchestrator:
    def __init__(
        self,
        model_router: ModelRouter,
        skill_service: SkillService,
    ) -> None:
        self.model_router = model_router
        self.skill_service = skill_service

    async def generate_assistant_reply(
        self,
        history: list[ChatMessage],
        provider: str | None = None,
        model: str | None = None,
    ) -> tuple[str, str, str]:
        selection = self.model_router.resolve(provider=provider, model=model)
        chat_model = self.model_router.build_chat_model(
            provider=selection.provider,
            model=selection.model,
        )
        prompt_messages = [SystemMessage(content=self.skill_service.build_agent_prompt("supervisor"))]
        prompt_messages.extend(self._history_to_langchain_messages(history))

        response = await chat_model.ainvoke(prompt_messages)
        content = self._normalize_content(response.content)
        return content, selection.provider, selection.model

    def _history_to_langchain_messages(self, history: list[ChatMessage]) -> list:
        messages = []
        for item in history:
            if item.role == "system":
                messages.append(SystemMessage(content=item.content))
            elif item.role == "assistant":
                messages.append(AIMessage(content=item.content))
            else:
                messages.append(HumanMessage(content=item.content))
        return messages

    def _normalize_content(self, content: str | list) -> str:
        if isinstance(content, str):
            return content.strip()
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
        return "\n".join(part.strip() for part in parts if part).strip()
