from faker import Faker

from src.domain.interfaces.random_name_generator import RandomNameGenerator


class FakerRandomNameGenerator(RandomNameGenerator):
    def __init__(self):
        self.fake = Faker("ko_KR")
        self.adjectives = [
            "행복한",
            "즐거운",
            "신나는",
            "귀여운",
            "멋진",
            "용감한",
            "씩씩한",
            "활발한",
            "조용한",
            "차분한",
            "사랑스러운",
            "당당한",
            "빛나는",
            "푸른",
            "붉은",
            "따뜻한",
            "시원한",
            "달콤한",
            "상쾌한",
            "반짝이는",
        ]

        self.nouns = [
            "루피",
            "뽀로로",
            "토끼",
            "호랑이",
            "사자",
            "펭귄",
            "판다",
            "코끼리",
            "고양이",
            "강아지",
            "여우",
            "다람쥐",
            "햄스터",
            "앵무새",
            "돌고래",
            "코알라",
            "기린",
            "얼룩말",
            "수달",
            "미어캣",
        ]

    def generate(self) -> str:
        """형용사 + 명사 조합으로 랜덤 닉네임 생성 (예: 행복한루피)"""
        adj = self.fake.random_element(self.adjectives)
        noun = self.fake.random_element(self.nouns)
        return f"{adj}{noun}"
