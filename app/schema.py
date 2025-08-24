# app/schema.py
import strawberry
from typing import List, Optional
from fastapi import HTTPException
from .resolvers import get_projects, get_workflow_results
from app.auth import require_roles  # NEW


@strawberry.type
class ProjectType:
    id: int
    name: str
    owner: str
    created_at: str


@strawberry.type
class WorkflowResultType:
    projectId: int
    analysis: str
    status: Optional[str]
    error: Optional[str]
    timestamp: str


@strawberry.type
class WhoAmIType:   # NEW
    sub: str
    username: Optional[str]
    email: Optional[str]
    roles: List[str]


@strawberry.type
class Query:
    @strawberry.field
    def projects(
        self, skip: int = 0, limit: int = 10, owner: Optional[str] = None
    ) -> List[ProjectType]:
        return get_projects(skip=skip, limit=limit, owner=owner)

    @strawberry.field
    def workflow_results(self, project_id: int) -> List[WorkflowResultType]:
        raw_results = get_workflow_results(project_id)

        return [
            WorkflowResultType(
                projectId=r["project_id"],
                analysis=r["analysis"],
                status=r.get("status"),
                error=r.get("error"),
                timestamp=r["timestamp"],
            )
            for r in raw_results
        ]

    @strawberry.field  # NEW
    def whoami(self, info) -> WhoAmIType:
        user = info.context.get("user") or {}
        return WhoAmIType(
            sub=user.get("sub", ""),
            username=user.get("username"),
            email=user.get("email"),
            roles=user.get("roles") or [],
        )


@strawberry.type
class Mutation:
    @strawberry.mutation
    def start_workflow(self, info, project_id: int) -> str:
        require_roles(info, ["uma_authorization"])  # only users with this role can run
        from app.workflows.project_workflow import project_analysis_flow
        from prefect.deployments import run_deployment

        deployment_id = "project-analysis-flow/default"
        run = run_deployment(name=deployment_id, parameters={"project_id": project_id})

        return f"Workflow submitted for project {project_id}, run id: {run.id}"


schema = strawberry.Schema(query=Query, mutation=Mutation)
