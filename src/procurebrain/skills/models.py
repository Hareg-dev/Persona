from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SkillMetadata:
    name: str
    version: str
    description: str
    tags: list[str]
    compatible_agents: list[str]
    allowed_tools: list[str]
    priority: int
    enabled: bool


@dataclass(slots=True)
class SkillDefinition:
    metadata: SkillMetadata
    root_path: Path
    system_text: str
    inputs_text: str = ""
    outputs_text: str = ""
    examples_text: str = ""
