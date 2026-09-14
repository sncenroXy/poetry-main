from .search import router as search_router
from .poem import router as poem_router
from .challenge import router as challenge_router
from .generate import router as generate_router
from .image import router as image_router
from .video import router as video_router
from .assistant import router as assistant_router
from .imagery import router as imagery_router

__all__ = ["search_router", "poem_router", "challenge_router", "generate_router", "image_router", "video_router", "assistant_router", "imagery_router"]
