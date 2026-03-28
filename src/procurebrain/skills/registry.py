from collections.abc import Iterable

from procurebrain.skills.models import SkillDefinition


class SkillRegistry:
    def __init__(self, skills: Iterable[SkillDefinition]):
        self._skills = {skill.metadata.name: skill for skill in skills}

    def list_all(self) -> list[SkillDefinition]:
        return sorted(self._skills.values(), key=lambda item: item.metadata.priority)

    def by_agent(self, agent_name: str) -> list[SkillDefinition]:
        return [
            skill
            for skill in self.list_all()
            if agent_name in skill.metadata.compatible_agents and skill.metadata.enabled
        ]

    def get(self, skill_name: str) -> SkillDefinition | None:
        return self._skills.get(skill_name)
