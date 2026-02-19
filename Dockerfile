# Python 3.14 베이스 이미지
FROM python:3.14-slim

# 작업 디렉토리 설정
WORKDIR /app

# uv 설치 (Python 패키지 매니저)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 프로젝트 파일 복사
COPY pyproject.toml uv.lock ./

# 의존성 설치 (가상환경 생성 및 패키지 설치)
RUN uv sync --frozen --no-dev

# 애플리케이션 코드 복사 (의존성 설치 후에 복사)
COPY . .

# 가상환경 경로를 PATH에 추가
ENV PATH="/app/.venv/bin:$PATH"

# 포트 노출
EXPOSE 8000

# 서버 실행
CMD ["uv", "run", "main.py"]
