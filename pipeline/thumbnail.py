"""
Generates eye-catching YouTube thumbnails using Pillow.
Dark cinematic style with bold text.
"""
import os
import logging
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
from config import OUTPUT_DIR
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "REDACTED_PEXELS_KEY")

log = logging.getLogger(__name__)
W, H = 1080, 1920


def _get_bg_image(topic: str) -> Image.Image | None:
    """Fetch relevant background image from Pexels."""
    if not PEXELS_API_KEY:
        return None
    try:
        # Extract key noun from topic for search
        query = topic.split()[:3]
        query = " ".join(query)
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_API_KEY},
            params={"query": query, "per_page": 3, "orientation": "landscape"},
            timeout=10
        )
        if r.ok:
            photos = r.json()["photos"]
            if photos:
                img_url = photos[0]["src"]["large2x"]
                img_data = requests.get(img_url, timeout=15).content
                from io import BytesIO
                return Image.open(BytesIO(img_data)).convert("RGB")
    except Exception as e:
        log.warning(f"Pexels fetch failed: {e}")
    return None


def _make_gradient_bg() -> Image.Image:
    """Create dramatic dark gradient background as fallback."""
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        ratio = y / H
        r = int(10 + ratio * 20)
        g = int(5 + ratio * 10)
        b = int(30 + ratio * 20)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Add dramatic light effect
    for cx, cy, intensity in [(250, 200, 80), (900, 500, 60)]:
        for radius in range(200, 0, -5):
            alpha = int(intensity * (1 - radius/200) * 0.15)
            color = (255, 140, 50, alpha)
            overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(overlay).ellipse(
                [cx - radius, cy - radius, cx + radius, cy + radius],
                fill=color
            )
            img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    return img


def generate_thumbnail(
    main_text: str,
    subtitle: str,
    topic: str,
    job_id: str
) -> str:
    """Generates 1280x720 JPG thumbnail. Returns file path."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{job_id}_thumb.jpg")
    log.info("Generating thumbnail...")

    # Background
    bg = _get_bg_image(topic)
    if bg:
        bg = bg.resize((W, H), Image.LANCZOS)
        bg = ImageEnhance.Brightness(bg).enhance(0.35)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=2))
    else:
        bg = _make_gradient_bg()

    draw = ImageDraw.Draw(bg)

    # Dark overlay bottom half
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(H // 2, H):
        alpha = int(180 * (y - H // 2) / (H // 2))
        od.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(bg)

    # Try loading fonts, fall back to default
    try:
        font_xl  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
        font_lg  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_sm  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except:
        font_xl  = ImageFont.load_default()
        font_lg  = font_xl
        font_sm  = font_xl

    # Orange accent bar
    draw.rectangle([0, H - 8, W, H], fill=(255, 107, 53))

    # "HISTORY UNVEILED" channel branding top-left
    draw.text((30, 25), "HISTORY UNVEILED", font=font_sm, fill=(255, 107, 53))

    # Main thumbnail text (wrapped)
    lines = textwrap.wrap(main_text.upper(), width=18)
    y_start = H // 2 - len(lines) * 55
    for i, line in enumerate(lines[:3]):
        y = y_start + i * 100
        # Shadow
        draw.text((44, y + 4), line, font=font_xl, fill=(0, 0, 0, 180))
        # Main text
        draw.text((40, y), line, font=font_xl, fill=(255, 255, 255))

    # Subtitle
    if subtitle:
        sub_y = y_start + len(lines[:3]) * 100 + 10
        draw.text((42, sub_y + 2), subtitle.upper(), font=font_lg, fill=(0, 0, 0, 150))
        draw.text((40, sub_y), subtitle.upper(), font=font_lg, fill=(255, 200, 100))

    bg.save(out_path, "JPEG", quality=95)
    log.info(f"Thumbnail saved: {out_path}")
    return out_path
