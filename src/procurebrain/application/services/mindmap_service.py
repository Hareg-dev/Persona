class MindmapService:
    def build_branches_from_sections(self, sections: dict[str, list[str]], limit_per_section: int = 5) -> dict[str, list[str]]:
        return {
            section: [item[:120] for item in items[:limit_per_section]]
            for section, items in sections.items()
            if items
        }

    def build_markdown_mindmap(self, root: str, branches: dict[str, list[str]]) -> str:
        lines = [f"# {root}"]
        for branch, children in branches.items():
            lines.append(f"## {branch}")
            for child in children:
                lines.append(f"- {child}")
        return "\n".join(lines)

    def build_mermaid_mindmap(self, root: str, branches: dict[str, list[str]]) -> str:
        lines = ["mindmap", f"  root(({root}))"]
        for branch, children in branches.items():
            lines.append(f"    {branch}")
            for child in children:
                lines.append(f"      {child}")
        return "\n".join(lines)
