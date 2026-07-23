from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import shutil
from pathlib import Path
from app.state import PipelineState
from app.graph import get_pipeline_graph
from app.jobs import create_job, update_job, get_job
from app.config import settings

os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

app = FastAPI(title="Agentic Data Preprocessing Pipeline")
app.mount("/static", StaticFiles(directory="frontend"), name="static")


def run_pipeline(job_id: str, file_path: str, original_filename: str):
    try:
        initial_state: PipelineState = {
            "file_path": file_path,
            "original_filename": original_filename,
            "data_profile": {},
            "profile_summary_text": "",
            "preprocessing_plan": [],
            "cleaned_file_path": "",
            "cleaning_log": [],
            "post_clean_profile": {},
            "chart_plan": [],
            "charts": [],
            "errors": [],
            "status": "running",
        }
        update_job(job_id, {"state": initial_state, "status": "running"})
        graph = get_pipeline_graph()
        result = graph.invoke(initial_state)
        base_name = Path(original_filename).stem
        cleaned_data_urls = {"csv": f"/api/download/{job_id}/csv", "xlsx": f"/api/download/{job_id}/xlsx"}
        report_lines = ["# Data Processing Report", "", "## Dataset Description", result.get("profile_summary_text", "N/A"), "", "## Preprocessing Steps Applied"]
        for log in result.get("cleaning_log", []):
            report_lines.append(f"- {log}")
        report_lines.extend(["", "## Charts Generated", f"{len(result.get('charts', []))} charts were generated based on the data."])
        report_markdown = "\n".join(report_lines)
        update_job(job_id, {
            "status": result["status"],
            "state": result,
            "result": {
                "job_id": job_id,
                "status": result["status"],
                "profile_summary": result.get("profile_summary_text", ""),
                "preprocessing_plan": result.get("preprocessing_plan", []),
                "cleaning_log": result.get("cleaning_log", []),
                "chart_plan": result.get("chart_plan", []),
                "charts": result.get("charts", []),
                "cleaned_data_urls": cleaned_data_urls,
                "report_markdown": report_markdown,
                "errors": result.get("errors", []),
            }
        })
    except Exception as e:
        update_job(job_id, {"status": "failed", "error": str(e)})


@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html")


@app.post("/api/analyze")
async def analyze_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    file_size = 0
    for chunk in file.file:
        file_size += len(chunk)
        if file_size > settings.max_upload_size_mb * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"File too large. Max size: {settings.max_upload_size_mb}MB")
    await file.seek(0)
    if not file.filename.endswith(('.csv', '.xlsx')):
        raise HTTPException(status_code=400, detail="Only .csv and .xlsx files are supported")
    upload_path = Path("uploads") / file.filename
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    job_id = create_job({})
    background_tasks.add_task(run_pipeline, job_id, str(upload_path), file.filename)
    return {"job_id": job_id, "status": "pending", "message": "File uploaded. Processing started."}


@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job["job_id"], "status": job["status"], "created_at": job["created_at"], "updated_at": job["updated_at"], "result": job.get("result"), "error": job.get("error")}


@app.get("/api/download/{job_id}/{file_type}")
async def download_cleaned_file(job_id: str, file_type: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "done":
        raise HTTPException(status_code=400, detail="Job not completed")
    state = job.get("state", {})
    cleaned_file_path = state.get("cleaned_file_path")
    if not cleaned_file_path or not os.path.exists(cleaned_file_path):
        raise HTTPException(status_code=404, detail="Cleaned file not found")
    base_path = Path(cleaned_file_path)
    if file_type == "csv":
        file_path = base_path
    elif file_type == "xlsx":
        file_path = base_path.with_suffix(".xlsx")
    else:
        raise HTTPException(status_code=400, detail="Invalid file type")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=file_path.name)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
