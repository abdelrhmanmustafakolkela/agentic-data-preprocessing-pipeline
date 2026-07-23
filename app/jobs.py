import uuid
from typing import Dict, Any
from datetime import datetime
from threading import Lock

_jobs: Dict[str, Dict[str, Any]] = {}
_jobs_lock = Lock()


def create_job(initial_state: Dict[str, Any]) -> str:
    job_id = str(uuid.uuid4())
    with _jobs_lock:
        _jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "state": initial_state,
            "result": None,
            "error": None,
        }
    return job_id


def update_job(job_id: str, updates: Dict[str, Any]):
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id].update(updates)
            _jobs[job_id]["updated_at"] = datetime.utcnow().isoformat()


def get_job(job_id: str) -> Dict[str, Any]:
    with _jobs_lock:
        return _jobs.get(job_id)


def delete_job(job_id: str):
    with _jobs_lock:
        if job_id in _jobs:
            del _jobs[job_id]


def cleanup_old_jobs(max_age_hours: int = 24):
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
    with _jobs_lock:
        to_delete = [jid for jid, job in _jobs.items() if datetime.fromisoformat(job["created_at"]) < cutoff]
        for jid in to_delete:
            del _jobs[jid]
