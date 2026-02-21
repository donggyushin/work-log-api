from src.domain.entities.chat import ChatMessage, ChatSession
from src.domain.interfaces.ai_chat_bot import AIChatBot


# 구현 필요
class AnthropicAIChatBot(AIChatBot):
    async def send(self, chat: ChatSession) -> ChatMessage:
        return await super().send(chat)
