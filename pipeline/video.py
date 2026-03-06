"""
pipeline/video.py
Upgraded: MoviePy → FFmpeg + ElevenLabs word timings + ASS pop subtitles
Background: Minecraft parkour footage (looped) — place at assets/minecraft_parkour.mp4
Output: 1080x1920 vertical, 60fps, H264, ready for YouTube Shorts
"""
import json
import logging
import os
import subprocess
from config import OUTPUT_DIR, VIDEO_FPS, VIDEO_WIDTH, VIDEO_HEIGHT, MINECRAFT_BG_PATH
from pipeline.subtitles import generate_ass

log = logging.getLogger(__name__)
W, H = VIDEO_WIDTH, VIDEO_HEIGHT


def _get_duration(path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return float(r.stdout.strip())


def build_video(voice_path: str, script_data: dict, job_id: str, topic: str) -> str:
    """
    Assembles final MP4:
    1. Loops Minecraft parkour background to audio length
    2. Crops/scales to 1080x1920 vertical
    3. Burns in ASS pop subtitles (word-by-word)
    4. Mixes ElevenLabs audio
    5. Fade in/out
    Returns path to final MP4.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    out_path      = os.path.join(OUTPUT_DIR, f"{job_id}_short.mp4")
    subs_path     = os.path.join(OUTPUT_DIR, f"{job_id}_subs.ass")
    timings_path  = os.path.join(OUTPUT_DIR, f"{job_id}_timings.json")

    # ── Load word timings saved by voice.py ────────────────────────────────────
    if not os.path.exists(timings_path):
        raise FileNotFoundError(
            f"Word timings not found: {timings_path}\n"
            "Make sure voice.py ran successfully first."
        )
    with open(timings_path) as f:
        word_timings = json.load(f)

    # ── Generate ASS pop subtitles ─────────────────────────────────────────────
    log.info(f"Generating pop subtitles ({len(word_timings)} words)...")
    generate_ass(word_timings, subs_path)

    # ── Check background footage ───────────────────────────────────────────────
    if not os.path.exists(MINECRAFT_BG_PATH):
        raise FileNotFoundError(
            f"Minecraft background not found: {MINECRAFT_BG_PATH}\n"
            "Download free Minecraft parkour footage and place it there.\n"
            "yt-dlp command: yt-dlp -f 'bestvideo[ext=mp4]' YOUR_URL -o assets/minecraft_parkour.mp4"
        )

    duration = _get_duration(voice_path)
    duration = min(duration, 58)
    log.info(f"Duration: {duration:.1f}s")

    fade = 0.4
    vf = ",".join([
        f"scale={W}:{H}:force_original_aspect_ratio=increase",
        f"crop={W}:{H}",
        # Slight darken so subtitles pop
        "colorlevels=romax=0.7:gomax=0.7:bomax=0.7",
        f"ass={subs_path}",
        f"fade=t=in:st=0:d={fade}",
        f"fade=t=out:st={duration - fade}:d={fade}",
    ])

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",       # loop background
        "-i", MINECRAFT_BG_PATH,
        "-i", voice_path,
        "-t", str(duration),
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",               # high quality
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        "-r", str(VIDEO_FPS),
        out_path,
    ]

    log.info("Rendering video with FFmpeg...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed:\n{result.stderr}")

    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    log.info(f"Video rendered: {out_path} ({size_mb:.1f} MB)")
    return out_path
