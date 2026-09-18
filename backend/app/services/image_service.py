"""诗画互生服务 — 文生图 & 图生文"""
import base64
import io
import logging
import time
from typing import Dict, Any
from app.config import settings
from app.models import Poem, Author, Analysis
from app.utils.llm import get_llm_client, get_image_client, get_vision_client, parse_llm_json

logger = logging.getLogger(__name__)


# ---------- 文生图：诗词 → 水墨配图 ----------

PROMPT_TRANSLATE_SYSTEM = """你是一位精通中国古典诗词与视觉艺术的翻译专家。
你的任务是将中国古典诗词翻译为适合 AI 图像生成模型的英文画面描述 prompt。

要求：
1. 深入理解诗词的意境、情感和视觉元素
2. 用英文描述画面中应呈现的景物、色调、氛围、构图
3. 始终附加以下风格约束关键词：Chinese ink wash painting, traditional shanshui style, elegant brushwork, minimalist composition, rice paper texture
4. prompt 长度控制在 80-150 个英文单词
5. 只返回英文 prompt 文本，不要任何其他内容"""


async def generate_image_from_poem(
    poem_text: str,
    title: str = "",
    style: str = "水墨国风",
) -> Dict[str, Any]:
    """文生图：将诗词转为水墨风格配图

    Returns:
        {"image_url": str, "prompt_used": str, "poem_text": str}
    """
    # 第 1 步：用文本 LLM 将诗词翻译为英文图像 prompt
    user_msg = f"诗词标题：{title}\n诗词内容：\n{poem_text}"
    if style != "水墨国风":
        user_msg += f"\n画面风格偏好：{style}"

    llm = get_llm_client()
    translate_resp = await llm.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": PROMPT_TRANSLATE_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.7,
        max_tokens=300,
    )
    image_prompt = (translate_resp.choices[0].message.content or "").strip()
    logger.info("Image prompt translated: %s", image_prompt[:200])

    # 第 2 步：调用图像生成 API
    img_client = get_image_client()
    img_resp = await img_client.images.generate(
        model=settings.IMAGE_MODEL,
        prompt=image_prompt,
        size=settings.IMAGE_SIZE,
        n=1,
        response_format="url",
    )
    image_url = img_resp.data[0].url

    return {
        "image_url": image_url,
        "prompt_used": image_prompt,
        "poem_text": poem_text,
        "title": title,
    }


# ---------- 图生文：图片 → 诗词 ----------

VISION_POEM_SYSTEM = """你是一位精通中国古典诗词的AI诗人，同时拥有出色的视觉理解能力。
你将根据用户提供的图片内容，创作一首与画面意境相匹配的中国古典诗词。

创作要求：
1. 仔细观察图片中的景物、色调、氛围、季节等视觉元素
2. 将视觉元素转化为诗词意象
3. 创作一首符合古典诗词格律的作品（五言/七言绝句或律诗）
4. 注意押韵和意境的完整性

返回 JSON 格式：
{
  "title": "诗词标题",
  "genre": "体裁（如五言绝句、七言律诗等）",
  "content": ["第一句", "第二句", "第三句", "第四句"],
  "scene_description": "对图片画面的简要描述（中文，30字以内）",
  "translation": "白话译文",
  "appreciation": "简要赏析（50字以内）"
}

只返回 JSON，不要其他内容。"""


_ALLOWED_IMAGE_MIME = ("image/jpeg", "image/png", "image/webp")


def _validate_image_data(image_base64: str) -> None:
    """轻量校验：长度已由 pydantic 限制，这里校验 data URI 的 MIME 类型"""
    if not image_base64 or not image_base64.startswith("data:"):
        return
    header = image_base64.split(";", 1)[0]
    mime = header.split(":", 1)[1] if ":" in header else ""
    if mime and mime.lower() not in _ALLOWED_IMAGE_MIME:
        raise ValueError(f"不支持的图片格式: {mime}")


_MAX_IMAGE_EDGE = 1024  # 图片最大边长（像素），超出则等比缩放
_JPEG_QUALITY = 85  # 重编码 JPEG 质量


def _compress_image(image_base64: str, max_edge: int = _MAX_IMAGE_EDGE, quality: int = _JPEG_QUALITY) -> str:
    """解码 base64 图片，限制最大边长并重编码为 JPEG 以压缩体积。

    返回 data URI 字符串。若 Pillow 未安装则原样返回（优雅降级）。
    """
    try:
        from PIL import Image, ImageOps
    except ImportError:
        logger.warning("Pillow not installed, skip image compression")
        return image_base64

    data = image_base64
    if data.startswith("data:"):
        data = data.split(",", 1)[1] if "," in data else ""
    if not data:
        raise ValueError("空图片数据")

    try:
        raw = base64.b64decode(data)
    except Exception as e:
        raise ValueError(f"无效的 base64 图片数据: {e}") from e

    img = Image.open(io.BytesIO(raw))
    img = ImageOps.exif_transpose(img)  # 处理手机照片方向
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    if max(img.size) > max_edge:
        img.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


async def generate_poem_from_image(
    image_base64: str,
    style: str = "古风",
    emotion: str = "",
) -> Dict[str, Any]:
    """图生文：分析图片并创作诗词

    Args:
        image_base64: base64 编码的图片（含 data:image/... 前缀或纯 base64）
        style: 风格偏好
        emotion: 情感偏好（可选）

    Returns:
        {"poem": Poem, "scene_description": str}
    """
    _validate_image_data(image_base64)

    # 压缩体积（限制最大边长 + 重编码 JPEG），再构建 data URI
    image_base64 = _compress_image(image_base64)

    # 构建 data URI
    if not image_base64.startswith("data:"):
        image_base64 = f"data:image/jpeg;base64,{image_base64}"

    user_content = "请根据这张图片创作一首中国古典诗词。"
    if style:
        user_content += f"\n风格偏好：{style}"
    if emotion:
        user_content += f"\n情感基调：{emotion}"

    vision = get_vision_client()
    resp = await vision.chat.completions.create(
        model=settings.VISION_MODEL,
        messages=[
            {"role": "system", "content": VISION_POEM_SYSTEM},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_content},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_base64, "detail": "high"},
                    },
                ],
            },
        ],
        temperature=0.8,
        max_tokens=1000,
    )
    raw = (resp.choices[0].message.content or "").strip()
    logger.debug("Vision LLM raw response: %s", raw[:500])

    data = parse_llm_json(raw)

    content = data.get("content", [])
    if isinstance(content, str):
        content = [line.strip() for line in content.split("\n") if line.strip()]

    poem_id = f"vision-{int(time.time() * 1000)}"
    poem = Poem(
        id=poem_id,
        title=data.get("title", "观图有感"),
        author=Author(name="AI诗人", dynasty="现代", brief="AI 看图写诗，仅供参考"),
        dynasty="现代",
        genre=data.get("genre", style),
        content=content,
        analysis=Analysis(
            translation=data.get("translation", ""),
            appreciation=data.get("appreciation", ""),
            cultural="AI 根据图片创作，仅供学习参考。",
        ),
        tags=[],
    )

    return {
        "poem": poem,
        "scene_description": data.get("scene_description", ""),
    }
