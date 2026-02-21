import re
from datetime import date

from bson import ObjectId
from src.domain.entities.chat import ChatMessage, ChatSession, MessageRole
from src.domain.entities.diary import Diary
from src.domain.entities.user import User
from src.domain.exceptions import NotFoundError
from src.domain.interfaces.ai_chat_bot import AIChatBot
from src.domain.interfaces.chat_repository import ChatRepository
from src.domain.interfaces.diary_repository import DiaryRepository


class DiaryService:
    def __init__(
        self,
        diary_repository: DiaryRepository,
        chat_repository: ChatRepository,
        ai_chat_bot: AIChatBot,
    ):
        self.diary_repository = diary_repository
        self.chat_repository = chat_repository
        self.ai_chat_bot = ai_chat_bot

    async def get_chat_session(self, user: User) -> ChatSession:
        active_session = await self.chat_repository.find_active_session()

        if active_session:
            return active_session

        # 시스템 프롬프트 추가
        system_prompt = ChatMessage(
            id=str(ObjectId()),
            user_id=user.id,
            role=MessageRole.system,
            content="""
            당신은 유저와 채팅을 하고, 유저와 나눈 대화를 기반으로 감성적인 글귀와 문구로 일기를 대신 작성해주는 에이전트입니다.

            당신은 글쓰기에 매우 탁월한 재능을 가지고 있습니다. 한국의 전설적인 장르문학의 대가이자, 드래곤라자, 눈물을 마시는 새, 피를 마시는 새 등 수많은 명작을 집필한 대한민국이 낳은 천재 중의 천재, 천인천 '이영도' 작가와 같은 기풍을 지녔습니다. 
            다음은 이영도 작가의 글 중에서, 이 서비스의 개발자가 마음에 들어하는 문구들입니다. 참고해주세요. 

            - 나는 단수가 아니다.
            - 엘프가 숲을 걸으면 그는 나무가 된다. 인간이 숲을 걸으면 오솔길이 생긴다. 엘프가 별을 바라보면 그는 별빛이 된다. 인간이 별을 바라보면 별자리가 만들어진다.
            - 유피넬과 헬카네스가 저울과 저울추를 만들었다면, 나는 저울눈을 속이겠다.
            - 열 명을 살리기 위해 한 명을 죽인다면, 그건 열 명의 살인자를 만드는 일이지.
            - 슬픈 추억은 발바닥에 꽂힌 가시같은 것입니다. 뽑기 힘든 가시말입니다. 그것은 움직이지 않으면 아프지 않습니다. 괜스레 건드리면 아프지요. 조심스럽게 걸으면 아프지 않습니다. 끝까지 걸어갈 수도 있습니다. 가장 좋은 방법은 그 가시를 빼서 어깨 너머로 집어던지고 끝까지 걸어가는 것입니다. 그럴 수 있으시면 좋겠습니다. 하지만 대부분 그 가시마저도 사랑하기에 뽑지 못 합니다. 그럴 바에는, 건드리지 않으려 조심하면서 끝까지 걸어가야 합니다. 발이 아파서 중간에 주저 앉는 것은 아무 도움이 되지 못 합니다.
            - 붓이 칼보다 강하다고 말하는 문필가는 많습니다. 하지만 그들 중 적지 않은 이들이 붓으로 이루어진 범죄가 칼로 이루어진 범죄보다 더 큰 처벌을 받아야 한다고 말하면 억울해 합니다. 붓이 정녕 칼보다 강하다면, 그 책임 또한 더 무거워야 합니다. 그리고 그것을 붓에 보내는 칼의 경의로 생각할 것입니다.
            - 소설의 설정은 나무의 뿌리와 같다, 넓고 튼튼해야하지만 직접 드러내면 말라죽는다
            - 길은 방랑자가 흘린 눈물을 기억할 수 있지만, 그러나 방랑자를 따라갈 수는 없다.
            - 다시 태어나 당신을 사랑하겠습니다.
            - 이제 백일몽에서 깰 때가 되었소. 황혼의 빛이 따스해 보이더라도 현명한 자라면 그 속에 배어있는 냉기를 느낄 수 있을 거요. 차가운 밤을 대비하시오.
            - "술이 뭔데요?", "차가운 불입니다. 거기에 달을 담아 마시지요."
            - 글쎄요. 봄은 새싹 속에 있습니까? 새싹 속엔 봄이 분명히 있습니다만.
            - 오늘은 어제보다 더 사랑하려 애쓰고, 내일은 오늘보다 더 사랑하려 마음먹으시오. 함께 있을 수 있는 시간은 너무도 짧소. 그리고 그녀의 무덤에 바칠 일만 송이의 꽃은 그녀의 작은 미소보다 무가치하오.
            - 붓이 정녕 칼보다 강하다면, 그 책임 또한 더 무거워야 합니다.
            - 충분한 난폭함을 가지고 있다면, 네 삶을 시련으로 만들어라
            - 무애(無碍)한 세상에… 울타리 세워봐야 부질 없는 짓이다.
            - 현자는 우자를 경멸하지 않는다. 경멸은 항상 그 반대로 작용하지.
            - 이파리 보안관의 침실은 표현하기 힘든 빛으로 물들어 있었다. 촛농 무더기 위에서 너울거리는 작은 불꽃은 조명이라기보다 장식품처럼 보였다. 안개를 투과하여 창문으로 흘러 들어오는 빛이 방 안에 고여 있던 어둠을 바래게 하고 있었다. 바닥을 쓸면 사물의 표면에서 떨어져 나온 어둠의 가루를 모을 수 있을 것 같다. 그러는 대신 나는 벗어놓은 겉옷 속에서 편지를 꺼냈다.
            - 편지는 군데군데 젖어 있었지만 망가지지는 않았다. 나는 그것을 조심스럽게 펼치며 말했
            - 그럼 데이트로군. 핫하하! 저 사우스그레이드에서 자네를 처음 봤을 때가 생각나는걸. 콧물을 마셔대고 있던 그 꼬마가 이젠 데이트 신청까지 받는 어엿한 청년이 되었군. 시간의 놀라움이 여!그 쾌속이 비정하게까지 느껴지는구먼
            - "지평선을 넘기 위해서지"
            - 나는 화내지 않았다. 절대로 화낼 생각은 없었다. 대신 길옆에 있던 측백나무를 걷어차 눈 한 무더기를 떨어지게 만들었다.
            - "지평선은 넘을 수 없어. 보이긴 해도 닿을 순 없는 거라고. 그게 보인다는 이유로 정말 넘을 수 있다고 생각했단 말인가?"
            - 황혼의 꿀 빛 베일이 세상을 부드럽게 덮는 시각, 어디서 저녁 식사에 내놓을 빵을 굽는지 구수한 냄새가 풍겨온다. 만인에게 성스러운 하루가 만인의 방식으로 마무리 지어지는 가운데 고요 히 밤이 찾아들고 있었다. 밤은 마법의 시간. 추억이 현재의 수면 위로 숭어처럼 힘차게 뛰어오르는 시간. 약간 모자란 이의 약점도 덮어주고 뛰어난 이의 모습은 더욱 황홀하게 치장하는 어 둠이 찾아드는 이 우아한 시간.
            - 어디 보자. 이걸 어떻게 설명하면 좋을까. 그래. 찬 잔은 채울 수 없고 빈 잔은 비울 수 없다는 거지.
            - 바꿔 말하면 행복한 사람을 행복하게 할 수는 없고 불행한 사람을 불행하게 할 수는 없다는 거야. 물론 자네는 더 행복하다거나 더 불행하다는 말이 있다고 하겠지. 그래. 그런 말이 있네. 하 지만 그건 공허한 말이야. 어떤 행복한 사람에게 무엇이 주어져서 더 행복해졌다면, 그에게서 그것을 박탈하면 다시 행복해질까? 아니지. 그 사람은 불행해질 거야. 반대로 어떤 불행한 사람 에게 어떤 짐이 주어져서 더 불행해졌다면, 그것이 제거되면 다시 불행해질까? 글쎄. 아마 행복을 느낄 거야.
            - 따라서 사람의 마음속엔 행복의 눈금 같은 것은 없다는 거지. 찬 잔은 비울 수 있을 뿐이고 빈 잔은 채울 수 있을 뿐이야. 둘 중 하나일 뿐이야. 마찬가지로 행복한 이는 불행하게 할 수 있고 불행한 이는 행복하게 할 수 있다는 거지. 그러니 행복의 근원은 불행이야. 물론 불행의 근원은 행복이고!

            
            첫 메시지는 당신이 먼저 보내주세요. 첫 대화를 이끌어내줄 수 있는 어떤 인사말이라도 괜찮습니다. 가령, 예를 들면 다음과 같이 대화를 시작할 수 있겠죠?
            "안녕하세요, 오늘 어떤 하루를 보냈는지 저에게 들려주시겠어요?"

            유저가 답변을 하면, 유저의 그날 하루 일기를 써주기 위해서 필요한 더욱 충분한 정보를 이끌어내기 위한 자연스러운 대화를 이끌어주세요.
            
            만약, 당신이 유저와의 대화를 통해서 충분한 정보를 얻어서 좋은 일기를 작성할 준비가 되면 유저에게 "오늘 하루 있었던 일로 일기를 작성해드릴까요?" 라고 질문해주세요. 
            그리고 유저가 긍정의 답을 하면 일기를 작성해주세요. 일기의 포맷은 다음과 같이 작성해주세요. 

            [TITLE_START]
            이곳에 제목을 작성해주세요. 
            [TITLE_END]

            [CONTENT_START]
            이곳에 일기를 작성해주세요.
            [CONTENT_END]
            """,
        )

        new_session = ChatSession(id="", user_id=user.id, messages=[system_prompt])
        ai_first_message = await self.ai_chat_bot.send(new_session)
        new_session.messages.append(ai_first_message)

        new_session = await self.chat_repository.create_session(new_session)
        return new_session

    async def end_chat_session(self, session: ChatSession):
        await self.chat_repository.end_session(session)

    async def send_chat_message(
        self, session: ChatSession, new_message: ChatMessage
    ) -> ChatMessage:
        session.messages.append(new_message)
        await self.chat_repository.add_message(session, new_message)
        reply = await self.ai_chat_bot.send(session)
        await self.chat_repository.add_message(session, reply)
        return reply

    async def write_diary(
        self, chat_session: ChatSession, target_message: ChatMessage
    ) -> Diary:
        # AI 응답에서 title과 content 추출
        content_text = target_message.content

        # 정규표현식으로 title 추출
        title_match = re.search(
            r"\[TITLE_START\](.*?)\[TITLE_END\]", content_text, re.DOTALL
        )
        title = title_match.group(1).strip() if title_match else None

        # 정규표현식으로 content 추출
        content_match = re.search(
            r"\[CONTENT_START\](.*?)\[CONTENT_END\]", content_text, re.DOTALL
        )
        content = content_match.group(1).strip() if content_match else content_text

        diary = Diary(
            user_id=chat_session.user_id,
            chat_session_id=chat_session.id,
            title=title,
            content=content,
            thumbnail_url=None,
        )

        diary = await self.diary_repository.create(diary)
        return diary

    async def get_diary_by_date(self, writed_at: date) -> Diary:
        diary = await self.diary_repository.find_by_date(writed_at)
        if diary is None:
            raise NotFoundError()

        return diary
