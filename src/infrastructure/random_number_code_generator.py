from src.domain.interfaces.verification_code_generator import VerificationCodeGenerator
import random


class RandomNumberCodeGenerator(VerificationCodeGenerator):
    def generate(self) -> str:
        code = random.randint(100000, 999999)
        return f"{code}"
