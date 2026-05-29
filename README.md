# Calculator App with Postgres History

A simple Python calculator web app that stores every calculation in PostgreSQL. The app and database are designed to run in separate Kubernetes pods.

## Stack

- FastAPI for the backend and UI
- Vanilla HTML, CSS, and JavaScript for the frontend
- PostgreSQL for history storage
- Kubernetes manifests for Docker Desktop in WSL

## Local run

```bash
cd app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=calculator
export DB_USER=calculator
export DB_PASSWORD=calculator123
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Docker image

```bash
cd app
docker build -t calculator-app:1.0 .
```

## Kubernetes on Docker Desktop

1. Start Kubernetes in Docker Desktop.
2. Apply the manifests:

```bash
kubectl apply -k k8s
```

3. Build the app image locally so Kubernetes can pull it from the Docker Desktop image store:

```bash
cd app
docker build -t calculator-app:1.0 .
```

4. Open the app at `http://localhost:30080`.

If you want a single command apply flow later, a `kustomization.yaml` can be added on top of these manifests.
