import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional


class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


db = Database()


async def connect_to_mongo():
    """MongoDB 연결 (Atlas 및 로컬 모두 지원)"""

    # Atlas 연결 문자열이 있으면 우선 사용 (프로덕션)
    mongo_url = os.getenv("MONGO_URL")

    if mongo_url:
        # MongoDB Atlas 또는 전체 연결 문자열 사용
        mongo_uri = mongo_url
        connection_type = "MongoDB Atlas"
    else:
        # 개별 환경 변수 사용 (로컬 개발)
        username = os.getenv("MONGO_INITDB_ROOT_USERNAME", "admin")
        password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
        host = os.getenv("MONGO_HOST", "localhost")
        port = os.getenv("MONGO_PORT", "27017")

        # MongoDB URI 생성
        mongo_uri = f"mongodb://{username}:{password}@{host}:{port}"
        connection_type = f"local MongoDB at {host}:{port}"

    # Motor 클라이언트 생성
    db.client = AsyncIOMotorClient(mongo_uri)
    db.db = db.client["dailylog"]  # 데이터베이스 이름

    # 연결 테스트 (실제로 MongoDB에 연결 시도)
    try:
        await db.client.admin.command('ping')
        print(f"✅ Connected to {connection_type}")
    except Exception as e:
        print(f"❌ Failed to connect to {connection_type}: {e}")
        raise


async def close_mongo_connection():
    """MongoDB 연결 종료"""
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")


def get_database() -> Optional[AsyncIOMotorDatabase]:
    """데이터베이스 인스턴스 반환"""
    return db.db
