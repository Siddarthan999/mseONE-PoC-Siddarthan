# To start the server
1. `python3 -m venv venv`
2. `.\venv\Scripts\Activate.ps1`
3. `uvicorn app.main:app --reload`

# To run the test cases
`pytest`
and
`pytest -v`

# Docker
`docker-compose down -v`
`docker-compose up --build`


