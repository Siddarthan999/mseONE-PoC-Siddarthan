# To start the server
1. `python3 -m venv venv`
2. `.\venv\Scripts\Activate.ps1`
3. `uvicorn app.main:app --reload`

# To run the test cases
`pytest`
and
`pytest -v`

# Docker
1. `docker-compose down -v`
2. `docker-compose up --build`

# PostGres
1. `docker exec -it poc_postgres psql -U admin -d pocdb`
2. `INSERT INTO projects (name, owner) VALUES ('POC GraphQL', 'Alice');`
3. `INSERT INTO projects (name, owner) VALUES ('Workflow Automation', 'Bob');`

# GraphQL
GraphQL API accessible at http://127.0.0.1:8000/graphql

# MinIO
MinIO console accessible at http://127.0.0.1:9001