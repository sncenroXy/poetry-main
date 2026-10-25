"""MongoDB 异步连接（Motor）"""
import motor.motor_asyncio
from app.config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.DATABASE_NAME]

# 集合
poems_collection = db["poems"]
users_collection = db["users"]
favorites_collection = db["user_favorites"]
activities_collection = db["user_activities"]
creations_collection = db["user_creations"]
wrong_answers_collection = db["user_wrong_answers"]


async def ensure_indexes():
    """创建 MongoDB 索引以加速检索查询"""
    await poems_collection.create_index("title")
    await poems_collection.create_index("author.name")
    await poems_collection.create_index("tags")
    await poems_collection.create_index("sort_order")
    await poems_collection.create_index("dynasty")
    await poems_collection.create_index("genre")
    await poems_collection.create_index([("content", 1)])  # 飞花令接龙等值查询
    await poems_collection.create_index("keywords")  # 检索倒排（jieba 分词，多键索引）
    await favorites_collection.create_index(
        [("username", 1), ("poem_id", 1)], unique=True
    )
    await favorites_collection.create_index([("username", 1), ("created_at", -1)])
    await activities_collection.create_index([("username", 1), ("created_at", -1)])
    await activities_collection.create_index([("username", 1), ("event_type", 1), ("created_at", -1)])
    await creations_collection.create_index([("username", 1), ("created_at", -1)])
    await wrong_answers_collection.create_index([("username", 1), ("created_at", -1)])
