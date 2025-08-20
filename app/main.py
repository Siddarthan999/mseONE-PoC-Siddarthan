from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from .schema import schema
from .database import Base, engine

# create tables
Base.metadata.create_all(bind=engine)

graphql_app = GraphQLRouter(schema)

app = FastAPI(title="POC GraphQL API")

@app.get("/")
def healthcheck():
    return {"status": "ok"}

# Mount GraphQL endpoint
app.include_router(graphql_app, prefix="/graphql")
