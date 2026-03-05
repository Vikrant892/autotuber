"""
Animated vertical Short builder — moviepy 1.0.3 compatible.
Features: zoom-in text, animated captions, colour flashes, cinematic cuts.
"""
import os, logging, requests, tempfile
import numpy as np
from config import OUTPUT_DIR, VIDEO_FPS, VIDEO_WIDTH, VIDEO_HEIGHT, PEXELS_API_KEY

log = logging.getLogger(__name__)
W, H = VIDEO_WIDTH, VIDEO_HEIGHT


def _fetch_clip(keyword: str):
    if not PEXELS_API_KEY:
        return None
    for orientation in ("portrait", "landscape"):
        try:
            r = requests.get(
                "https://api.pexels.com/videos/search",
                headers={"Authorization": PEXELS_API_KEY},
                params={"query": keyword, "per_page": 5,
                        "orientation": orientation, "size": "medium"},
                timeout=15
            )
            videos = r.json().get("videos", []) if r.ok else []
            for vid in videos:
                files = vid.get("video_files", [])
                src = next((f["link"] for f in files
                            if f.get("quality") in ("hd", "sd")), None)
                if not src:
                    continue
                tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
                tmp.write(requests.get(src, timeout=60).content)
                tmp.close()
                log.info(f"Clip downloaded ({orientation})")
                return tmp.name
        except Exception as e:
            log.warning(f"Pexels {orientation} failed: {e}")
    return None


def _make_gradient_frame(t, duration):
    frame = np.zeros((H, W, 3), dtype=np.uint8)
    progress = t / max(duration, 1)
    r = int(8  + 12 * np.sin(progress * np.pi))
    g = int(4  + 6  * np.sin(progress * np.pi + 1))
    b = int(20 + 15 * np.sin(progress * np.pi + 2))
    frame[:, :] = [r, g, b]
    for y in range(0, H, 4):
        edge = min(y, H - y) / (H * 0.3)
        factor = min(1.0, edge)
        frame[y:y+4] = (frame[y:y+4] * factor).astype(np.uint8)
    return frame


def build_video(voice_path: str, script_data: dict,
                job_id: str, topic: str) -> str:

    from moviepy.editor import (
        VideoFileClip, AudioFileClip, ImageClip,
        ColorClip, TextClip, CompositeVideoClip,
        concatenate_videoclips, VideoClip
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{job_id}_short.mp4")

    voice    = AudioFileClip(voice_path)
    duration = min(voice.duration, 58)
    log.info(f"Duration: {duration:.1f}s")

    keyword   = script_data.get("search_keyword", topic)
    clip_path = _fetch_clip(keyword)

    if clip_path:
        try:
            raw = VideoFileClip(clip_path)
            rw, rh = raw.size
            if rw > rh:
                margin = (rw - rh) // 2
                raw = raw.crop(x1=margin, x2=rw - margin)
            bg = raw.resize((W, H))
            if bg.duration < duration:
                loops = int(duration / bg.duration) + 2
                bg = concatenate_videoclips([bg] * loops)
            bg = bg.subclip(0, duration)
        except Exception as e:
            log.warning(f"Clip load failed: {e}")
            bg = VideoClip(lambda t: _make_gradient_frame(t, duration),
                           duration=duration).set_fps(VIDEO_FPS)
    else:
        bg = VideoClip(lambda t: _make_gradient_frame(t, duration),
                       duration=duration).set_fps(VIDEO_FPS)

    dark = ColorClip((W, H), color=(0, 0, 0), duration=duration).set_opacity(0.55)
    layers = [bg, dark]

    # Orange bars top and bottom
    top_bar    = ColorClip((W, 8), color=(255, 107, 53), duration=duration).set_position(("left", 0))
    bottom_bar = ColorClip((W, 8), color=(255, 107, 53), duration=duration).set_position(("left", H - 8))
    layers += [top_bar, bottom_bar]

    # Channel name
    wm = (TextClip("HISTORY UNVEILED", fontsize=38, color="#FF6B35",
                   font="DejaVu-Sans-Bold", method="label")
          .set_position(("center", 55))
          .set_duration(duration)
          .set_opacity(0.9))
    layers.append(wm)

    # Hook — large centred text (0–7s)
    hook_text = script_data.get("hook", "")
    if hook_text:
        hook_clip = (TextClip(hook_text, fontsize=70, color="white",
                              font="DejaVu-Sans-Bold", method="caption",
                              size=(W - 80, None), align="center",
                              stroke_color="black", stroke_width=3)
                     .set_position(("center", H // 2 - 200))
                     .set_start(0).set_duration(7)
                     .crossfadein(0.2).crossfadeout(0.4))
        layers.append(hook_clip)

    # Orange fact card flash (7–11s)
    body_text = script_data.get("body", "")
    if body_text:
        first_sentence = body_text.split(".")[0].strip() + "."
        fact_bg = (ColorClip((W - 60, 220), color=(255, 107, 53), duration=4)
                   .set_position(("center", H // 2 - 110))
                   .set_start(7).set_opacity(0.92)
                   .crossfadein(0.25).crossfadeout(0.3))
        layers.append(fact_bg)

        fact_txt = (TextClip(first_sentence, fontsize=46, color="white",
                             font="DejaVu-Sans-Bold", method="caption",
                             size=(W - 130, None), align="center")
                    .set_position(("center", H // 2 - 100))
                    .set_start(7).set_duration(4)
                    .crossfadein(0.25).crossfadeout(0.3))
        layers.append(fact_txt)

    # Body text (11s → end-6s)
    if body_text and duration > 14:
        body_clip = (TextClip(body_text, fontsize=50, color="white",
                              font="DejaVu-Sans", method="caption",
                              size=(W - 80, None), align="center",
                              stroke_color="black", stroke_width=2)
                     .set_position(("center", H // 2 - 100))
                     .set_start(11).set_duration(max(4, duration - 17))
                     .crossfadein(0.4).crossfadeout(0.4))
        layers.append(body_clip)

    # CTA dark panel + text (last 6s)
    cta_text  = script_data.get("cta", "Follow for more! 🔔")
    cta_start = max(duration - 6, duration * 0.75)

    cta_bg = (ColorClip((W, 160), color=(15, 15, 35), duration=6)
              .set_position(("left", H - 180))
              .set_start(cta_start).set_opacity(0.88)
              .crossfadein(0.4))
    layers.append(cta_bg)

    cta = (TextClip(cta_text, fontsize=50, color="#FF6B35",
                    font="DejaVu-Sans-Bold", method="caption",
                    size=(W - 60, None), align="center",
                    stroke_color="black", stroke_width=2)
           .set_position(("center", H - 168))
           .set_start(cta_start).set_duration(6)
           .crossfadein(0.4))
    layers.append(cta)

    # Animated progress bar
    def progress_frame(t):
        frame = np.zeros((12, W, 3), dtype=np.uint8)
        filled = int(W * (t / duration))
        frame[:, :filled] = [255, 107, 53]
        frame[:, filled:] = [30, 30, 50]
        return frame

    progress = (VideoClip(progress_frame, duration=duration)
                .set_fps(VIDEO_FPS)
                .set_position(("left", H - 20)))
    layers.append(progress)

    # Compose
    final = (CompositeVideoClip(layers, size=(W, H))
             .set_duration(duration)
             .set_audio(voice.subclip(0, duration)))

    log.info("Rendering animated Short...")
    final.write_videofile(
        out_path, fps=VIDEO_FPS,
        codec="libx264", audio_codec="aac",
        temp_audiofile=f"/tmp/{job_id}_a.m4a",
        remove_temp=True, verbose=False, logger=None,
        preset="fast", threads=4,
    )

    if clip_path:
        try: os.unlink(clip_path)
        except: pass

    size_mb = os.path.getsize(out_path) / 1024 / 1024
    log.info(f"Short rendered: {out_path} ({size_mb:.1f}MB)")
    return out_path
```

---

Also update **`requirements.txt`** — add this one line at the bottom:
```
opencv-python-headless>=4.8.0
