from procurebrain.skills.models import SkillDefinition


def compose_agent_prompt(agent_name: str, skills: list[SkillDefinition]) -> str:
    relevant = [
        skill for skill in skills if agent_name in skill.metadata.compatible_agents and skill.metadata.enabled
    ]
    ordered = sorted(relevant, key=lambda item: item.metadata.priority)

    sections: list[str] = []
    for skill in ordered:
        sections.append(f"# Skill: {skill.metadata.name}")
        sections.append(skill.system_text.strip())
        if skill.inputs_text:
            sections.append(skill.inputs_text.strip())
        if skill.outputs_text:
            sections.append(skill.outputs_text.strip())
        if skill.examples_text:
            sections.append(skill.examples_text.strip())

    return "\n\n".join(section for section in sections if section)
