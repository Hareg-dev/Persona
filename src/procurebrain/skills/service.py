from procurebrain.skills.composer import compose_agent_prompt
from procurebrain.skills.loader import discover_skills
from procurebrain.skills.registry import SkillRegistry


class SkillService:
    def __init__(self) -> None:
        self.registry = SkillRegistry(discover_skills())

    def list_skills(self) -> list[str]:
        return [skill.metadata.name for skill in self.registry.list_all()]

    def build_agent_prompt(self, agent_name: str) -> str:
        return compose_agent_prompt(agent_name, self.registry.by_agent(agent_name))
