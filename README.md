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
2.
Body -> Raw (JSON)
```
{
  "query": "{ whoami { sub username email roles } }"
}
{
  "query": "{ projects { id name owner createdAt } }"
}
{
  "query": "{ workflow_results(projectId: 1) { projectId analysis status error timestamp } }"
}
{
  "query": "{ start_workflow(project_id: 1) }"
}
```


