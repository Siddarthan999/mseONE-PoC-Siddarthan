# app/resolvers.py
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Project
from app.storage.minio_client import minio_client, BUCKET_NAME
import json


def get_projects(skip: int = 0, limit: int = 10, owner: str | None = None) -> list[Project]:
    db: Session = SessionLocal()
    try:
        query = db.query(Project)
        if owner:
            query = query.filter(Project.owner == owner)
        return query.offset(skip).limit(limit).all()
    finally:
        db.close()


def get_workflow_results(project_id: int):
    """Fetch workflow results for a project from MinIO."""
    results = []
    objects = minio_client.list_objects(BUCKET_NAME, prefix="results/", recursive=True)

    for obj in objects:
        try:
            response = minio_client.get_object(BUCKET_NAME, obj.object_name)
            content = response.read().decode("utf-8")
            data = json.loads(content)

            if data.get("project_id") == project_id:
                results.append(data)

        except Exception as e:
            print(f"Error reading {obj.object_name}: {e}")
        finally:
            response.close()
            response.release_conn()

    return results
