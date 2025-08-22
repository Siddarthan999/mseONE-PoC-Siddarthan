# app/schema.py
import strawberry
from typing import List, Optional
from .resolvers import get_projects, get_workflow_results


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
class Query:
    @strawberry.field
    def projects(
        self, skip: int = 0, limit: int = 10, owner: Optional[str] = None
    ) -> List[ProjectType]:
        return get_projects(skip=skip, limit=limit, owner=owner)

    @strawberry.field
    def workflow_results(self, project_id: int) -> List[WorkflowResultType]:
        raw_results = get_workflow_results(project_id)

        # Convert dict → WorkflowResultType
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


@strawberry.type
class Mutation:
    @strawberry.mutation
    def start_workflow(self, project_id: int) -> str:
        from app.workflows.project_workflow import project_analysis_flow

        result = project_analysis_flow(project_id)
        return f"Workflow started for project {project_id}, result: {result['analysis']}, stored at {result['file']}"


schema = strawberry.Schema(query=Query, mutation=Mutation)
