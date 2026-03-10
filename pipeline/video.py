import os, logging
import numpy as np
from config import OUTPUT_DIR, VIDEO_FPS, VIDEO_WIDTH, VIDEO_HEIGHT

log = logging.getLogger(__name__)
W, H = VIDEO_WIDTH, VIDEO_HEIGHT


def _bg_frame(t, duration):
    """Animated dark background with moving gradient."""
    frame = np.zeros((H, W, 3), dtype=np.uint8)
    p = t / max(duration, 1)
    # Shifting dark colours
    r = int(10 + 8  * np.sin(p * np.pi * 2))
    g = int(5  + 4  * np.sin(p * np.pi * 2 + 1))
    b = int(25 + 18 * np.sin(p * np.pi * 2 + 2))
    frame[:, :] = [r, g, b]
    # Vignette
    cx, cy = W // 2, H // 2
    Y, X = np.ogrid[:H, :W]
    dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
    vignette = np.clip(1 - dist / (max(W, H) * 0.75), 0.3, 1.0)
    frame = (frame * vignette[:, :, np.newaxis]).astype(np.uint8)
    return frame


def _scanlines_frame(t):
    """Subtle scanline overlay for cinematic feel."""
    frame = np.zeros((H, W, 3), dtype=np.uint8)
    frame[::4, :] = [20, 20, 20]
    return frame


def build_video(voice_path, script_data, job_id, topic):
    from moviepy.editor import (
        AudioFileClip, ColorClip, TextClip,
        CompositeVideoClip, VideoClip
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{job_id}_short.mp4")

    voice    = AudioFileClip(voice_path)
    duration = min(voice.duration, 58)
    log.info(f"Duration: {duration:.1f}s")

    # Animated background
    bg = VideoClip(lambda t: _bg_frame(t, duration),
                   duration=duration).set_fps(VIDEO_FPS)

    layers = [bg]

    # Top + bottom orange bars
    layers.append(ColorClip((W, 10), color=(255, 107, 53), duration=duration).set_position(("left", 0)))
    layers.append(ColorClip((W, 10), color=(255, 107, 53), duration=duration).set_position(("left", H - 10)))

    # Left accent line
    layers.append(ColorClip((6, H), color=(255, 107, 53), duration=duration).set_position((0, 0)).set_opacity(0.5))

    # Channel name top centre
    layers.append(
        TextClip("HISTORY UNVEILED", fontsize=40, color="#FF6B35",
                 font="DejaVu-Sans-Bold", method="label")
        .set_position(("center", 60))
        .set_duration(duration)
        .set_opacity(0.95)
    )

    # Episode number / date stamp top right
    from datetime import datetime
    stamp = datetime.now().strftime("#%j")
    layers.append(
        TextClip(stamp, fontsize=32, color="#555577",
                 font="DejaVu-Sans", method="label")
        .set_position((W - 120, 65))
        .set_duration(duration)
        .set_opacity(0.6)
    )

    hook_text = script_data.get("hook", "")
    body_text = script_data.get("body", "")
    cta_text  = script_data.get("cta", "Follow for more!")

    # ── HOOK (0-7s): huge white text, fades in fast ───────────────────────────
    if hook_text:
        # Shadow layer
        layers.append(
            TextClip(hook_text, fontsize=74, color="#111122",
                     font="DejaVu-Sans-Bold", method="caption",
                     size=(W - 60, None), align="center")
            .set_position((6, H // 2 - 244))
            .set_start(0).set_duration(7)
            .crossfadein(0.15).crossfadeout(0.3)
            .set_opacity(0.7)
        )
        # Main
        layers.append(
            TextClip(hook_text, fontsize=74, color="white",
                     font="DejaVu-Sans-Bold", method="caption",
                     size=(W - 60, None), align="center")
            .set_position(("center", H // 2 - 250))
            .set_start(0).set_duration(7)
            .crossfadein(0.15).crossfadeout(0.3)
        )

    # ── FACT CARD (7-12s): orange box ────────────────────────────────────────
    if body_text:
        first = body_text.split(".")[0].strip() + "."

        # Orange card background
        layers.append(
            ColorClip((W - 40, 250), color=(200, 75, 20), duration=5)
            .set_position((20, H // 2 - 125))
            .set_start(7)
            .set_opacity(0.95)
            .crossfadein(0.2).crossfadeout(0.25)
        )
        # Inner lighter stripe
        layers.append(
            ColorClip((W - 40, 8), color=(255, 140, 60), duration=5)
            .set_position((20, H // 2 - 125))
            .set_start(7)
            .crossfadein(0.2).crossfadeout(0.25)
        )
        layers.append(
            ColorClip((W - 40, 8), color=(255, 140, 60), duration=5)
            .set_position((20, H // 2 + 117))
            .set_start(7)
            .crossfadein(0.2).crossfadeout(0.25)
        )
        # Label "DID YOU KNOW"
        layers.append(
            TextClip("DID YOU KNOW?", fontsize=30, color="#FFD580",
                     font="DejaVu-Sans-Bold", method="label")
            .set_position(("center", H // 2 - 115))
            .set_start(7).set_duration(5)
            .crossfadein(0.2).crossfadeout(0.25)
        )
        # Fact text
        layers.append(
            TextClip(first, fontsize=50, color="white",
                     font="DejaVu-Sans-Bold", method="caption",
                     size=(W - 100, None), align="center")
            .set_position(("center", H // 2 - 70))
            .set_start(7).set_duration(5)
            .crossfadein(0.2).crossfadeout(0.25)
        )

    # ── BODY (12s → end-7s): white text with subtle bg ───────────────────────
    if body_text and duration > 16:
        body_dur = max(4, duration - 19)

        # Dark semi-transparent bg behind body text
        layers.append(
            ColorClip((W - 40, 420), color=(0, 0, 0), duration=body_dur)
            .set_position((20, H // 2 - 210))
            .set_start(12)
            .set_opacity(0.5)
            .crossfadein(0.35).crossfadeout(0.35)
        )
        layers.append(
            TextClip(body_text, fontsize=52, color="white",
                     font="DejaVu-Sans", method="caption",
                     size=(W - 90, None), align="center",
                     stroke_color="black", stroke_width=1)
            .set_position(("center", H // 2 - 200))
            .set_start(12).set_duration(body_dur)
            .crossfadein(0.35).crossfadeout(0.35)
        )

    # ── CTA (last 7s) ─────────────────────────────────────────────────────────
    cta_start = max(duration - 7, duration * 0.78)

    layers.append(
        ColorClip((W, 200), color=(8, 6, 20), duration=7)
        .set_position(("left", H - 210))
        .set_start(cta_start)
        .set_opacity(0.92)
        .crossfadein(0.3)
    )
    # Orange divider above CTA
    layers.append(
        ColorClip((W, 4), color=(255, 107, 53), duration=7)
        .set_position(("left", H - 210))
        .set_start(cta_start)
        .crossfadein(0.3)
    )
    layers.append(
        TextClip(cta_text, fontsize=52, color="#FF6B35",
                 font="DejaVu-Sans-Bold", method="caption",
                 size=(W - 60, None), align="center",
                 stroke_color="black", stroke_width=2)
        .set_position(("center", H - 195))
        .set_start(cta_start).set_duration(7)
        .crossfadein(0.3)
    )
    # Bell icon text
    layers.append(
        TextClip("🔔 Like & Subscribe", fontsize=36, color="#FFD580",
                 font="DejaVu-Sans", method="label")
        .set_position(("center", H - 90))
        .set_start(cta_start).set_duration(7)
        .crossfadein(0.3)
        .set_opacity(0.85)
    )

    # ── Progress bar ──────────────────────────────────────────────────────────
    def prog(t):
        f = np.zeros((14, W, 3), dtype=np.uint8)
        n = int(W * t / duration)
        f[:, :n] = [255, 107, 53]
        f[:, n:] = [25, 25, 45]
        return f

    layers.append(
        VideoClip(prog, duration=duration)
        .set_fps(VIDEO_FPS)
        .set_position(("left", H - 14))
    )

    # Compose
    final = (CompositeVideoClip(layers, size=(W, H))
             .set_duration(duration)
             .set_audio(voice.subclip(0, duration)))

    log.info("Rendering...")
    final.write_videofile(
        out_path, fps=VIDEO_FPS, codec="libx264", audio_codec="aac",
        temp_audiofile=f"/tmp/{job_id}_a.m4a", remove_temp=True,
        verbose=False, logger=None, preset="fast", threads=4,
    )

    log.info(f"Done: {out_path} ({os.path.getsize(out_path)//1024//1024}MB)")
    return out_path
