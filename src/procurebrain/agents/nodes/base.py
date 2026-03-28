from langchain_core.messages import HumanMessage, SystemMessage

from procurebrain.application.services.model_router import ModelRouter
from procurebrain.skills.service import SkillService


class BaseAgentNode:
    def __init__(self, model_router: ModelRouter, skill_service: SkillService) -> None:
        self.model_router = model_router
        self.skill_service = skill_service

    async def run_prompt(
        self,
        node_name: str,
        user_prompt: str,
        provider: str | None = None,
        model: str | None = None,
    ) -> str:
        chat_model = self.model_router.build_chat_model(provider=provider, model=model)
        system_prompt = self.skill_service.build_node_prompt(node_name)
        response = await chat_model.ainvoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )
        content = response.content
        if isinstance(content, str):
            return content.strip()
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
        return "\n".join(part.strip() for part in parts if part).strip()
