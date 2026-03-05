"""
Main orchestrator — runs one complete video pipeline:
Trend → Script → Voice → Video → Thumbnail → Upload
"""
import uuid
import logging
import os
import sys
from datetime import datetime
from pipeline import db, trends, script, voice, video, thumbnail, upload

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"logs/pipeline_{datetime.now().strftime('%Y%m%d')}.log")
    ]
)
log = logging.getLogger("orchestrator")
os.makedirs("logs", exist_ok=True)


def run_pipeline() -> dict:
    """Run one full video pipeline. Returns result dict."""
    job_id = str(uuid.uuid4())[:8]
    log.info(f"═══ Starting job {job_id} ═══")
    db.init_db()

    # ── 1. Find Topic ─────────────────────────────────────────────────────────
    try:
        log.info("Stage 1/6: Finding topic...")
        used = db.get_used_topics()
        topic = trends.get_topic(used)
        db.create_job(job_id, topic)
        db.add_log(job_id, "INFO", f"Topic selected: {topic}")
        db.update_job(job_id, stage="topic_found")
    except Exception as e:
        log.error(f"Topic finder failed: {e}")
        db.fail_job(job_id, f"Trend stage failed: {e}")
        return {"success": False, "error": str(e), "stage": "trends"}

    # ── 2. Generate Script ────────────────────────────────────────────────────
    try:
        log.info("Stage 2/6: Writing script...")
        db.update_job(job_id, stage="writing_script")
        script_data = script.generate_script(topic)
        narration   = script.get_full_narration(script_data)
        db.add_log(job_id, "INFO", f"Script written: {script_data['title']}")
        db.update_job(job_id, title=script_data["title"], stage="script_done")
    except Exception as e:
        log.error(f"Script generation failed: {e}")
        db.fail_job(job_id, f"Script stage failed: {e}")
        return {"success": False, "error": str(e), "stage": "script"}

    # ── 3. Generate Voice ─────────────────────────────────────────────────────
    try:
        log.info("Stage 3/6: Generating voiceover...")
        db.update_job(job_id, stage="generating_voice")
        voice_path = voice.generate_voice(narration, job_id)
        db.add_log(job_id, "INFO", f"Voice generated: {voice_path}")
        db.update_job(job_id, stage="voice_done")
    except Exception as e:
        log.error(f"Voice generation failed: {e}")
        db.fail_job(job_id, f"Voice stage failed: {e}")
        return {"success": False, "error": str(e), "stage": "voice"}

    # ── 4. Build Video ────────────────────────────────────────────────────────
    try:
        log.info("Stage 4/6: Building video...")
        db.update_job(job_id, stage="building_video")
        video_path = video.build_video(voice_path, script_data, job_id, topic)
        db.add_log(job_id, "INFO", f"Video built: {video_path}")
        db.update_job(job_id, video_path=video_path, stage="video_done")
    except Exception as e:
        log.error(f"Video build failed: {e}")
        db.fail_job(job_id, f"Video stage failed: {e}")
        return {"success": False, "error": str(e), "stage": "video"}

    # ── 5. Generate Thumbnail ─────────────────────────────────────────────────
    try:
        log.info("Stage 5/6: Creating thumbnail...")
        db.update_job(job_id, stage="making_thumbnail")
        thumb_path = thumbnail.generate_thumbnail(
            script_data["thumbnail_text"],
            script_data["thumbnail_subtitle"],
            topic, job_id
        )
        db.add_log(job_id, "INFO", f"Thumbnail created: {thumb_path}")
        db.update_job(job_id, thumb_path=thumb_path, stage="thumbnail_done")
    except Exception as e:
        log.warning(f"Thumbnail failed (non-fatal): {e}")
        thumb_path = ""

    # ── 6. Upload to YouTube ──────────────────────────────────────────────────
    try:
        log.info("Stage 6/6: Uploading to YouTube...")
        db.update_job(job_id, stage="uploading")
        result = upload.upload_video(
            video_path   = video_path,
            thumbnail_path = thumb_path,
            title        = script_data["title"],
            description  = script_data["description"],
            tags         = script_data["tags"],
        )
        db.complete_job(job_id, result["video_id"], result["url"], result["title"])
        upload.notify_dashboard({"job_id": job_id, "topic": topic, "title": result["title"], "video_url": result["url"], "video_id": result["video_id"], "status": "done", "stage": "uploaded"})
        db.add_log(job_id, "INFO", f"Uploaded: {result['url']}")
        log.info(f"═══ Job {job_id} COMPLETE: {result['url']} ═══")
        return {"success": True, "job_id": job_id, **result}
    except Exception as e:
        log.error(f"Upload failed: {e}")
        db.fail_job(job_id, f"Upload stage failed: {e}")
        return {"success": False, "error": str(e), "stage": "upload"}


if __name__ == "__main__":
    result = run_pipeline()
    print("\n" + "═" * 50)
    if result["success"]:
        print(f"✅ Success! Video live at: {result['url']}")
    else:
        print(f"❌ Failed at stage '{result['stage']}': {result['error']}")
    print("═" * 50)
