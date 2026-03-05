"""
Generates YouTube Shorts script (45-55 seconds max).
Fast, punchy, single shocking history fact per video.
"""
import json
import logging
import anthropic
from config import ANTHROPIC_API_KEY

log = logging.getLogger(__name__)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def generate_script(topic: str) -> dict:
    """
    Returns dict with title, script segments, description, tags, thumbnail info.
    Total narration must be 45-55 seconds when spoken at fast pace.
    """
    log.info(f"Writing SHORT script for: {topic}")

    prompt = f"""You write scripts for viral YouTube Shorts about History & Facts.

Topic: {topic}

Rules:
- Total spoken word count: 120-150 words MAX (45-55 seconds at fast speech)
- Hook must land in first 3 seconds or viewer swipes away
- One single shocking fact — do NOT cover multiple things
- End with "Follow for more" or similar CTA
- Vertical video (9:16) — write for mobile viewers

Return ONLY valid JSON, no markdown, no explanation:

{{
  "title": "YouTube Shorts title with #Shorts hashtag (max 60 chars, use shock/mystery)",
  "hook": "Opening 1-2 sentences. Shocking fact or question. Max 20 words.",
  "body": "Main content expanding the hook. Max 90 words. Fast, punchy sentences.",
  "cta": "2-sentence outro. Like + Follow CTA. Max 15 words.",
  "description": "Short description for YouTube (50-80 words) + hashtags: #Shorts #History #Facts #HistoryFacts #AncientHistory",
  "tags": ["Shorts","History","Facts","HistoryFacts","AncientHistory","DidYouKnow","HistoryShorts","FunFacts","AmazingFacts","LearnOnTikTok"],
  "thumbnail_text": "2-4 WORD HOOK IN CAPS",
  "thumbnail_subtitle": "2-3 word teaser",
  "search_keyword": "2-3 word Pexels search term for relevant background footage (e.g. 'ancient rome ruins')"
}}"""

    msg = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    data = json.loads(raw)
    log.info(f"Short script: {data['title']} ({len(get_full_narration(data).split())} words)")
    return data


def get_full_narration(script_data: dict) -> str:
    """Concatenate hook + body + CTA for TTS."""
    return " ".join([
        script_data.get("hook", ""),
        script_data.get("body", ""),
        script_data.get("cta", "")
    ])
