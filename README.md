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

## Google Cloud CD

The repository includes a separate GitHub Actions workflow at `.github/workflows/cd-gcp.yml` for deploying to Google Cloud.

It expects these GitHub repository variables:

- `GCP_PROJECT_ID`
- `GCP_REGION`
- `GKE_CLUSTER_NAME`
- `GKE_CLUSTER_LOCATION`
- `ARTIFACT_REGISTRY_REPOSITORY`

It also expects this secret:

- `GCP_SA_KEY` - the JSON service account key for a Google Cloud service account with permissions to push to Artifact Registry and deploy to GKE.

The workflow builds the app image from `app/Dockerfile`, pushes it to Artifact Registry, gets GKE credentials, and applies `k8s/` to the cluster.

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

4. Try the NodePort URL first:

```bash
http://localhost:30080
```

5. If NodePort does not open in your Docker Desktop/WSL setup, use port-forward instead:

```bash
kubectl port-forward -n calculator svc/calculator-app 8000:8000
```

Then open:

```bash
http://localhost:8000
```

6. For Postgres Database you can do the following:

```bash
kubectl port-forward -n calculator svc/calculator-postgres 5432:5432
psql -h localhost -p 5432 -U calculator -d calculator
```

With the password being "calculator123" or check manifest

If you want a single command apply flow later, a `kustomization.yaml` can be added on top of these manifests.
