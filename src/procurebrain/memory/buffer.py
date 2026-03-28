from procurebrain.domain.chat.entities import ChatMessage


class LangChainBufferMemoryService:
    """Short-term conversation memory compatible with a LangChain-style buffer concept."""

    def build_transcript(self, history: list[ChatMessage], max_messages: int = 20) -> str:
        selected = history[-max_messages:]
        lines: list[str] = []
        for item in selected:
            lines.append(f"{item.role.upper()}: {item.content}")
        return "\n".join(lines).strip()
