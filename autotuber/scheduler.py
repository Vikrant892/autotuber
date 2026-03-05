"""
Scheduler — runs the pipeline every day at 7am Adelaide time.
Run this once and leave it running (or use Docker).
"""
import logging
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from config import SCHEDULE_HOUR, SCHEDULE_TZ
from main import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SCHEDULER] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("scheduler")


def job():
    log.info("⏰ Scheduled run triggered")
    result = run_pipeline()
    if result["success"]:
        log.info(f"✅ Done: {result.get('url')}")
    else:
        log.error(f"❌ Failed: {result.get('error')}")


scheduler = BlockingScheduler(timezone=SCHEDULE_TZ)
scheduler.add_job(
    job,
    CronTrigger(hour=SCHEDULE_HOUR, minute=0, timezone=SCHEDULE_TZ),
    id="daily_video",
    name="Daily video pipeline",
    max_instances=1,
    misfire_grace_time=3600
)

log.info(f"🕐 Scheduler started. Next run: daily at {SCHEDULE_HOUR}:00 {SCHEDULE_TZ}")
log.info("   Press Ctrl+C to stop.")

try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    log.info("Scheduler stopped.")
