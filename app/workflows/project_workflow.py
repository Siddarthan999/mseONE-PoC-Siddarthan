# app/workflows/project_workflow.py
import io
import time
import json
from datetime import datetime
from prefect import flow, task, get_run_logger
from storage.minio_client import minio_client, BUCKET_NAME

@task
def fetch_project_metadata(project_id: int):
    logger = get_run_logger()
    logger.info(f"Fetching metadata for project {project_id}")
    return {"id": project_id, "name": f"Project-{project_id}"}

@task
def analyze_project(metadata: dict):
    logger = get_run_logger()
    logger.info(f"Analyzing project {metadata['name']}...")
    time.sleep(2)
    return f"Project {metadata['name']} analyzed successfully!"

@task
def save_to_minio(project_id: int, analysis: str):
    result = {
        "project_id": project_id,
        "analysis": analysis,
        "status": "completed",
        "error": None,
        "timestamp": datetime.utcnow().isoformat()
    }
    content = json.dumps(result).encode("utf-8")

    file_name = f"results/project-{project_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
    minio_client.put_object(
        BUCKET_NAME,
        file_name,
        io.BytesIO(content),
        length=len(content),
        content_type="application/json",
    )

    return file_name

@flow(name="project-analysis-flow")
def project_analysis_flow(project_id: int = 1):
    metadata = fetch_project_metadata(project_id)
    analysis = analyze_project(metadata)
    file_path = save_to_minio(project_id, analysis)
    return {"analysis": analysis, "file": file_path}

if __name__ == "__main__":
    from prefect.deployments import Deployment

    # Create a deployment for our flow
    deployment = Deployment.build_from_flow(
        flow=project_analysis_flow,
        name="project-analysis-deployment"
    )
    deployment.apply()
