# app/workflows/project_workflow.py
import io
import time
import json
from datetime import datetime
from prefect import flow, task
from app.storage.minio_client import minio_client, BUCKET_NAME


@task
def fetch_project_metadata(project_id: int):
    """Simulate fetching metadata for a project."""
    return {"id": project_id, "name": f"Project-{project_id}"}


@task
def analyze_project(metadata: dict):
    """Simulate heavy analysis logic for a project."""
    time.sleep(2)  # simulate computation
    return f"Project {metadata['name']} analyzed successfully!"


@task
def save_to_minio(project_id: int, analysis: str):
    """Persist analysis results as JSON in MinIO."""
    result = {
        "project_id": project_id,
        "analysis": analysis,
        "timestamp": datetime.utcnow().isoformat()
    }
    content = json.dumps(result).encode("utf-8")

    # File path inside bucket
    file_name = f"results/project-{project_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"

    # Upload JSON to MinIO
    minio_client.put_object(
        BUCKET_NAME,
        file_name,
        io.BytesIO(content),
        length=len(content),
        content_type="application/json",
    )
    return file_name


@flow(name="project-analysis-flow")
def project_analysis_flow(project_id: int):
    """Full Prefect flow to analyze a project and persist results to MinIO."""
    metadata = fetch_project_metadata(project_id)
    analysis = analyze_project(metadata)
    file_path = save_to_minio(project_id, analysis)

    return {
        "analysis": analysis,
        "file": file_path
    }
