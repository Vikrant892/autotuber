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
DASHBOARD_SECRET      = os.getenv("DASHBOARD_SECRET", "REDACTED_INGEST_SECRET")
