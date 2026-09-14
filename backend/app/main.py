"""FastAPI 主应用"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import search_router, poem_router, challenge_router, generate_router, image_router, video_router, assistant_router, imagery_router
from app.database import poems_collection, ensure_indexes
from app.models import Author, Analysis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化示例数据"""
    await ensure_indexes()
    await init_sample_data()
    yield


app = FastAPI(
    title="诗词雅韵 API",
    description="诗词学习/创作后端服务 - Python FastAPI 版本",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(search_router)
app.include_router(poem_router)
app.include_router(challenge_router)
app.include_router(generate_router)
app.include_router(image_router)
app.include_router(video_router)
app.include_router(assistant_router)
app.include_router(imagery_router)


@app.get("/", tags=["健康检查"])
async def root():
    return {"message": "诗词雅韵 API 运行中", "docs": "/docs"}


async def init_sample_data():
    """初始化示例诗词数据（如果数据库为空）"""
    # 清理 AI 生成的诗词（不应留在诗词库中）
    ai_filter = {
        "$or": [
            {"_id": {"$regex": "^(gen-|mimic-|vision-)"}},
            {"author.name": {"$in": ["AI诗人", "AI写手", "AI润色", "AI诗人（看图写诗）"]}},
        ]
    }
    deleted = await poems_collection.delete_many(ai_filter)
    if deleted.deleted_count > 0:
        print(f"已清理 {deleted.deleted_count} 首 AI 生成的诗词")

    count = await poems_collection.count_documents({})
    if count > 0:
        print(f"数据库已有 {count} 首诗词，跳过初始化")
        return

    print("初始化示例诗词数据...")

    sample_poems = [
        {
            "_id": "poem-1",
            "title": "静夜思",
            "author": {
                "name": "李白",
                "dynasty": "唐",
                "brief": "唐代浪漫主义诗人，号青莲居士。"
            },
            "dynasty": "唐",
            "genre": "五言绝句",
            "content": ["床前明月光", "疑是地上霜", "举头望明月", "低头思故乡"],
            "analysis": {
                "translation": "床前的月光让人误以为地上结了霜。抬头望着明月，低头又想起了故乡。",
                "appreciation": "画面寥寥数语，情感直白，寄托浓重的思乡之情。",
                "cultural": "明月常在古典诗词中作为思乡意象。"
            },
            "tags": ["明月", "思乡", "床前"]
        },
        {
            "_id": "poem-2",
            "title": "春晓",
            "author": {
                "name": "孟浩然",
                "dynasty": "唐",
                "brief": "盛唐时期田园诗人，诗风清新自然。"
            },
            "dynasty": "唐",
            "genre": "五言绝句",
            "content": ["春眠不觉晓", "处处闻啼鸟", "夜来风雨声", "花落知多少"],
            "analysis": {
                "translation": "春天睡得很沉，没有感觉到天已亮，到处都能听见鸟叫。夜里风雨声不断，不知道有多少花被吹落。",
                "appreciation": "写春日早晨的生动景象，既有惬意的睡意，也有对春光易逝的淡淡惋惜。",
                "cultural": "以小见大，借景抒情，典型的田园写意手法。"
            },
            "tags": ["春", "鸟", "花"]
        },
        {
            "_id": "poem-3",
            "title": "将进酒",
            "author": {
                "name": "李白",
                "dynasty": "唐",
                "brief": "浪漫主义诗人，善饮善作。"
            },
            "dynasty": "唐",
            "genre": "古体诗",
            "content": ["君不见黄河之水天上来", "奔流到海不复回", "君不见高堂明镜悲白发", "朝如青丝暮成雪"],
            "analysis": {
                "translation": "以豪放奔放的笔调，劝酒寄情，慨叹人生短促，应尽欢娱。",
                "appreciation": "语言奔放，气势磅礴，充满豪放派的风格。",
                "cultural": "常被用来表达及时行乐的人生态度。"
            },
            "tags": ["豪放", "劝酒", "人生"]
        }
    ]

    for poem in sample_poems:
        await poems_collection.update_one(
            {"_id": poem["_id"]},
            {"$set": poem},
            upsert=True
        )

    print(f"成功初始化 {len(sample_poems)} 首示例诗词")
