from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "poetrydb"
    HOST: str = "0.0.0.0"
    PORT: int = 8081

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

    class Config:
        env_file = ".env"


settings = Settings()
