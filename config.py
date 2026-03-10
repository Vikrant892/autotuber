import asyncio
import logging
import os
import edge_tts

log = logging.getLogger(__name__)

VOICE_NAME  = "en-US-GuyNeural"
VOICE_SPEED = "+15%"
OUTPUT_DIR  = "output"


async def _synthesise(text, output_path):
    communicate = edge_tts.Communicate(text, VOICE_NAME, rate=VOICE_SPEED)
    await communicate.save(output_path)


def generate_voice(text, job_id):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{job_id}_voice.mp3")
    log.info(f"Generating voiceover ({len(text)} chars)...")
    asyncio.run(_synthesise(text, out_path))
    size_kb = os.path.getsize(out_path) // 1024
    log.info(f"Voiceover saved: {out_path} ({size_kb}KB)")
    return out_path
