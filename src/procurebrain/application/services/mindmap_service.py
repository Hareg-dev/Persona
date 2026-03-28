class MindmapService:
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
