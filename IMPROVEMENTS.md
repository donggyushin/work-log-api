# DailyLog API - 개선사항 및 기능 제안

> 프로젝트 분석 일자: 2026-03-08

## 📊 현재 프로젝트 상태

### 구현된 핵심 기능
- ✅ JWT 기반 사용자 인증 (access/refresh token)
- ✅ 이메일 인증 시스템 (Resend API)
- ✅ AI 대화형 일기 작성 (Claude Sonnet 4.5, 이영도 스타일)
- ✅ AI 썸네일 생성 (DALL-E 3)
- ✅ 프로필 관리 (이미지 업로드/삭제, Cloudflare R2)
- ✅ 일기 CRUD 및 페이지네이션
- ✅ 비밀번호 변경 기능
- ✅ Clean Architecture 패턴 적용
- ✅ Docker 컨테이너화
- ✅ Railway 배포 설정

### 아키텍처 강점
- Domain-driven design with clear separation
- Repository pattern for data access
- Dependency injection via FastAPI
- MongoDB with Motor (async driver)
- Type-safe code with Pydantic models

---

## 🎯 우선순위별 개선사항

## Priority 1: 핵심 기능 강화

### 1. 감정 분석 및 통계 기능
**설명**: 일기 내용을 AI로 분석해서 감정 상태를 추적하고 시각화

**구현 요소**:
- Diary 엔티티에 `emotion` 필드 추가 (POSITIVE, NEUTRAL, NEGATIVE, MIXED)
- `emotion_score` (0.0 ~ 1.0) 추가로 강도 측정
- Claude API로 감정 분석 프롬프트 실행
- 통계 집계 서비스 추가

**새 API 엔드포인트**:
```
GET /api/v1/diaries/statistics
  - Query: from_date, to_date, group_by (day|week|month)
  - Response: { emotions: {...}, word_cloud: [...], total_count: N }

GET /api/v1/diaries/emotions/{emotion}
  - 특정 감정의 일기만 필터링
```

**기술적 고려사항**:
- 감정 분석은 일기 작성 시 비동기로 수행 (성능 고려)
- 월별 통계는 Redis 캐싱으로 최적화

**예상 작업량**: 3-4일

---

### 2. 일기 검색 기능
**설명**: 키워드, 날짜 범위, 태그 기반 일기 검색

**구현 요소**:
- MongoDB text index 생성 (title, content 필드)
- Diary 엔티티에 `tags: List[str]` 필드 추가
- 검색 서비스 레이어 추가 (DiarySearchService)

**새 API 엔드포인트**:
```
GET /api/v1/diaries/search
  - Query params:
    - q: 검색 키워드 (fulltext search)
    - tags: 쉼표로 구분된 태그 (예: 여행,음식)
    - from_date, to_date: 날짜 범위
    - emotion: 감정 필터
  - Response: 검색된 일기 목록 (pagination 지원)

POST /api/v1/diary/{diary_id}/tags
  - Body: { tags: ["여행", "제주도"] }
  - 태그 추가/수정

DELETE /api/v1/diary/{diary_id}/tags/{tag}
  - 특정 태그 제거
```

**MongoDB 인덱스**:
```python
# 마이그레이션 스크립트 필요
db.diaries.create_index([("title", "text"), ("content", "text")])
db.diaries.create_index("tags")
db.diaries.create_index([("user_id", 1), ("writed_at", -1)])
```

**예상 작업량**: 2-3일

---

### 3. 결제/구독 시스템 완성
**설명**: 현재 `PaymentsLog` 엔티티만 있고 실제 결제 로직이 없음. 전체 결제 플로우 구현 필요

**구현 요소**:
- 결제 게이트웨이 연동 (토스페이먼츠 또는 아임포트 추천)
- 구독 플랜 엔티티 추가 (SubscriptionPlan)
- 구독 상태 관리 (ACTIVE, CANCELLED, EXPIRED)
- Webhook 처리 (결제 성공/실패/환불)

**구독 플랜 설계**:
```python
class SubscriptionPlan(Enum):
    FREE = "free"           # 3회 무료
    MONTHLY = "monthly"     # 월 9,900원
    YEARLY = "yearly"       # 연 99,000원 (2개월 무료)

class Subscription(BaseModel):
    id: str
    user_id: str
    plan: SubscriptionPlan
    status: SubscriptionStatus  # ACTIVE, CANCELLED, EXPIRED
    start_date: date
    end_date: date
    auto_renew: bool
    payment_method_id: Optional[str]
    created_at: datetime
```

**새 API 엔드포인트**:
```
GET /api/v1/subscriptions/plans
  - 사용 가능한 구독 플랜 목록

POST /api/v1/subscriptions/subscribe
  - Body: { plan: "monthly", payment_method: "card" }
  - 구독 시작 (결제 게이트웨이로 리다이렉트)

POST /api/v1/subscriptions/cancel
  - 구독 취소 (다음 갱신일까지 유효)

GET /api/v1/subscriptions/current
  - 현재 구독 상태 조회

GET /api/v1/payments/history
  - 결제 내역 조회

POST /api/v1/webhooks/payments
  - 결제 게이트웨이 webhook 처리
```

**보안 고려사항**:
- Webhook 서명 검증 필수
- 결제 정보는 절대 DB에 저장하지 않음 (PCI-DSS 준수)
- 구독 상태 변경 시 이메일 알림

**예상 작업량**: 5-7일

---

### 4. 일기 리마인더 알림
**설명**: 설정한 시간에 일기 작성 알림 전송

**구현 요소**:
- Firebase Cloud Messaging (FCM) 또는 푸시 알림 서비스 연동
- 스케줄러 추가 (APScheduler 또는 Celery Beat)
- 사용자별 알림 설정 저장

**새 엔티티**:
```python
class ReminderSettings(BaseModel):
    id: str
    user_id: str
    enabled: bool
    reminder_time: time  # 예: 21:00
    days_of_week: List[int]  # 0=월, 6=일
    fcm_token: Optional[str]  # 모바일 앱용
    timezone: str  # "Asia/Seoul"
```

**새 API 엔드포인트**:
```
GET /api/v1/reminders/settings
  - 현재 리마인더 설정 조회

PUT /api/v1/reminders/settings
  - Body: { enabled: true, reminder_time: "21:00", days_of_week: [1,2,3,4,5] }
  - 리마인더 설정 업데이트

POST /api/v1/reminders/fcm-token
  - Body: { token: "fcm_device_token" }
  - FCM 토큰 등록 (모바일 앱용)
```

**스케줄러 구현**:
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=21, minute=0)
async def send_daily_reminders():
    # 21시에 알림 설정한 사용자 찾기
    users = await reminder_service.get_users_for_reminder(datetime.now().time())
    for user in users:
        await notification_service.send_push(
            user.fcm_token,
            "오늘 하루는 어땠나요?",
            "일기를 작성해보세요 ✍️"
        )
```

**예상 작업량**: 3-4일

---

### 5. 일기 공유 기능
**설명**: 특정 일기를 공개 링크로 공유 (읽기 전용)

**구현 요소**:
- ShareToken 엔티티 추가
- UUID 기반 공유 토큰 생성
- 만료 기간 설정 (7일, 30일, 무제한)
- 공개 조회 API (인증 불필요)

**새 엔티티**:
```python
class ShareToken(BaseModel):
    id: str
    diary_id: str
    token: str  # UUID
    expires_at: Optional[datetime]
    view_count: int
    created_at: datetime
```

**새 API 엔드포인트**:
```
POST /api/v1/diary/{diary_id}/share
  - Body: { expires_in_days: 7 }  # optional, null = 무제한
  - Response: { share_url: "https://dailylog.com/shared/abc123" }

GET /api/v1/shared/{token}
  - 인증 없이 공개 조회 가능
  - Response: 일기 내용 + 작성자 닉네임 (이메일 제외)
  - view_count 증가

DELETE /api/v1/diary/{diary_id}/share
  - 공유 링크 비활성화
```

**보안 고려사항**:
- 공유된 일기는 작성자 개인정보(이메일) 노출 안 됨
- Rate limiting 적용 (스크래핑 방지)
- 공유 비활성화 시 즉시 접근 불가

**예상 작업량**: 2일

---

## Priority 2: 기술적 개선

### 6. 성능 최적화

#### 6.1 Redis 캐싱 도입
**대상 데이터**:
- 사용자 정보 (TTL: 15분)
- 최근 일기 목록 (TTL: 5분)
- 구독 상태 (TTL: 10분)
- 감정 통계 (TTL: 1시간)

**구현 예시**:
```python
# infrastructure/redis_cache.py
from redis.asyncio import Redis

class RedisCache:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_user(self, user_id: str) -> Optional[User]:
        data = await self.redis.get(f"user:{user_id}")
        if data:
            return User.model_validate_json(data)
        return None

    async def set_user(self, user: User, ttl: int = 900):
        await self.redis.setex(
            f"user:{user.id}",
            ttl,
            user.model_dump_json()
        )
```

**환경 변수 추가**:
```
REDIS_URL=redis://localhost:6379/0
```

**docker-compose.yml 수정**:
```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
```

---

#### 6.2 비동기 작업 큐 (Celery)
**대상 작업**:
- DALL-E 썸네일 생성 (현재 동기적으로 처리되어 느림)
- 감정 분석
- 이메일 발송
- 대용량 데이터 내보내기

**구현**:
```python
# infrastructure/celery_app.py
from celery import Celery

celery_app = Celery(
    'dailylog',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

@celery_app.task
async def generate_thumbnail_task(diary_id: str):
    diary = await diary_repository.find_by_id(diary_id)
    image_url = await image_generator.generate(diary.title, diary.content)
    await diary_repository.update_thumbnail(diary_id, image_url)
```

**API 변경**:
```python
# 기존: 동기적으로 썸네일 생성 (느림)
# 개선: 일기는 즉시 저장, 썸네일은 백그라운드에서 생성
@app.post("/api/v1/diary")
async def write_diary(...):
    diary = await diary_service.write_diary(...)

    # 비동기 작업으로 썸네일 생성
    generate_thumbnail_task.delay(diary.id)

    return diary  # 즉시 반환 (thumbnail_url은 나중에 업데이트)
```

---

#### 6.3 데이터베이스 인덱스 최적화
**필수 인덱스**:
```python
# scripts/create_indexes.py
async def create_indexes():
    db = await get_database()

    # Users collection
    await db.users.create_index("email", unique=True)

    # Diaries collection
    await db.diaries.create_index([("user_id", 1), ("writed_at", -1)])
    await db.diaries.create_index([("title", "text"), ("content", "text")])
    await db.diaries.create_index("tags")

    # Chats collection
    await db.chats.create_index([("user_id", 1), ("active", 1)])

    # Email verification codes
    await db.email_verification_codes.create_index("expired_at", expireAfterSeconds=0)  # TTL index
```

**실행**:
```bash
uv run python scripts/create_indexes.py
```

---

### 7. 보안 강화

#### 7.1 CORS 설정 엄격화
**현재 문제**: `allow_origins=["*"]` - 모든 도메인 허용

**개선**:
```python
# main.py
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 환경변수로 관리
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)
```

**.env 추가**:
```
ALLOWED_ORIGINS=https://dailylog.com,https://app.dailylog.com
```

---

#### 7.2 Rate Limiting
**구현**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 적용
@app.post("/api/v1/email_verification_code")
@limiter.limit("3/minute")  # 분당 3회 제한
async def send_verification_code(...):
    ...

@app.post("/api/v1/register")
@limiter.limit("5/hour")  # 시간당 5회 제한
async def register(...):
    ...
```

---

#### 7.3 민감 정보 로깅 방지
**현재 문제**: 에러 로그에 사용자 데이터 노출 가능

**개선**:
```python
# domain/logging.py
import structlog

logger = structlog.get_logger()

# 민감 필드 마스킹
def mask_sensitive(data: dict) -> dict:
    sensitive_fields = ["password", "email", "token"]
    return {
        k: "***REDACTED***" if k in sensitive_fields else v
        for k, v in data.items()
    }

# 사용
logger.info("User registered", user_data=mask_sensitive(user.model_dump()))
```

---

#### 7.4 JWT 토큰 만료 시간 명시
**현재 문제**: `PyJWTProvider`에서 만료 시간 설정이 불명확

**개선**:
```python
# infrastructure/py_jwt_provider.py
class PyJWTProvider(JWTProvider):
    ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1시간
    REFRESH_TOKEN_EXPIRE_DAYS = 30    # 30일

    def generate_token(self, user_id: str) -> str:
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        return jwt.encode(
            {"user_id": user_id, "exp": expire},
            self.secret_key,
            algorithm="HS256"
        )
```

---

### 8. 데이터 백업/복원

#### 8.1 사용자 데이터 내보내기
**구현**:
```python
# domain/services/export_service.py
class ExportService:
    async def export_user_data(self, user_id: str) -> bytes:
        """전체 일기 + 이미지를 ZIP 파일로 내보내기"""
        diaries = await self.diary_repository.find_all_by_user(user_id)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            # JSON 데이터
            zip_file.writestr(
                'diaries.json',
                json.dumps([d.model_dump() for d in diaries], ensure_ascii=False)
            )

            # 이미지 다운로드
            for diary in diaries:
                if diary.thumbnail_url:
                    image_data = await self.download_image(diary.thumbnail_url)
                    zip_file.writestr(f'images/{diary.id}.png', image_data)

        return zip_buffer.getvalue()
```

**API 엔드포인트**:
```
GET /api/v1/export
  - Response: application/zip
  - Content-Disposition: attachment; filename="dailylog_export_2024-12-10.zip"
```

---

#### 8.2 GDPR 준수 - 데이터 삭제
**구현**:
```python
@app.delete("/api/v1/me/delete-account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    confirmation: str = Body(...)
):
    """계정 영구 삭제 (GDPR Right to be Forgotten)"""
    if confirmation != current_user.email:
        raise HTTPException(400, "이메일 확인이 일치하지 않습니다")

    # 모든 관련 데이터 삭제
    await user_service.delete_user_and_all_data(current_user.id)

    return {"message": "계정이 영구 삭제되었습니다"}
```

---

### 9. 테스트 코드 작성

#### 디렉토리 구조
```
tests/
├── conftest.py              # pytest fixtures
├── test_auth_service.py     # 인증 서비스 유닛 테스트
├── test_diary_service.py    # 일기 서비스 유닛 테스트
├── test_repositories.py     # 레포지토리 통합 테스트
├── test_api_endpoints.py    # API E2E 테스트
└── fixtures/
    └── sample_data.py       # 테스트 데이터
```

#### 예시: 인증 테스트
```python
# tests/test_auth_service.py
import pytest
from src.domain.services.auth_service import AuthService
from src.domain.exceptions import EmailAlreadyExistsError

@pytest.mark.asyncio
async def test_register_success(auth_service: AuthService):
    """회원가입 성공 케이스"""
    user = await auth_service.register("test@example.com", "password123")

    assert user.email == "test@example.com"
    assert user.username is not None  # 자동 생성된 닉네임
    assert user.email_verified is False

@pytest.mark.asyncio
async def test_register_duplicate_email(auth_service: AuthService):
    """이메일 중복 시 예외 발생"""
    await auth_service.register("test@example.com", "password123")

    with pytest.raises(EmailAlreadyExistsError):
        await auth_service.register("test@example.com", "password456")
```

#### pytest 설정
```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
```

**실행**:
```bash
uv run pytest tests/ -v
uv run pytest --cov=src tests/  # 커버리지 측정
```

---

### 10. 에러 처리 개선

#### 현재 문제점
`api.py`에서 너무 많은 generic exception handling:
```python
try:
    result = await service.do_something()
except Exception as e:
    raise e  # 의미 없는 re-raise
```

#### 개선 방안

**1. 도메인 예외를 HTTP 예외로 매핑**:
```python
# presentation/error_handlers.py
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(EmailAlreadyExistsError)
async def email_exists_handler(request: Request, exc: EmailAlreadyExistsError):
    return JSONResponse(
        status_code=409,
        content={"detail": "이미 사용 중인 이메일입니다"}
    )

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": "리소스를 찾을 수 없습니다"}
    )

@app.exception_handler(ExpiredError)
async def expired_handler(request: Request, exc: ExpiredError):
    return JSONResponse(
        status_code=400,
        content={"detail": "만료된 요청입니다"}
    )
```

**2. API 라우트 단순화**:
```python
# Before
@app.post("/api/v1/diary")
async def write_diary(...):
    try:
        result = await service.write_diary(...)
        return result
    except NotFoundError:
        raise HTTPException(404, "세션을 찾을 수 없습니다")
    except ExpiredError:
        raise HTTPException(400, "세션이 만료되었습니다")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(500, "서버 오류")

# After (with global exception handlers)
@app.post("/api/v1/diary")
async def write_diary(...):
    # 예외는 글로벌 핸들러가 자동 처리
    return await service.write_diary(...)
```

**3. 구조화된 에러 응답**:
```python
class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[dict] = None

# 사용 예시
return JSONResponse(
    status_code=400,
    content=ErrorResponse(
        error_code="INVALID_VERIFICATION_CODE",
        message="인증 코드가 올바르지 않습니다",
        details={"attempts_remaining": 2}
    ).model_dump()
)
```

---

## Priority 3: UX 개선

### 11. AI 프롬프트 템플릿

**설명**: 사용자가 AI 작가 스타일을 선택할 수 있도록 함

**현재**: 이영도 스타일만 고정
**개선**: 다양한 스타일 제공

**새 엔티티**:
```python
class WritingStyle(Enum):
    LEE_YEONGDO = "lee_yeongdo"        # 현재 기본값
    MURAKAMI = "murakami"              # 무라카미 하루키 (간결, 일상적)
    KIM_YOUNGHA = "kim_youngha"        # 김영하 (현대적, 도시적)
    SIMPLE = "simple"                  # 단순 일기체
    POETIC = "poetic"                  # 시적 표현
```

**User 엔티티 수정**:
```python
class User(BaseModel):
    ...
    preferred_writing_style: WritingStyle = WritingStyle.LEE_YEONGDO
```

**API 엔드포인트**:
```
GET /api/v1/writing-styles
  - Response: [
      { id: "lee_yeongdo", name: "이영도", description: "판타지 소설가의 섬세한 묘사" },
      { id: "simple", name: "간결한 일기", description: "단순하고 명료한 문체" }
    ]

PUT /api/v1/me/writing-style
  - Body: { style: "murakami" }
  - 선호 스타일 저장
```

**시스템 프롬프트 관리**:
```python
# domain/prompts/writing_styles.py
WRITING_STYLE_PROMPTS = {
    WritingStyle.LEE_YEONGDO: """
    당신은 한국의 판타지 소설가 이영도의 문체로 일기를 작성합니다...
    """,
    WritingStyle.SIMPLE: """
    당신은 간결하고 명료한 일기를 작성합니다.
    - 불필요한 수식어 최소화
    - 사실 중심의 서술
    - 3-5문단으로 구성
    """,
    WritingStyle.MURAKAMI: """
    당신은 일본 작가 무라카미 하루키의 문체로 일기를 작성합니다.
    - 일상적이고 간결한 문장
    - 고독과 성찰의 분위기
    - 음식, 음악 등 구체적 디테일 포함
    """
}
```

---

### 12. 일기 달력 뷰

**설명**: 월별 달력 형태로 일기 작성 여부를 한눈에 확인

**API 엔드포인트**:
```
GET /api/v1/diaries/calendar/{year}/{month}
  - Response: {
      "year": 2024,
      "month": 12,
      "days": [
        { "date": "2024-12-01", "has_diary": true, "emotion": "POSITIVE" },
        { "date": "2024-12-02", "has_diary": false },
        ...
      ]
    }
```

**구현**:
```python
class DiaryService:
    async def get_calendar_data(self, user_id: str, year: int, month: int) -> dict:
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        diaries = await self.diary_repository.find_by_date_range(
            user_id, start_date, end_date
        )

        # 날짜별로 그룹핑
        diary_map = {d.writed_at: d for d in diaries}

        # 모든 날짜 생성
        days = []
        current = start_date
        while current < end_date:
            diary = diary_map.get(current.isoformat())
            days.append({
                "date": current.isoformat(),
                "has_diary": diary is not None,
                "emotion": diary.emotion if diary else None
            })
            current += timedelta(days=1)

        return {"year": year, "month": month, "days": days}
```

---

### 13. 연속 작성 일수 추적 (Streak)

**설명**: 연속으로 일기를 작성한 일수를 추적하고 동기부여 제공

**User 엔티티 수정**:
```python
class User(BaseModel):
    ...
    current_streak: int = 0          # 현재 연속 일수
    longest_streak: int = 0          # 최장 연속 기록
    last_diary_date: Optional[date] = None
```

**로직**:
```python
class DiaryService:
    async def update_streak(self, user: User, diary_date: date):
        """일기 작성 시 연속 일수 업데이트"""
        if user.last_diary_date is None:
            # 첫 일기
            user.current_streak = 1
        else:
            days_diff = (diary_date - user.last_diary_date).days

            if days_diff == 1:
                # 연속 작성
                user.current_streak += 1
            elif days_diff == 0:
                # 같은 날 (업데이트)
                pass
            else:
                # 연속 끊김
                user.current_streak = 1

        # 최장 기록 갱신
        if user.current_streak > user.longest_streak:
            user.longest_streak = user.current_streak

        user.last_diary_date = diary_date
        await self.user_repository.update(user)
```

**배지 시스템**:
```python
class Achievement(Enum):
    STREAK_7 = "7일 연속 작성"
    STREAK_30 = "30일 연속 작성"
    STREAK_100 = "100일 연속 작성"
    DIARY_COUNT_50 = "일기 50개 작성"
    DIARY_COUNT_365 = "일기 365개 작성"

def get_achievements(user: User, total_diaries: int) -> List[Achievement]:
    achievements = []
    if user.longest_streak >= 7:
        achievements.append(Achievement.STREAK_7)
    if user.longest_streak >= 30:
        achievements.append(Achievement.STREAK_30)
    if user.longest_streak >= 100:
        achievements.append(Achievement.STREAK_100)
    if total_diaries >= 50:
        achievements.append(Achievement.DIARY_COUNT_50)
    if total_diaries >= 365:
        achievements.append(Achievement.DIARY_COUNT_365)
    return achievements
```

**API**:
```
GET /api/v1/me/achievements
  - Response: {
      "current_streak": 5,
      "longest_streak": 12,
      "achievements": ["STREAK_7", "DIARY_COUNT_50"]
    }
```

---

## 💡 Quick Wins (즉시 구현 가능)

### 1. API 문서 자동화 (Swagger UI)

**현재 문제**: FastAPI의 자동 문서 기능이 비활성화되어 있을 가능성

**개선**:
```python
# main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="DailyLog API",
        version="1.0.0",
        description="AI-powered diary API with authentication and image generation",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# 접속: http://localhost:8000/docs (Swagger UI)
# 접속: http://localhost:8000/redoc (ReDoc)
```

**Response 모델에 예시 추가**:
```python
class DiaryResponse(BaseModel):
    id: str = Field(..., example="507f1f77bcf86cd799439011")
    title: str = Field(..., example="오늘의 소중한 순간")
    content: str = Field(..., example="오늘은 친구와 카페에서...")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "507f1f77bcf86cd799439011",
                    "title": "오늘의 소중한 순간",
                    "content": "오늘은 친구와 카페에서 오랜만에 수다를 떨었다..."
                }
            ]
        }
    }
```

**예상 작업량**: 1-2시간

---

### 2. 환경변수 관리 개선 (pydantic-settings)

**현재 문제**: 환경변수가 여러 파일에 분산되어 있음

**개선**:
```python
# config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # JWT
    jwt_secret_key: str

    # MongoDB
    mongo_url: Optional[str] = None
    mongo_host: str = "localhost"
    mongo_port: int = 27017
    mongo_username: str
    mongo_password: str

    # External APIs
    anthropic_api_key: str
    openai_api_key: str
    resend_api_key: str

    # Cloudflare R2
    cloudflare_account_id: str
    cloudflare_r2_access_key_id: str
    cloudflare_r2_secret_access_key: str
    cloudflare_r2_bucket_name: str
    cloudflare_r2_public_domain: Optional[str] = None

    # Server
    port: int = 8000
    debug: bool = False
    allowed_origins: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

# 싱글톤
settings = Settings()
```

**사용**:
```python
from config.settings import settings

# 기존: os.getenv("JWT_SECRET_KEY")
# 개선: settings.jwt_secret_key (타입 안전성 + 자동 검증)
```

**예상 작업량**: 2-3시간

---

### 3. 구조화된 로깅 (structlog)

**현재 문제**: 로그가 일관성 없음

**개선**:
```python
# infrastructure/logging.py
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# 사용
logger.info("user_registered", user_id=user.id, email=user.email)
logger.error("diary_creation_failed", user_id=user.id, error=str(e))
```

**출력** (JSON 형식으로 구조화):
```json
{
  "event": "user_registered",
  "user_id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "timestamp": "2024-12-10T12:34:56.789Z",
  "level": "info"
}
```

**예상 작업량**: 2시간

---

### 4. 타입 체크 오류 수정

**현재**: CI에서 mypy 실행하지만 경고가 있을 수 있음

**확인**:
```bash
make typecheck
```

**일반적인 오류 패턴**:
```python
# 오류: Optional 타입 처리 안 됨
user = await user_repository.find_by_id(user_id)
user.email  # mypy error: user could be None

# 수정
user = await user_repository.find_by_id(user_id)
if not user:
    raise NotFoundError()
user.email  # OK
```

**예상 작업량**: 1-2시간

---

## 📋 구현 로드맵 제안

### Phase 1: 핵심 기능 개선 (2-3주)
1. ✅ Quick wins 구현 (API 문서, 설정 관리, 로깅)
2. 🔍 일기 검색 기능
3. 📊 감정 분석 및 통계
4. 📅 달력 뷰 + Streak 추적

### Phase 2: 비즈니스 모델 (2주)
1. 💳 결제/구독 시스템 완성
2. 🔔 리마인더 알림

### Phase 3: 성능 & 보안 (1-2주)
1. ⚡ Redis 캐싱
2. 🔒 보안 강화 (CORS, Rate limiting)
3. 🧪 테스트 코드 작성

### Phase 4: UX 개선 (1주)
1. ✍️ AI 스타일 선택
2. 🔗 일기 공유 기능
3. 📤 데이터 내보내기

---

## 🛠 개발 환경 개선 제안

### 개발 도구 추가
```toml
# pyproject.toml
[tool.uv.dev-dependencies]
pytest = "^8.0.0"
pytest-asyncio = "^0.23.0"
pytest-cov = "^5.0.0"
structlog = "^24.0.0"
redis = "^5.0.0"
celery = "^5.4.0"
slowapi = "^0.1.9"
pydantic-settings = "^2.3.0"
```

### Pre-commit 훅 설정
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black

  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic]
```

---

## 📊 성능 벤치마크 목표

### 응답 시간 목표
- 인증 API: < 200ms
- 일기 목록 조회: < 300ms
- 일기 작성 (AI 응답): < 5s
- 썸네일 생성: < 10s (비동기 처리)

### 동시 접속자 목표
- 100명 동시 접속 시 응답 시간 2배 이내
- MongoDB connection pool 크기: 50-100

---

## 🔍 모니터링 & 알림

### 추가 권장 사항
1. **Sentry**: 에러 트래킹 및 알림
2. **Prometheus + Grafana**: 메트릭 수집 및 시각화
3. **Uptime Robot**: 서버 다운타임 감지
4. **LogDNA/Datadog**: 로그 집계 및 검색

---

## ✅ 체크리스트

### 프로덕션 배포 전 필수 항목
- [ ] CORS 설정 엄격화
- [ ] Rate limiting 적용
- [ ] 에러 로그 민감정보 마스킹
- [ ] JWT 만료 시간 명시
- [ ] MongoDB 인덱스 생성
- [ ] 환경변수 검증 (누락된 키 확인)
- [ ] SSL 인증서 설정 (Railway 자동 제공)
- [ ] 백업 전략 수립
- [ ] 로드 테스트 실행
- [ ] 보안 취약점 스캔

---

**문서 작성일**: 2026-03-08
**프로젝트 버전**: 1.0.0
**다음 리뷰 예정일**: 구현 진행 상황에 따라 업데이트
