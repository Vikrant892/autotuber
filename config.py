import os

# Video settings
VIDEO_WIDTH           = 1080
VIDEO_HEIGHT          = 1920
VIDEO_FPS             = 30
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
DB_FILE       = "data/jobs.db"

# API keys from environment
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PEXELS_API_KEY    = os.getenv("PEXELS_API_KEY", "")

# Dashboard
DASHBOARD_URL    = os.getenv("DASHBOARD_URL", "https://autotuber-dashboard.pages.dev")
DASHBOARD_SECRET = os.getenv("DASHBOARD_SECRET", "REDACTED_INGEST_SECRET")
```

---

**`requirements.txt`** — select all, paste this:
```
anthropic>=0.40.0
python-dotenv>=1.0.0
requests>=2.31.0
pytrends>=4.9.2
moviepy==1.0.3
edge-tts==6.1.9
google-api-python-client>=2.100.0
google-auth-oauthlib>=1.2.0
google-auth-httplib2>=0.2.0
flask>=3.0.0
Pillow>=10.0.0
APScheduler>=3.10.0
numpy>=1.24.0
imageio>=2.31.0
imageio-ffmpeg>=0.4.9
decorator>=4.4.2
tqdm>=4.65.0
