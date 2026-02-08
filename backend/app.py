from __future__ import annotations

from threading import Lock, Thread
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request, send_from_directory

from backend.config import DEFAULT_QUALITY, OUTPUT_DIR, QUALITY_PRESETS, RECITERS
from backend.services.audio_processing import prepare_audio
from backend.services.quran_api import fetch_ayah_data
from backend.services.video_composer import compose_video

JOBS: dict[str, dict[str, object]] = {}
JOBS_LOCK = Lock()


def _update_job(job_id: str, **updates: object) -> None:
    with JOBS_LOCK:
        JOBS.setdefault(job_id, {}).update(updates)


def _render_job(job_id: str, surah: int, ayah: int, reciter_id: str, quality: str) -> None:
    started_at = time()
    try:
        _update_job(job_id, status="running", progress=5, message="جلب بيانات الآية")
        reciter = next((r for r in RECITERS if r.id == reciter_id), RECITERS[0])
        ayah_data = fetch_ayah_data(surah, ayah, reciter.audio_base_url)

        _update_job(job_id, progress=35, message="معالجة الصوت")
        audio_path = OUTPUT_DIR / f"{job_id}.mp3"
        audio_path, duration = prepare_audio(ayah_data.audio_url, audio_path)

        _update_job(job_id, progress=65, message="تركيب الفيديو")
        output_path = OUTPUT_DIR / f"{job_id}.mp4"
        preset = QUALITY_PRESETS.get(quality, QUALITY_PRESETS[DEFAULT_QUALITY])
        compose_video(
            ayah_data.text,
            audio_path,
            output_path,
            duration,
            size=preset["size"],
            fps=preset["fps"],
            threads=preset["threads"],
            preset=preset["preset"],
        )
        elapsed = round(time() - started_at, 2)
        _update_job(
            job_id,
            status="done",
            progress=100,
            message="تم إنشاء الفيديو بنجاح",
            output=f"/outputs/{output_path.name}",
            reciter=reciter.name,
            elapsed=elapsed,
        )
    except Exception as exc:  # noqa: BLE001
        elapsed = round(time() - started_at, 2)
        _update_job(
            job_id,
            status="failed",
            progress=100,
            message="حدث خطأ أثناء إنشاء الفيديو",
            error=str(exc),
            elapsed=elapsed,
        )


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/api/reciters")
    def list_reciters():
        return jsonify(
            [
                {
                    "id": reciter.id,
                    "name": reciter.name,
                    "audio_base_url": reciter.audio_base_url,
                }
                for reciter in RECITERS
            ]
        )

    @app.post("/api/render")
    def render_video():
        payload = request.get_json(force=True)
        surah = int(payload.get("surah", 1))
        ayah = int(payload.get("ayah", 1))
        reciter_id = payload.get("reciter", RECITERS[0].id)
        quality = payload.get("quality", DEFAULT_QUALITY)

        job_id = uuid4().hex
        _update_job(
            job_id,
            status="queued",
            progress=0,
            message="في قائمة الانتظار",
            surah=surah,
            ayah=ayah,
            quality=quality,
        )
        Thread(target=_render_job, args=(job_id, surah, ayah, reciter_id, quality), daemon=True).start()

        return jsonify({"job_id": job_id})

    @app.get("/api/status/<job_id>")
    def job_status(job_id: str):
        with JOBS_LOCK:
            job = JOBS.get(job_id)
        if not job:
            return jsonify({"status": "not_found"}), 404
        return jsonify(job)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/")
    def index():
        return send_from_directory("frontend", "index.html")

    @app.get("/<path:path>")
    def static_assets(path: str):
        return send_from_directory("frontend", path)

    @app.get("/outputs/<path:filename>")
    def outputs(filename: str):
        return send_from_directory(str(OUTPUT_DIR), filename)

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)
