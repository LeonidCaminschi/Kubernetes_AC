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
docker build -t ghcr.io/your-org/calculator-app:1.0.0 .
```

## Image reference used by Kubernetes

The Kubernetes base uses `calculator-app` as the image name and `k8s/kustomization.yaml` rewrites it to `ghcr.io/your-org/calculator-app:1.0.0`. In CI/CD, update the tag to the commit SHA or release version before deploying.

## Kubernetes on Docker Desktop

1. Start Kubernetes in Docker Desktop.
2. Apply the manifests:

```bash
kubectl apply -k k8s
```

3. Build the app image with the same registry name used by Kustomize, then push it in CI/CD or load it into Docker Desktop locally:

```bash
cd app
docker build -t ghcr.io/your-org/calculator-app:1.0.0 .
```

4. Open the app at `http://localhost:30080`.

If you want a single command apply flow later, a `kustomization.yaml` can be added on top of these manifests.
