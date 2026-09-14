"""MongoDB 异步连接（Motor）"""
import motor.motor_asyncio
from app.config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.DATABASE_NAME]

# 集合
poems_collection = db["poems"]


async def ensure_indexes():
    """创建 MongoDB 索引以加速检索查询"""
    await poems_collection.create_index("title")
    await poems_collection.create_index("author.name")
    await poems_collection.create_index("tags")
    await poems_collection.create_index("sort_order")
    await poems_collection.create_index("dynasty")
    await poems_collection.create_index("genre")
