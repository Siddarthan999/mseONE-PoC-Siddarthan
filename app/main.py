# app/main.py
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from .schema import schema
from .database import Base, engine
from .auth import auth_context  # NEW

# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="POC GraphQL API")

# Mount GraphQL endpoint with auth context
graphql_app = GraphQLRouter(schema, context_getter=auth_context)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def healthcheck():
    return {"status": "ok"}
