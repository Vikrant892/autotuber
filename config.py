import os
from dotenv import load_dotenv
load_dotenv()

# ── APIs ──────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY     = os.getenv("ANTHROPIC_API_KEY", "")
ELEVENLABS_API_KEY    = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID   = os.getenv("ELEVENLABS_VOICE_ID", "nPczCjzI2devNBz1zQrb")  # Brian — deep/punchy
YOUTUBE_CLIENT_ID     = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")

# ── Channel settings ──────────────────────────────────────────────────────────
NICHE           = "History & Facts"
CHANNEL_NAME    = "History Unveiled"
VIDEOS_PER_DAY  = 1
SCHEDULE_HOUR   = 7    # 7am
SCHEDULE_TZ     = "Australia/Adelaide"

# ── Video settings ────────────────────────────────────────────────────────────
VIDEO_DURATION_TARGET = 55   # 55 seconds — YouTube Shorts
VIDEO_FPS             = 60  # 60fps — Shorts algorithm loves this
VIDEO_WIDTH           = 1080
VIDEO_HEIGHT          = 1920

# ── Paths ─────────────────────────────────────────────────────────────────────
OUTPUT_DIR         = "output"
MINECRAFT_BG_PATH  = os.getenv("MINECRAFT_BG_PATH", "assets/minecraft_parkour.mp4")
LOG_DIR       = "logs"
DATA_DIR      = "data"
TOKEN_FILE    = "data/youtube_token.json"
OAUTH_FILE    = "data/client_secrets.json"
DB_FILE       = "data/autotuber.db"

# ── YouTube upload defaults ───────────────────────────────────────────────────
YT_CATEGORY_ID  = "27"  # Education   # Education
YT_PRIVACY      = "public"
YT_LANGUAGE     = "en"

# ── Topics bank (fallback if trends fail) ────────────────────────────────────
FALLBACK_TOPICS = [
    "The real reason the Roman Empire collapsed",
    "Ancient Egyptian technology that still baffles scientists",
    "The lost city of Pompeii — what they never taught you",
    "Why the Mongol Empire was the largest in history",
    "The secret societies that shaped medieval Europe",
    "How ancient Greeks invented democracy",
    "The truth about Viking exploration in America",
    "Ancient Chinese inventions that changed the world",
    "The mystery of the Indus Valley Civilisation",
    "How the Black Death changed Europe forever",
    "The real story behind the pyramids of Giza",
    "Why ancient Rome had no middle class",
    "The forgotten women rulers of ancient history",
    "How Alexander the Great built his empire in 10 years",
    "The ancient trade routes that connected the world",
]
