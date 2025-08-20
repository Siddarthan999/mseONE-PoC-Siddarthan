import strawberry
from typing import List, Optional
from .resolvers import get_projects

@strawberry.type
class ProjectType:
    id: int
    name: str
    owner: str
    created_at: str

@strawberry.type
class Query:
    @strawberry.field
    def projects(self, skip: int = 0, limit: int = 10, owner: Optional[str] = None) -> List[ProjectType]:
        return get_projects(skip=skip, limit=limit, owner=owner)

schema = strawberry.Schema(query=Query)
