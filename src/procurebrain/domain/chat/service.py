from procurebrain.domain.chat.entities import ChatMessage, ChatSession


class ChatDomainService:
    def create_session(self, title: str, user_id: str | None = None) -> ChatSession:
        return ChatSession(title=title.strip(), user_id=user_id)

    def create_message(
        self,
        chat_id: str,
        content: str,
        role: str = "user",
        provider: str | None = None,
        model: str | None = None,
    ) -> ChatMessage:
        return ChatMessage(
            chat_id=chat_id,
            role=role,
            content=content.strip(),
            provider=provider,
            model=model,
        )
