import os, logging, requests, tempfile
import numpy as np
from config import OUTPUT_DIR, VIDEO_FPS, VIDEO_WIDTH, VIDEO_HEIGHT, PEXELS_API_KEY

log = logging.getLogger(__name__)
W, H = VIDEO_WIDTH, VIDEO_HEIGHT


def _fetch_clip(keyword):
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
                src = next((f["link"] for f in files if f.get("quality") in ("hd", "sd")), None)
                if not src:
                    continue
                tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
                tmp.write(requests.get(src, timeout=60).content)
                tmp.close()
                return tmp.name
        except Exception as e:
            log.warning(f"Pexels failed: {e}")
    return None


def _gradient(t, duration):
    frame = np.zeros((H, W, 3), dtype=np.uint8)
    p = t / max(duration, 1)
    frame[:, :] = [int(8 + 12*np.sin(p*np.pi)), int(4 + 6*np.sin(p*np.pi+1)), int(20 + 15*np.sin(p*np.pi+2))]
    return frame


def build_video(voice_path, script_data, job_id, topic):
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, ColorClip, TextClip,
        CompositeVideoClip, concatenate_videoclips, VideoClip
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{job_id}_short.mp4")

    voice = AudioFileClip(voice_path)
    duration = min(voice.duration, 58)
    log.info(f"Duration: {duration:.1f}s")

    clip_path = _fetch_clip(script_data.get("search_keyword", topic))

    if clip_path:
        try:
            raw = VideoFileClip(clip_path)
            rw, rh = raw.size
            if rw > rh:
                margin = (rw - rh) // 2
                raw = raw.crop(x1=margin, x2=rw - margin)
            bg = raw.resize((W, H))
            if bg.duration < duration:
                bg = concatenate_videoclips([bg] * (int(duration / bg.duration) + 2))
            bg = bg.subclip(0, duration)
        except Exception as e:
            log.warning(f"Clip failed: {e}")
            bg = VideoClip(lambda t: _gradient(t, duration), duration=duration).set_fps(VIDEO_FPS)
    else:
        bg = VideoClip(lambda t: _gradient(t, duration), duration=duration).set_fps(VIDEO_FPS)

    dark = ColorClip((W, H), color=(0, 0, 0), duration=duration).set_opacity(0.55)
    layers = [bg, dark]

    layers.append(ColorClip((W, 8), color=(255, 107, 53), duration=duration).set_position(("left", 0)))
    layers.append(ColorClip((W, 8), color=(255, 107, 53), duration=duration).set_position(("left", H - 8)))

    layers.append(
        TextClip("HISTORY UNVEILED", fontsize=38, color="#FF6B35",
                 font="DejaVu-Sans-Bold", method="label")
        .set_position(("center", 55)).set_duration(duration).set_opacity(0.9)
    )

    hook_text = script_data.get("hook", "")
    if hook_text:
        layers.append(
            TextClip(hook_text, fontsize=70, color="white", font="DejaVu-Sans-Bold",
                     method="caption", size=(W - 80, None), align="center",
                     stroke_color="black", stroke_width=3)
            .set_position(("center", H // 2 - 200))
            .set_start(0).set_duration(7).crossfadein(0.2).crossfadeout(0.4)
        )

    body_text = script_data.get("body", "")
    if body_text:
        first = body_text.split(".")[0].strip() + "."
        layers.append(
            ColorClip((W - 60, 220), color=(255, 107, 53), duration=4)
            .set_position(("center", H // 2 - 110))
            .set_start(7).set_opacity(0.92).crossfadein(0.25).crossfadeout(0.3)
        )
        layers.append(
            TextClip(first, fontsize=46, color="white", font="DejaVu-Sans-Bold",
                     method="caption", size=(W - 130, None), align="center")
            .set_position(("center", H // 2 - 100))
            .set_start(7).set_duration(4).crossfadein(0.25).crossfadeout(0.3)
        )

    if body_text and duration > 14:
        layers.append(
            TextClip(body_text, fontsize=50, color="white", font="DejaVu-Sans",
                     method="caption", size=(W - 80, None), align="center",
                     stroke_color="black", stroke_width=2)
            .set_position(("center", H // 2 - 100))
            .set_start(11).set_duration(max(4, duration - 17))
            .crossfadein(0.4).crossfadeout(0.4)
        )

    cta_text = script_data.get("cta", "Follow for more!")
    cta_start = max(duration - 6, duration * 0.75)
    layers.append(
        ColorClip((W, 160), color=(15, 15, 35), duration=6)
        .set_position(("left", H - 180)).set_start(cta_start)
        .set_opacity(0.88).crossfadein(0.4)
    )
    layers.append(
        TextClip(cta_text, fontsize=50, color="#FF6B35", font="DejaVu-Sans-Bold",
                 method="caption", size=(W - 60, None), align="center",
                 stroke_color="black", stroke_width=2)
        .set_position(("center", H - 168))
        .set_start(cta_start).set_duration(6).crossfadein(0.4)
    )

    def progress_frame(t):
        frame = np.zeros((12, W, 3), dtype=np.uint8)
        filled = int(W * (t / duration))
        frame[:, :filled] = [255, 107, 53]
        frame[:, filled:] = [30, 30, 50]
        return frame

    layers.append(VideoClip(progress_frame, duration=duration).set_fps(VIDEO_FPS).set_position(("left", H - 20)))

    final = (CompositeVideoClip(layers, size=(W, H))
             .set_duration(duration)
             .set_audio(voice.subclip(0, duration)))

    log.info("Rendering...")
    final.write_videofile(
        out_path, fps=VIDEO_FPS, codec="libx264", audio_codec="aac",
        temp_audiofile=f"/tmp/{job_id}_a.m4a", remove_temp=True,
        verbose=False, logger=None, preset="fast", threads=4,
    )

    if clip_path:
        try: os.unlink(clip_path)
        except: pass

    log.info(f"Done: {out_path}")
    return out_path
