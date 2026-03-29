from dataclasses import dataclass
import json
import re

from procurebrain.application.services.model_router import ModelRouter
from procurebrain.application.services.knowledge_graph_service import KnowledgeRelation


@dataclass(slots=True)
class ExtractedEntity:
    name: str
    category: str
    note: str | None = None


@dataclass(slots=True)
class StructuredAnalysis:
    sections: dict[str, list[str]]
    entities: list[ExtractedEntity]
    relations: list[KnowledgeRelation]


class AnalysisStructuringService:
    def __init__(self, model_router: ModelRouter | None = None) -> None:
        self.model_router = model_router

    section_aliases = {
        "findings": "Findings",
        "risks": "Risks",
        "opportunities": "Opportunities",
        "recommendations": "Recommendations",
        "market": "Market",
        "technology": "Technology",
    }

    def structure(self, text: str, root_query: str) -> StructuredAnalysis:
        sections = self._parse_sections(text)
        entities = self._extract_entities(sections)
        relations = self._build_relations(root_query=root_query, entities=entities, sections=sections)
        return StructuredAnalysis(sections=sections, entities=entities, relations=relations)

    async def structure_with_llm(
        self,
        text: str,
        root_query: str,
        provider: str | None = None,
        model: str | None = None,
    ) -> StructuredAnalysis:
        if self.model_router is None:
            return self.structure(text=text, root_query=root_query)

        prompt = (
            "Extract structured research analysis as JSON with keys "
            "`sections`, `entities`, and `relations`.\n"
            "sections should be an object of arrays.\n"
            "entities should be objects with name, category, note.\n"
            "relations should be objects with source, relation, target, evidence.\n"
            f"Root query: {root_query}\n\n"
            f"Analysis text:\n{text}"
        )
        try:
            chat_model = self.model_router.build_chat_model(provider=provider, model=model)
            response = await chat_model.ainvoke(prompt)
            payload = self._extract_json(response.content if hasattr(response, "content") else response)
            sections = {
                str(key): [str(item) for item in value]
                for key, value in payload.get("sections", {}).items()
                if isinstance(value, list)
            }
            entities = [
                ExtractedEntity(
                    name=str(item.get("name", "")),
                    category=str(item.get("category", "Analysis")),
                    note=item.get("note"),
                )
                for item in payload.get("entities", [])
                if item.get("name")
            ]
            relations = [
                KnowledgeRelation(
                    source=str(item.get("source", root_query)),
                    relation=str(item.get("relation", "related_to")),
                    target=str(item.get("target", "")),
                    evidence=item.get("evidence"),
                )
                for item in payload.get("relations", [])
                if item.get("target")
            ]
            if sections or entities or relations:
                return StructuredAnalysis(
                    sections=sections or self._parse_sections(text),
                    entities=entities,
                    relations=relations,
                )
        except Exception:  # noqa: BLE001
            pass
        return self.structure(text=text, root_query=root_query)

    def _extract_json(self, content: object) -> dict:
        raw = content if isinstance(content, str) else str(content)
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1:
            return {}
        return json.loads(raw[start : end + 1])

    def _parse_sections(self, text: str) -> dict[str, list[str]]:
        sections: dict[str, list[str]] = {}
        current = "Analysis"
        sections[current] = []
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            maybe_section = self._normalize_section_header(line)
            if maybe_section:
                current = maybe_section
                sections.setdefault(current, [])
                continue
            if line.startswith("-") or line.startswith("*"):
                sections.setdefault(current, []).append(line[1:].strip())
            else:
                sections.setdefault(current, []).append(line)
        return sections

    def _normalize_section_header(self, line: str) -> str | None:
        cleaned = line.strip(":").strip().lower()
        cleaned = re.sub(r"[^a-z ]", "", cleaned)
        return self.section_aliases.get(cleaned)

    def _extract_entities(self, sections: dict[str, list[str]]) -> list[ExtractedEntity]:
        entities: list[ExtractedEntity] = []
        seen: set[tuple[str, str]] = set()
        for category, items in sections.items():
            for item in items:
                candidates = re.findall(r"\b[A-Z][a-zA-Z0-9\-]{2,}\b", item)
                for candidate in candidates[:4]:
                    key = (candidate, category)
                    if key in seen:
                        continue
                    seen.add(key)
                    entities.append(ExtractedEntity(name=candidate, category=category, note=item))
        return entities

    def _build_relations(
        self,
        root_query: str,
        entities: list[ExtractedEntity],
        sections: dict[str, list[str]],
    ) -> list[KnowledgeRelation]:
        relations: list[KnowledgeRelation] = []
        for entity in entities:
            relations.append(
                KnowledgeRelation(
                    source=root_query,
                    relation=f"has_{entity.category.lower()}",
                    target=entity.name,
                    evidence=entity.note,
                )
            )
        for section, items in sections.items():
            for item in items[:5]:
                relations.append(
                    KnowledgeRelation(
                        source=section,
                        relation="contains",
                        target=item[:80],
                        evidence=item,
                    )
                )
        return relations
