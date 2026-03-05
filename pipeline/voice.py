"""
Converts narration text to MP3 using Microsoft Edge TTS.
Completely free, no API key needed, sounds very natural.
"""
import asyncio
import logging
import os
import edge_tts
from config import VOICE_NAME, VOICE_SPEED, OUTPUT_DIR

log = logging.getLogger(__name__)


async def _synthesise(text: str, output_path: str) -> None:
    communicate = edge_tts.Communicate(text, VOICE_NAME, rate=VOICE_SPEED)
    await communicate.save(output_path)


def generate_voice(text: str, job_id: str) -> str:
    """
    Generates MP3 voiceover from text.
    Returns path to MP3 file.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{job_id}_voice.mp3")

    log.info(f"Generating voiceover ({len(text)} chars)...")
    asyncio.run(_synthesise(text, out_path))

    size_kb = os.path.getsize(out_path) // 1024
    log.info(f"Voiceover saved: {out_path} ({size_kb}KB)")
    return out_path


def get_available_voices() -> list:
    """List available Microsoft TTS voices."""
    async def _list():
        voices = await edge_tts.list_voices()
        return [v for v in voices if v["Locale"].startswith("en-")]

    return asyncio.run(_list())
