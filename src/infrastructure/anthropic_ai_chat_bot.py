from src.domain.entities.chat import ChatMessage, ChatSession
from src.domain.interfaces.ai_chat_bot import AIChatBot


class AnthropicAIChatBot(AIChatBot):
    async def send(self, chat: ChatSession) -> ChatMessage:
        return await super().send(chat)
