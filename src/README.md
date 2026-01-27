# Gists FastAPI — Usage Guide

This document explains how to run, test, lint and containerize the Gists
FastAPI application in this repository.

Files of interest
- Configuration template: [src/.env_template](src/.env_template)
- Python requirements: [src/requirements.txt](src/requirements.txt)
- Application entrypoint: [src/app/main.py](src/app/main.py)
- Dockerfile: [Dockerfile](Dockerfile)
- Tests: [src/tests/tests_routes.py](src/tests/tests_routes.py)
- Linter config: [pyproject.toml](pyproject.toml)

Prerequisites
- Python 3.11 (or compatible 3.11.x)
- Docker (optional, for container builds)

## Local development

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
# if Windows, run: .venv/scripts/activate
source .venv/bin/activate
```

2. Install runtime dependencies:

```
pip install --upgrade pip
pip install -r src/requirements-lint.txt
```

3. Create a `.env` file from the template and set any values needed:

```
cp src/.env_template .env
# then edit .env to set APP__GITHUB_TOKEN if you have one. This will help with rate limmits on Github
```

4. Run the application locally (development):

```
# Option A: run via the module entrypoint used in the project
python -m app.main

# Option B: run with uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

Endpoints
- Health: `GET /healthz` — returns `{"status": "ok"}`
- Gists: `GET /users/{username}` — returns paginated gist pages under the `results` key
- Metrics: `GET /metrics` — Prometheus metrics exposed by Instrumentator

5. (Optional) - Run Redis cache and enable Redis caching for api responses from Github


### Running tests

Run the pytest suite from within src directory as it will pick up conftest.py:

```
pytest -rPq tests
```

The provided tests use `fastapi.testclient.TestClient` and monkeypatch
helpers to validate behavior without requiring real upstream GitHub
requests.

### Linting

This project includes `pyproject.toml` configured for `black`, `isort`
and `flake8`.

Install tools (if not already installed, the above steps include instructions to install requirements-lint.txt). Run the following checks:

```
black --check src
isort --check-only src
pflake8 src
```

Or format in-place:

```
black src
isort src
```

### Docker

Build the image (the `Dockerfile` copies only the `src/app` folder):

```
docker build -t gists-app .
```

Run the container, mapping the container port to the host:

```
# tip: remove quotes from variable values in file:
docker run --rm -p 8080:8080 --env-file .env gists-app
```

Notes
- The app reads nested settings using the `Settings` model; provide
  environment overrides using the `APP__...` nested variable names (see
  [src/.env_template](src/.env_template)).

### Future Considerations

- implement middleware logic to improve logging, rate limiting + more..
- implement CORS logic to improve security
- Implement more structured logging and standardize throughout the app
