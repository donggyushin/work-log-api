import os
from datetime import datetime

from anthropic import AsyncAnthropic
from anthropic.types import MessageParam, TextBlock

from src.domain.entities.chat import ChatMessage, ChatSession, MessageRole
from src.domain.interfaces.ai_chat_bot import AIChatBot


class AnthropicAIChatBot(AIChatBot):
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"

    async def send(self, chat: ChatSession) -> ChatMessage:
        # ChatSession의 메시지를 Anthropic API 형식으로 변환
        system_messages: list[str] = []
        conversation_messages: list[MessageParam] = []

        for msg in chat.messages:
            if msg.role == MessageRole.system:
                system_messages.append(msg.content)
            elif msg.role == MessageRole.user:
                conversation_messages.append({"role": "user", "content": msg.content})
            elif msg.role == MessageRole.assistant:
                conversation_messages.append(
                    {"role": "assistant", "content": msg.content}
                )

        # system 메시지가 여러 개면 합치기
        system_prompt = "\n\n".join(system_messages)

        # Anthropic API 호출
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            system=system_prompt,
            messages=conversation_messages,
        )

        # 응답을 ChatMessage로 변환
        # user_id는 세션의 마지막 user 메시지에서 가져오기
        user_id = next(
            (
                msg.user_id
                for msg in reversed(chat.messages)
                if msg.role == MessageRole.user
            ),
            chat.messages[0].user_id if chat.messages else "",
        )

        # Anthropic 응답에서 텍스트 추출
        assistant_content = ""
        for item in response.content:
            if isinstance(item, TextBlock):
                assistant_content = item.text
                break

        return ChatMessage(
            id=response.id,
            user_id=user_id,
            role=MessageRole.assistant,
            content=assistant_content,
            created_at=datetime.now(),
        )
