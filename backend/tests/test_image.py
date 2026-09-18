"""图片校验与压缩测试"""
import base64
import io

import pytest
from PIL import Image

from app.services.image_service import _validate_image_data, _compress_image


def _make_data_uri(width: int, height: int, mime: str = "image/png", fmt: str = "PNG") -> str:
    img = Image.new("RGB", (width, height), (180, 40, 40))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return f"data:{mime};base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def test_validate_allows_jpeg_png_webp():
    _validate_image_data("data:image/jpeg;base64,xxx")
    _validate_image_data("data:image/png;base64,xxx")
    _validate_image_data("data:image/webp;base64,xxx")


def test_validate_rejects_unknown_mime():
    with pytest.raises(ValueError):
        _validate_image_data("data:image/gif;base64,xxx")


def test_validate_skips_plain_base64():
    # 无 data: 前缀时跳过 MIME 校验（不抛异常）
    _validate_image_data("cGxhaW4tYmFzZTY0")


def test_compress_downscales_and_reencodes():
    data = _make_data_uri(2000, 1500)
    result = _compress_image(data, max_edge=256, quality=85)
    assert result.startswith("data:image/jpeg;base64,")

    payload = result.split(",", 1)[1]
    decoded = base64.b64decode(payload)
    img = Image.open(io.BytesIO(decoded))
    assert max(img.size) <= 256


def test_compress_keeps_small_images():
    data = _make_data_uri(100, 100)
    result = _compress_image(data, max_edge=256)
    payload = result.split(",", 1)[1]
    img = Image.open(io.BytesIO(base64.b64decode(payload)))
    assert img.size == (100, 100)  # 未放大


def test_compress_invalid_base64_raises():
    with pytest.raises(ValueError):
        _compress_image("abcde")
