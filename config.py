import os

# Video settings
VIDEO_WIDTH          = 1080
VIDEO_HEIGHT         = 1920
VIDEO_FPS            = 30
VIDEO_DURATION_TARGET = 55

# Voice settings
VOICE_NAME  = "en-US-GuyNeural"
VOICE_SPEED = "+15%"

# Pipeline settings
VIDEOS_PER_DAY = 7
NICHE          = "History & Facts"

# Paths
OUTPUT_DIR    = "output"
THUMBNAIL_DIR = "output/thumbnails"
DB_FILE = DB_PATH

# API keys from environment
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PEXELS_API_KEY    = os.getenv("PEXELS_API_KEY", "")

# Dashboard
DASHBOARD_URL    = os.getenv("DASHBOARD_URL", "https://autotuber-dashboard.pages.dev")
DASHBOARD_SECRET = os.getenv("DASHBOARD_SECRET", "REDACTED_INGEST_SECRET")
