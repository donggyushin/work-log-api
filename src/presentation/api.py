from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.database import close_mongo_connection, connect_to_mongo
from src.presentation.routers import auth, chat, diary, email, password, post, user


# ========================================
# Application Setup
# ========================================


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(lifespan=lifespan)

# CORS 설정: 개발 환경에서 모든 origin 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용하도록 변경 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# Routers
# ========================================

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(email.router)
app.include_router(password.router)
app.include_router(chat.router)
app.include_router(diary.router)
app.include_router(post.router)


# ========================================
# Health Check
# ========================================


@app.get("/api/v1", tags=["Health"])
async def hello():
    return {"message": "hello world"}
