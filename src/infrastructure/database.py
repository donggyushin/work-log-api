import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional


class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


db = Database()


async def connect_to_mongo():
    """MongoDB 연결"""
    username = os.getenv("MONGO_INITDB_ROOT_USERNAME", "admin")
    password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
    host = os.getenv("MONGO_HOST", "localhost")
    port = os.getenv("MONGO_PORT", "27017")

    # MongoDB URI 생성
    mongo_uri = f"mongodb://{username}:{password}@{host}:{port}"

    # Motor 클라이언트 생성
    db.client = AsyncIOMotorClient(mongo_uri)
    db.db = db.client["dailylog"]  # 데이터베이스 이름

    print(f"Connected to MongoDB at {host}:{port}")


async def close_mongo_connection():
    """MongoDB 연결 종료"""
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")


def get_database() -> Optional[AsyncIOMotorDatabase]:
    """데이터베이스 인스턴스 반환"""
    return db.db
