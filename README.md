# Local Azure Services Equivalent POC

## 1. Overview

This Proof of Concept (POC) demonstrates a local, open-source equivalent implementation of various Azure services, focusing on workflow orchestration, data storage, GraphQL API exposure, and authentication/authorization.

#### The POC uses the following components: (Azure to Local/Open-Source Mapping)

| **Azure Service**                  | **Local / Open-Source Alternative**                        |
|------------------------------------|------------------------------------------------------------|
| **Azure CosmosDB**                | PostgreSQL (via Docker)                                     |
| **Azure WebApps**                 | Local FastAPI app in Docker container                      |
| **Azure Container Services / AKS**| Docker Compose                                             |
| **Azure Blob Storage**            | MinIO *(S3-compatible local object storage)*               |
| **Azure Logic Apps**              | Prefect *(workflow orchestration, runs locally in Docker)*        |
| **Azure AD Authentication**       | Keycloak *(identity & access management)*                  |

## 2. Architecture

### 2.1 Components

#### FastAPI GraphQL API
- Exposes project metadata and workflow results via GraphQL.
- Supports queries and mutations, including triggering Prefect workflows.

#### Prefect
- Orchestrates project workflow executions.
- Stores workflow run logs in MinIO.

#### MinIO
- Acts as a local S3-compatible object storage for workflow logs.

#### PostgreSQL
- Stores project metadata and workflow results.

#### Keycloak
- Manages authentication and role-based authorization.
- Provides JWT tokens for API access.

### 2.2 Flow

1. User logs in via Keycloak → receives JWT.
2. User sends GraphQL query/mutation with Bearer token in `Authorization` header.
3. FastAPI verifies the JWT using Keycloak’s JWKS endpoint.
4. API resolves the query:
   - For data queries: fetch from PostgreSQL.
   - For workflow trigger: call Prefect deployment.
5. Prefect workflow executes and stores logs in MinIO.
6. User can query workflow results from the API.

---

## 3. Setup & Installation

### 3.1 Docker Compose

Run all services locally:

```yaml
version: "3.9"
services:
  api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./app:/app

  prefect:
    image: prefecthq/prefect:2-latest
    command: bash -c "pip install -r /app/requirements.txt && prefect server start --host 0.0.0.0"
    working_dir: /app
    environment:
      - PYTHONPATH=/app
    ports:
      - "4200:4200"
    volumes:
      - ./app:/app

  minio:
    image: minio/minio
    ports:
      - "9000:9000"
    environment:
      MINIO_ROOT_USER: minio
      MINIO_ROOT_PASSWORD: minio123
    command: server /data
```
* API Dockerfile is located at ./api/Dockerfile.

* FastAPI and Prefect share the /app code volume.

* MinIO provides object storage.

### 3.2 Keycloak Setup

* Run Keycloak in Docker.

* Create Realm: mse-one

* Create Client: poc-cli (confidential)

* Create test user: sidd / password siddpass

* Set environment variables in .env:
```
OIDC_ISSUER=http://localhost:8080/realms/mse-one
OIDC_JWKS_URL=http://localhost:8080/realms/mse-one/protocol/openid-connect/certs
OIDC_AUDIENCE=account
REQUIRE_AUTH=true
```
## 4. GraphQL API

### 4.1 Queries

whoami
```
{
  whoami {
    sub
    username
    email
    roles
  }
}
```

projects
```
{
  projects {
    id
    name
    owner
    createdAt
  }
}
```

workflow_results
```
{
  workflow_results(project_id: 1) {
    projectId
    analysis
    status
    error
    timestamp
  }
}
```
### 4.2 Mutations

start_workflow
```
mutation {
  start_workflow(project_id: 1)
}
```
* Requires role: uma_authorization.

* Triggers a Prefect workflow deployment (project-analysis-flow).

## 5. Prefect Workflows

* project_analysis_flow:

  * Fetches project metadata from PostgreSQL.

  * Performs project analysis.

  * Saves results and logs to MinIO.

* Deployment:
```
prefect deployment build workflows/project_workflow.py:project_analysis_flow -n "project-analysis" -q "default" --skip-upload
prefect deployment apply project_analysis_flow-deployment.yaml
prefect agent start -q default
```

## 6. Achievements So Far
* ✅ Local GraphQL API exposing project data and workflow results.

* ✅ Prefect workflow integration with async execution.

* ✅ MinIO storage for workflow logs.

* ✅ JWT-based authentication & authorization using Keycloak.

* ✅ Role-based access control for mutations.

* ✅ Dockerized setup for API, Prefect, and MinIO.

* ✅ Fully tested GraphQL queries and mutations with JWT from Keycloak.



# To start the server
1. `python3 -m venv venv`
2. `.\venv\Scripts\Activate.ps1`
3. `uvicorn app.main:app --reload`

# To run the test cases
`pytest`
OR
`pytest -v`

# Docker
1. `docker-compose down -v`
2. `docker-compose up --build`

OR
1. `docker compose down`
2. `docker system prune -f`
3. `docker compose build --no-cache`
4. `docker compose up`

# Get into the api container shell
1. `docker compose exec api bash`
2. `python -m app.workflows.project_workflow`

1. `docker compose exec prefect bash`
2.
```
prefect deployment build workflows/project_workflow.py:project_analysis_flow -n "project-analysis" -q "default" --skip-upload
prefect deployment apply project_analysis_flow-deployment.yaml
```
3. `prefect agent start -q default`


# PostGres
1. `docker exec -it poc_postgres psql -U admin -d pocdb`
2. `INSERT INTO projects (name, owner) VALUES ('POC GraphQL', 'Alice');`
3. `INSERT INTO projects (name, owner) VALUES ('Workflow Automation', 'Bob');`

# GraphQL
GraphQL API accessible at http://127.0.0.1:8000/graphql

# MinIO
MinIO console accessible at http://127.0.0.1:9001

# GraphQL Commands
1. 
```
query {
  projects(limit: 5) {
    id
    name
    owner
    createdAt
  }
}
```

2.
```
mutation {
  startWorkflow(projectId: 1)
}
```
3.
```
query {
  workflowResults(projectId: 1) {
    projectId
    analysis
    timestamp
  }
}
```
4.
```
query {
  workflowResults(projectId: 1) {
    projectId
    analysis
    status
    error
    timestamp
  }
}
```

# Prefect
Check out the dashboard at http://127.0.0.1:4200/

# KeyCloak
http://127.0.0.1:8080/
1. Log in (admin/admin)
2. *Realm: mse-one*
    * *_Client ID:_* poc-cli
    * *_Username:_* sidd
    * *_Password:_* siddpass
3. JWT Token Generation using Invoke-RestMethod (cleaner in PowerShell)
```
$headers = @{
  "Content-Type" = "application/x-www-form-urlencoded"
}

$body = @{
  client_id = "poc-cli"
  username  = "sidd"
  password  = "siddpass"
  grant_type = "password"
}

$response = Invoke-RestMethod -Uri "http://localhost:8080/realms/mse-one/protocol/openid-connect/token" -Method Post -Headers $headers -Body $body
$response.access_token
```
# In PostMan
1. Headers
 * Content-Type = application/json
 * Authorization = Bearer eyJhb....
2. Body -> Raw (JSON)
```
{
  "query": "{ whoami { sub username email roles } }"
}
```
```
{
  "query": "{ projects { id name owner createdAt } }"
}
```
```
{
  "query": "{ workflow_results(projectId: 1) { projectId analysis status error timestamp } }"
}
```
```
{
  "query": "{ start_workflow(project_id: 1) }"
}
```

