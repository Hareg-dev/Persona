from dataclasses import dataclass

import networkx as nx


@dataclass(slots=True)
class KnowledgeRelation:
    source: str
    relation: str
    target: str
    evidence: str | None = None


class KnowledgeGraphService:
    def __init__(self) -> None:
        self.graph = nx.DiGraph()

    def add_relations(self, relations: list[KnowledgeRelation]) -> None:
        for item in relations:
            self.graph.add_node(item.source)
            self.graph.add_node(item.target)
            self.graph.add_edge(
                item.source,
                item.target,
                relation=item.relation,
                evidence=item.evidence,
            )

    def export_adjacency(self) -> dict[str, list[str]]:
        return {node: list(self.graph.successors(node)) for node in self.graph.nodes}

    def export_edges(self) -> list[dict]:
        return [
            {
                "source": source,
                "target": target,
                "relation": data.get("relation"),
                "evidence": data.get("evidence"),
            }
            for source, target, data in self.graph.edges(data=True)
        ]
