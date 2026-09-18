from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # extra="ignore"：容忍 .env 里属于 docker-compose 的变量（如 WEB_PORT），避免启动崩溃
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "poetrydb"
    HOST: str = "0.0.0.0"
    PORT: int = 8081

    # 安全配置
    APP_API_KEY: str = ""  # 非空时，AI 接口需携带 X-API-Key 请求头
    CORS_ORIGINS: str = "http://localhost:5173"  # 逗号分隔的跨域白名单
    AI_RATE_LIMIT_PER_MINUTE: int = 30  # AI 文本接口限流（次/分钟/IP）
    MEDIA_RATE_LIMIT_PER_MINUTE: int = 10  # 图/视频接口限流（次/分钟/IP）

    # LLM 配置
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"

    # 图像生成 API 配置（OpenAI 兼容 /v1/images/generations）
    IMAGE_API_KEY: str = ""
    IMAGE_BASE_URL: str = "https://api.openai.com/v1"
    IMAGE_MODEL: str = "dall-e-3"
    IMAGE_SIZE: str = "1024x1024"

    # 视觉模型 API 配置（支持多模态的 OpenAI 兼容接口）
    VISION_API_KEY: str = ""
    VISION_BASE_URL: str = "https://api.openai.com/v1"
    VISION_MODEL: str = "gpt-4o"

    # 视频生成 API 配置（智谱 CogVideoX）
    VIDEO_API_KEY: str = ""
    VIDEO_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4/"
    VIDEO_MODEL: str = "cogvideox-flash"


settings = Settings()
