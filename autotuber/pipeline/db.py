"""SQLite database for tracking all pipeline jobs and videos."""
import sqlite3
import json
import logging
from datetime import datetime
from config import DB_FILE

log = logging.getLogger(__name__)


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS jobs (
        id          TEXT PRIMARY KEY,
        topic       TEXT,
        title       TEXT,
        status      TEXT DEFAULT 'pending',
        stage       TEXT DEFAULT 'init',
        video_id    TEXT,
        video_url   TEXT,
        error       TEXT,
        views       INTEGER DEFAULT 0,
        likes       INTEGER DEFAULT 0,
        video_path  TEXT,
        thumb_path  TEXT,
        created_at  TEXT,
        completed_at TEXT
    );

    CREATE TABLE IF NOT EXISTS used_topics (
        topic       TEXT PRIMARY KEY,
        used_at     TEXT
    );

    CREATE TABLE IF NOT EXISTS logs (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id      TEXT,
        level       TEXT,
        message     TEXT,
        ts          TEXT
    );
    """)
    conn.commit()
    conn.close()
    log.info("DB initialised")


def create_job(job_id: str, topic: str) -> None:
    conn = get_conn()
    conn.execute(
        "INSERT INTO jobs(id,topic,status,stage,created_at) VALUES(?,?,'running','init',?)",
        (job_id, topic, datetime.utcnow().isoformat())
    )
    conn.execute(
        "INSERT OR IGNORE INTO used_topics(topic,used_at) VALUES(?,?)",
        (topic, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def update_job(job_id: str, **kwargs) -> None:
    if not kwargs:
        return
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [job_id]
    conn = get_conn()
    conn.execute(f"UPDATE jobs SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()


def complete_job(job_id: str, video_id: str, url: str, title: str) -> None:
    conn = get_conn()
    conn.execute(
        "UPDATE jobs SET status='done',stage='uploaded',video_id=?,video_url=?,title=?,completed_at=? WHERE id=?",
        (video_id, url, title, datetime.utcnow().isoformat(), job_id)
    )
    conn.commit()
    conn.close()


def fail_job(job_id: str, error: str) -> None:
    conn = get_conn()
    conn.execute(
        "UPDATE jobs SET status='error',error=? WHERE id=?",
        (error[:500], job_id)
    )
    conn.commit()
    conn.close()


def get_used_topics() -> list[str]:
    conn = get_conn()
    rows = conn.execute("SELECT topic FROM used_topics ORDER BY used_at DESC LIMIT 50").fetchall()
    conn.close()
    return [r["topic"] for r in rows]


def get_recent_jobs(n: int = 20) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (n,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_log(job_id: str, level: str, message: str) -> None:
    conn = get_conn()
    conn.execute(
        "INSERT INTO logs(job_id,level,message,ts) VALUES(?,?,?,?)",
        (job_id, level, message[:1000], datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def get_logs(job_id: str, n: int = 50) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM logs WHERE job_id=? ORDER BY ts DESC LIMIT ?",
        (job_id, n)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats() -> dict:
    conn = get_conn()
    total    = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    done     = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='done'").fetchone()[0]
    errors   = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='error'").fetchone()[0]
    running  = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='running'").fetchone()[0]
    conn.close()
    return {
        "total": total, "done": done,
        "errors": errors, "running": running,
        "est_revenue_usd": round(done * 1.5, 2)  # rough $1.5 per video avg
    }
