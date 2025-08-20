import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app

from fastapi.testclient import TestClient
from app.database import Base, engine, SessionLocal
from app.models import Project

client = TestClient(app)

# Setup fresh DB before tests
def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Seed some data
    db.add_all([
        Project(name="POC GraphQL", owner="Alice"),
        Project(name="Container API", owner="Bob"),
        Project(name="Automation Workflow", owner="Alice")
    ])
    db.commit()
    db.close()

def test_healthcheck():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

def test_graphql_projects_empty():
    # Reset DB to empty
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    query = """
    {
      projects {
        id
        name
      }
    }
    """
    res = client.post("/graphql", json={"query": query})
    assert res.status_code == 200
    assert res.json()["data"]["projects"] == []

def test_graphql_projects_with_data():
    query = """
    {
      projects(skip: 0, limit: 2, owner: "Alice") {
        id
        name
        owner
      }
    }
    """
    res = client.post("/graphql", json={"query": query})
    assert res.status_code == 200
    projects = res.json()["data"]["projects"]
    assert len(projects) <= 2
    for p in projects:
        assert p["owner"] == "Alice"
