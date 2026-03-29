import os

VIDEO_WIDTH           = 1080
VIDEO_HEIGHT          = 1920
VIDEO_FPS             = 30
VIDEO_DURATION_TARGET = 55
VOICE_NAME            = "en-US-GuyNeural"
VOICE_SPEED           = "+15%"
VIDEOS_PER_DAY        = 7
NICHE                 = "History & Facts"
OUTPUT_DIR            = "output"
THUMBNAIL_DIR         = "output/thumbnails"
DB_FILE               = "data/jobs.db"
ANTHROPIC_API_KEY     = os.getenv("ANTHROPIC_API_KEY", "")
PEXELS_API_KEY        = os.getenv("PEXELS_API_KEY", "")
DASHBOARD_URL         = os.getenv("DASHBOARD_URL", "https://autotuber-dashboard.pages.dev")
DASHBOARD_SECRET      = os.getenv("DASHBOARD_SECRET")

FALLBACK_TOPICS = [
    "Ancient Roman gladiator secrets",
    "Egyptian pyramid hidden chambers",
    "Viking navigation mysteries",
    "Medieval plague doctors",
    "Ancient Greek inventors",
    "Mongol empire war tactics",
    "Ancient Chinese inventions",
    "Spartan warrior training",
    "Aztec human sacrifice rituals",
    "Byzantine empire secrets",
    "Ancient Mayan calendar truth",
    "Roman emperor assassination plots",
    "Medieval castle siege weapons",
    "Ancient Persian empire secrets",
    "Greek mythology hidden meanings",
]

TOKEN_FILE       = "data/youtube_token.json"
OAUTH_FILE       = "data/client_secrets.json"
YT_CATEGORY_ID   = "27"
YT_PRIVACY       = "public"
YT_LANGUAGE = "en"
