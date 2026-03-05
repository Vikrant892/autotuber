"""
Dashboard web server — shows pipeline status, videos, stats.
Runs on port 5050.
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify, render_template, request
from pipeline import db

app = Flask(__name__)
db.init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stats")
def stats():
    return jsonify(db.get_stats())


@app.route("/api/jobs")
def jobs():
    n = int(request.args.get("n", 20))
    return jsonify(db.get_recent_jobs(n))


@app.route("/api/logs/<job_id>")
def logs(job_id):
    return jsonify(db.get_logs(job_id))


@app.route("/api/trigger", methods=["POST"])
def trigger():
    """Manually trigger one pipeline run."""
    import threading
    from main import run_pipeline
    def _run():
        run_pipeline()
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return jsonify({"status": "triggered", "message": "Pipeline started in background"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)
