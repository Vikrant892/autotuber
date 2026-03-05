"""
Builds vertical 1080x1920 YouTube Short (55 seconds max).
Fast cuts, large text overlays, cinematic look.
"""
import os
import logging
import requests
import tempfile
from config import OUTPUT_DIR, VIDEO_FPS, VIDEO_WIDTH, VIDEO_HEIGHT, PEXELS_API_KEY

log = logging.getLogger(__name__)


def _fetch_clip(keyword: str) -> str | None:
    """Download one relevant vertical/square Pexels clip."""
    if not PEXELS_API_KEY:
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": PEXELS_API_KEY},
            params={"query": keyword, "per_page": 5, "orientation": "portrait", "size": "medium"},
            timeout=15
        )
        if not r.ok:
            # fallback landscape
            r = requests.get(
                "https://api.pexels.com/videos/search",
                headers={"Authorization": PEXELS_API_KEY},
                params={"query": keyword, "per_page": 5, "size": "medium"},
                timeout=15
            )
        videos = r.json().get("videos", [])
        if not videos:
            return None
        files = videos[0].get("video_files", [])
        src = next((f["link"] for f in files if f.get("quality") in ("hd","sd")), None)
        if not src:
            return None
        tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        tmp.write(requests.get(src, timeout=60).content)
        tmp.close()
        log.info(f"Clip downloaded: {keyword}")
        return tmp.name
    except Exception as e:
        log.warning(f"Pexels clip failed: {e}")
        return None


def build_video(voice_path: str, script_data: dict, job_id: str, topic: str) -> str:
    """Renders vertical 1080x1920 Short. Returns output path."""
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, ColorClip,
        TextClip, CompositeVideoClip, concatenate_videoclips
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{job_id}_short.mp4")

    voice    = AudioFileClip(voice_path)
    duration = min(voice.duration, 58)  # hard cap 58s to be safe
    log.info(f"Short duration: {duration:.1f}s")

    W, H = VIDEO_WIDTH, VIDEO_HEIGHT   # 1080 x 1920

    # ── Background clip ──────────────────────────────────────────────────────
    keyword  = script_data.get("search_keyword", topic)
    clip_path = _fetch_clip(keyword)

    if clip_path:
        try:
            raw = VideoFileClip(clip_path)
            # Crop to vertical: take center square then scale up
            rw, rh = raw.size
            if rw > rh:
                # landscape → crop centre to square
                margin = (rw - rh) // 2
                raw = raw.crop(x1=margin, x2=rw - margin)
            bg = raw.resize((W, H))
            # Loop if too short
            if bg.duration < duration:
                loops = int(duration / bg.duration) + 1
                from moviepy.editor import concatenate_videoclips
                bg = concatenate_videoclips([bg] * loops)
            bg = bg.subclip(0, duration)
        except Exception as e:
            log.warning(f"Clip processing failed: {e}")
            bg = ColorClip((W, H), color=(8, 5, 18), duration=duration)
    else:
        bg = ColorClip((W, H), color=(8, 5, 18), duration=duration)

    # Dark overlay
    overlay = ColorClip((W, H), color=(0, 0, 0), duration=duration).set_opacity(0.5)

    # ── Text layers ───────────────────────────────────────────────────────────
    layers = [bg, overlay]

    # Top: channel name
    ch = (TextClip("HISTORY UNVEILED", fontsize=42, color="#FF6B35",
                   font="DejaVu-Sans-Bold", method="label")
          .set_position(("center", 80)).set_duration(duration).set_opacity(0.9))
    layers.append(ch)

    # Hook text (first 8 seconds, large, centred)
    hook_text = script_data.get("hook", "")
    if hook_text:
        hook = (TextClip(hook_text, fontsize=68, color="white",
                         font="DejaVu-Sans-Bold", method="caption",
                         size=(W - 80, None), align="center")
                .set_position("center").set_start(0).set_duration(min(8, duration))
                .crossfadein(0.2).crossfadeout(0.3))
        layers.append(hook)

    # Body text (after hook, smaller)
    body_text = script_data.get("body", "")
    if body_text and duration > 10:
        body = (TextClip(body_text, fontsize=52, color="white",
                         font="DejaVu-Sans", method="caption",
                         size=(W - 100, None), align="center")
                .set_position(("center", H // 2 - 60))
                .set_start(8).set_duration(duration - 12)
                .crossfadein(0.3).crossfadeout(0.3))
        layers.append(body)

    # CTA bottom
    cta_text = script_data.get("cta", "Follow for more!")
    cta = (TextClip(cta_text, fontsize=48, color="#FF6B35",
                    font="DejaVu-Sans-Bold", method="caption",
                    size=(W - 80, None), align="center")
           .set_position(("center", H - 220))
           .set_start(max(0, duration - 6)).set_duration(6)
           .crossfadein(0.3))
    layers.append(cta)

    # Orange bottom bar
    from moviepy.editor import ImageClip
    import numpy as np
    bar_arr = np.zeros((8, W, 3), dtype=np.uint8)
    bar_arr[:, :] = [255, 107, 53]
    bar = (ImageClip(bar_arr, duration=duration)
           .set_position(("left", H - 8)))
    layers.append(bar)

    # ── Compose + render ──────────────────────────────────────────────────────
    final = CompositeVideoClip(layers, size=(W, H)).set_duration(duration)
    final = final.set_audio(voice.subclip(0, duration))

    log.info("Rendering Short...")
    final.write_videofile(
        out_path, fps=VIDEO_FPS,
        codec="libx264", audio_codec="aac",
        temp_audiofile=f"/tmp/{job_id}_a.m4a",
        remove_temp=True, verbose=False, logger=None,
        preset="fast",
    )

    if clip_path:
        try: os.unlink(clip_path)
        except: pass

    size_mb = os.path.getsize(out_path) / 1024 / 1024
    log.info(f"Short rendered: {out_path} ({size_mb:.1f}MB)")
    return out_path
