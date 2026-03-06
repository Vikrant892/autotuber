"""
pipeline/voice.py
Upgraded: Microsoft Edge TTS → ElevenLabs (word-level timestamps)
Saves audio MP3 + word timings JSON side-by-side in OUTPUT_DIR
"""
import base64
import json
import logging
import os
import requests
from config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, OUTPUT_DIR

log = logging.getLogger(__name__)

MODEL_ID = "eleven_multilingual_v2"

import asyncio
import logging
import os
import edge_tts
from config import VOICE_NAME, VOICE_SPEED, OUTPUT_DIR

log = logging.getLogger(__name__)


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
    
def generate_voice(text: str, job_id: str) -> str:
    """
    Generates ElevenLabs voiceover from text.
    Saves:
      {job_id}_voice.mp3     — audio file
      {job_id}_timings.json  — word-level timestamps (read by video.py)
    Returns path to MP3.
    """
    if not ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY not set in .env")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/with-timestamps"

    headers = {
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }

    payload = {
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.85,
            "style": 0.3,
            "use_speaker_boost": True,
        },
    }

    log.info(f"Calling ElevenLabs TTS ({len(text)} chars)...")
    response = requests.post(url, headers=headers, json=payload, timeout=60)

    if response.status_code != 200:
        raise RuntimeError(
            f"ElevenLabs API error {response.status_code}: {response.text}"
        )

    data = response.json()

    # ── Save audio ─────────────────────────────────────────────────────────────
    audio_bytes = base64.b64decode(data["audio_base64"])
    audio_path  = os.path.join(OUTPUT_DIR, f"{job_id}_voice.mp3")
    with open(audio_path, "wb") as f:
        f.write(audio_bytes)

    # ── Extract + save word timings ────────────────────────────────────────────
    word_timings  = _char_to_word_timings(data["alignment"])
    timings_path  = os.path.join(OUTPUT_DIR, f"{job_id}_timings.json")
    with open(timings_path, "w") as f:
        json.dump(word_timings, f)

    size_kb = os.path.getsize(audio_path) // 1024
    log.info(f"Voice saved: {audio_path} ({size_kb} KB), {len(word_timings)} words timed")
    return audio_path


def _char_to_word_timings(alignment: dict) -> list[dict]:
    """Convert ElevenLabs character-level timestamps → word-level."""
    chars  = alignment["characters"]
    starts = alignment["character_start_times_seconds"]
    ends   = alignment["character_end_times_seconds"]

    words        = []
    current_word = ""
    word_start   = None

    for char, start, end in zip(chars, starts, ends):
        if char in (" ", "\n"):
            if current_word.strip():
                words.append({"word": current_word.strip(), "start": word_start, "end": end})
            current_word = ""
            word_start   = None
        else:
            if word_start is None:
                word_start = start
            current_word += char

    if current_word.strip():
        words.append({"word": current_word.strip(), "start": word_start, "end": ends[-1]})

    return words


def get_available_voices() -> list:
    """List available ElevenLabs voices."""
    if not ELEVENLABS_API_KEY:
        return []
    r = requests.get(
        "https://api.elevenlabs.io/v1/voices",
        headers={"xi-api-key": ELEVENLABS_API_KEY},
        timeout=15,
    )
    if r.ok:
        return [{"name": v["name"], "id": v["voice_id"]} for v in r.json().get("voices", [])]
    return []
