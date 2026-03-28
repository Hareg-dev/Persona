import json
from pathlib import Path

from procurebrain.skills.models import SkillDefinition, SkillMetadata


def _skills_root() -> Path:
    return Path(__file__).resolve().parents[3] / "skills"


def _read_optional(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_skill_definition(skill_name: str) -> SkillDefinition:
    root = _skills_root() / skill_name
    metadata = SkillMetadata(**json.loads((root / "skill.json").read_text(encoding="utf-8")))
    return SkillDefinition(
        metadata=metadata,
        root_path=root,
        system_text=(root / "SYSTEM.md").read_text(encoding="utf-8"),
        inputs_text=_read_optional(root / "INPUTS.md"),
        outputs_text=_read_optional(root / "OUTPUTS.md"),
        examples_text=_read_optional(root / "EXAMPLES.md"),
    )


def load_skill_text(skill_name: str) -> str:
    return load_skill_definition(skill_name).system_text


def discover_skills() -> list[SkillDefinition]:
    skills_root = _skills_root()
    discovered: list[SkillDefinition] = []
    for path in skills_root.iterdir():
        if not path.is_dir() or path.name.startswith("_"):
            continue
        if (path / "skill.json").exists() and (path / "SYSTEM.md").exists():
            discovered.append(load_skill_definition(path.name))
    return sorted(discovered, key=lambda item: item.metadata.priority)


def compose_skill_prompt(skill: SkillDefinition) -> str:
    sections = [skill.system_text.strip()]
    if skill.inputs_text:
        sections.append(skill.inputs_text.strip())
    if skill.outputs_text:
        sections.append(skill.outputs_text.strip())
    if skill.examples_text:
        sections.append(skill.examples_text.strip())
    return "\n\n".join(section for section in sections if section)
