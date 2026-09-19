# Assignment 2 AIOps

Rohan Sai P. (DA24B049)

This repository contains the code, manifests and notebooks for AIOps Module 3 Assignment 2. It packages a spam-detection API (TF-IDF + Naive Bayes, served with FastAPI) with Docker, runs it with a Redis cache using Docker Compose, and uses Kubernetes (minikube) for an Indexed Job and a Deployment. The answers and evidence are in `writeup.pdf`.

## Repository layout

| File | Used in | Purpose |
|---|---|---|
| `q1_docker.ipynb` | Q1 | Naive vs. multi-stage Docker images |
| `q2_compose.ipynb` | Q2 | API with a Redis cache, run with Docker Compose |
| `q3_indexed_job.ipynb` | Q3 | Indexed Job that validates 8 data shards in parallel |
| `q4_deployment.ipynb` | Q4 | Deployment, self-healing and rolling update |
| `generate_dataset.py`, `train_and_export_model.py` | Q1 | Generate the spam dataset and train the model |
| `data/` | Q1 to Q4 | Dataset (`spam_dataset.csv`) and trained model (`model.joblib`) |
| `spam_app.py`, `requirements-predictor.txt` | Q1 to Q4 | The API and the packages it needs |
| `Dockerfile.naive`, `Dockerfile.multistage` | Q1, Q2, Q4 | Docker images for the API |
| `docker-compose.yml` | Q2 | API + Redis services |
| `generate_shards.py`, `validate_shard.py` | Q3 | Create the shards and validate one shard per pod |
| `Dockerfile.validator` | Q3 | Image for the validation pods |
| `job-validate.yaml` | Q3 | Indexed Job manifest |
| `collect_results.py` | Q3 | Reads each pod's result from its logs through the Kubernetes API |
| `shards/expected_counts.json` | Q3 | Known number of invalid rows in each shard |
| `deployment.yaml`, `service.yaml` | Q4 | Deployment and Service manifests |

The shard CSV files are not in the repo because they are about 400 MB. The Q3 notebook generates them again from a fixed seed, so the data is the same on every run.

## Requirements

Tested on an ARM64 Ubuntu VM (UTM on a Mac) with 4 CPUs and about 5 GB of RAM:

- Docker 29.1.3 with Docker Compose v2
- minikube v1.39.0 (Docker driver) and kubectl v1.37.0
- Python 3 with a virtual environment

Everything runs on CPU. Image sizes may differ slightly on an x86 machine.

## Setup

Create the virtual environment **outside** the repo folder. Otherwise the naive Dockerfile's `COPY . .` copies the whole environment into the image.

```bash
cd ..
python3 -m venv venv
source venv/bin/activate
pip install jupyter pandas scikit-learn fastapi "uvicorn[standard]" joblib requests kubernetes
cd aiops-assignment2
jupyter notebook
```

For Q3 and Q4, start a 2-node minikube cluster with 2 CPUs per node:

```bash
minikube start --nodes 2 --cpus 2 --memory 2048 --driver=docker \
  --extra-config=kubelet.system-reserved=cpu=2
```

With the Docker driver, each node otherwise reports all of the machine's CPUs to Kubernetes. Reserving 2 CPUs per node makes each node offer exactly 2.

## Running the notebooks

Run the notebooks **in order, Q1 to Q4**, each from top to bottom. Each notebook writes its own version of `spam_app.py` and `requirements-predictor.txt`, and Q4 uses the `spam-api:multistage` image built in Q1.

1. **`q1_docker.ipynb`** trains the model, builds the naive and multi-stage images, tests both containers on port 8080, and compares their sizes.
2. **`q2_compose.ipynb`** adds the Redis cache, starts both services with `docker compose up`, and measures cache misses against hits. The last cell runs `docker compose down`.
3. **`q3_indexed_job.ipynb`** generates the shards, builds the validator image, loads it into minikube, runs the Indexed Job and collects the results. The last cell deletes the Job.
4. **`q4_deployment.ipynb`** deploys the API as v1, deletes a pod to show self-healing, then builds v2 and runs a rolling update while sending traffic.

## Notes

- Port 8080 must be free for Q1 and Q2. Q1 removes its containers at the end, and Q2 ends with `docker compose down`.
- Before running Q3, remove the Q4 Deployment if it exists, so its pods don't use CPU on the cluster:
  ```bash
  kubectl delete deployment spam-api --ignore-not-found
  kubectl delete service spam-api-svc --ignore-not-found
  ```
