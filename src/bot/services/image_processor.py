"""
Serramentista — Pre-processing foto
Resize, compressione e fix orientamento EXIF prima dell'analisi AI.
"""

import io
import structlog
from PIL import Image, ExifTags, ImageOps

log = structlog.get_logger()

# Dimensione massima lato lungo (pixel) — bilancio qualità/costo API
MAX_DIMENSION = 2048
# Qualità JPEG output
JPEG_QUALITY = 85
# Peso massimo output (bytes) — ~1.5 MB
MAX_FILE_SIZE = 1_500_000


def fix_exif_orientation(img: Image.Image) -> Image.Image:
    """Corregge l'orientamento basato su EXIF (foto scattate in verticale)."""
    try:
        return ImageOps.exif_transpose(img)
    except Exception:
        return img


def resize_if_needed(img: Image.Image) -> Image.Image:
    """Ridimensiona se eccede MAX_DIMENSION, mantenendo aspect ratio."""
    w, h = img.size
    if max(w, h) <= MAX_DIMENSION:
        return img

    if w > h:
        new_w = MAX_DIMENSION
        new_h = int(h * (MAX_DIMENSION / w))
    else:
        new_h = MAX_DIMENSION
        new_w = int(w * (MAX_DIMENSION / h))

    log.info("image.resize", original=f"{w}x{h}", new=f"{new_w}x{new_h}")
    return img.resize((new_w, new_h), Image.LANCZOS)


def compress_to_jpeg(img: Image.Image, quality: int = JPEG_QUALITY) -> bytes:
    """Converte a JPEG con qualità controllata."""
    # Converti RGBA → RGB (JPEG non supporta alpha)
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    elif img.mode != "RGB":
        img = img.convert("RGB")

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def process_photo(raw_bytes: bytes) -> bytes:
    """
    Pipeline di pre-processing completa:
    1. Apre immagine
    2. Fix orientamento EXIF
    3. Resize se troppo grande
    4. Comprimi a JPEG
    5. Se ancora troppo pesante, riduci qualità

    Returns: bytes JPEG processati
    """
    img = Image.open(io.BytesIO(raw_bytes))
    original_size = len(raw_bytes)

    log.info(
        "image.process.start",
        size_kb=original_size // 1024,
        dimensions=f"{img.size[0]}x{img.size[1]}",
        mode=img.mode,
    )

    # 1. Fix orientamento EXIF
    img = fix_exif_orientation(img)

    # 2. Resize
    img = resize_if_needed(img)

    # 3. Comprimi
    output = compress_to_jpeg(img)

    # 4. Se ancora troppo pesante, riduci qualità progressivamente
    quality = JPEG_QUALITY
    while len(output) > MAX_FILE_SIZE and quality > 40:
        quality -= 10
        output = compress_to_jpeg(img, quality=quality)
        log.info("image.recompress", quality=quality, size_kb=len(output) // 1024)

    log.info(
        "image.process.done",
        original_kb=original_size // 1024,
        output_kb=len(output) // 1024,
        dimensions=f"{img.size[0]}x{img.size[1]}",
        quality=quality,
    )

    return output
