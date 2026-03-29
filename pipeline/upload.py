"""
Uploads video to YouTube using YouTube Data API v3.
Handles OAuth token refresh automatically.
"""
import os
import json
import logging
import requests
from pathlib import Path
from config import (TOKEN_FILE, OAUTH_FILE, YT_CATEGORY_ID,
                    YT_PRIVACY, YT_LANGUAGE)

log = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]


def _get_credentials():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            log.info("Refreshing YouTube token...")
            creds.refresh(Request())
        else:
            log.info("Running YouTube OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(OAUTH_FILE, SCOPES)
            creds = flow.run_local_server(port=8080, open_browser=True)

        # Save token
        os.makedirs(Path(TOKEN_FILE).parent, exist_ok=True)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        log.info("YouTube token saved.")

    return creds


def upload_video(
    video_path: str,
    thumbnail_path: str,
    title: str,
    description: str,
    tags: list[str],
) -> dict:
    """
    Uploads video + thumbnail to YouTube.
    Returns {"video_id": "...", "url": "..."}
    """
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds   = _get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    log.info(f"Uploading to YouTube: {title}")

    # Video metadata
    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags[:15],
            "categoryId": YT_CATEGORY_ID,
            "defaultLanguage": YT_LANGUAGE,
            "defaultAudioLanguage": YT_LANGUAGE,
        },
        "status": {
            "privacyStatus": YT_PRIVACY,
            "selfDeclaredMadeForKids": False,
        }
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=50 * 1024 * 1024  # 50MB chunks
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            log.info(f"Upload progress: {pct}%")

    video_id = response["id"]
    log.info(f"Video uploaded: https://youtube.com/watch?v={video_id}")

    # Set thumbnail
    if os.path.exists(thumbnail_path):
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
            ).execute()
            log.info("Thumbnail set.")
        except Exception as e:
            log.warning(f"Thumbnail upload failed: {e}")

    return {
        "video_id": video_id,
        "url": f"https://youtube.com/watch?v={video_id}",
        "title": title,
    }


def notify_dashboard(job_data: dict) -> None:
    """Notify Cloudflare dashboard after successful upload."""
    import os
    dashboard_url = os.getenv("DASHBOARD_URL", "https://autotuber-dashboard.pages.dev")
    secret = os.getenv("INGEST_SECRET")
    try:
        r = requests.post(
            f"{dashboard_url}/api/ingest",
            json=job_data,
            headers={"Authorization": f"Bearer {secret}", "Content-Type": "application/json"},
            timeout=10
        )
        log.info(f"Dashboard notified: {r.status_code}")
    except Exception as e:
        log.warning(f"Dashboard notify failed (non-fatal): {e}")
