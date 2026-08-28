```markdown
# Automated GitOps Continuous Delivery Pipeline & Cloud Cost Auditor

[![CI/CD & FinOps Gate](https://github.com/your-username/gitops-cost-auditor/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/your-username/gitops-cost-auditor)
![Kubernetes](https://img.shields.io/badge/Kubernetes-1.29%2B-blue)
![ArgoCD](https://img.shields.io/badge/GitOps-ArgoCD-orange)
![FinOps](https://img.shields.io/badge/FinOps-Cost%20Guardrail-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green.svg)

An enterprise GitOps continuous delivery pipeline with an integrated pre-deployment FinOps cost-budget guardrail. The system evaluates Kubernetes resource requests and limits against cloud pricing models directly within GitHub Actions, automatically blocking pull requests that exceed defined budget thresholds before ArgoCD synchronizes changes to target clusters.

---

## Architecture Overview

```text
+-----------------------------------------------------------------------------------+
|                                 Developer Git Push                                |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                           GitHub Actions CI / FinOps Gate                         |
|  1. Run Linters & Pytest Test Suites                                              |
|  2. Render Helm Templates into Pure Kubernetes Manifests                          |
|  3. Run FinOps Cost Auditor against Monthly Budget Caps                           |
|  4. Dispatch Rich Slack Block Kit Cost Alerts                                     |
|  5. Auto-Promote Image Tag in GitOps Manifests (Main Branch Only)                 |
+------------------------------------------+----------------------------------------+
                                           | (Git Commit & Push)
                                           v
+-----------------------------------------------------------------------------------+
|                           ArgoCD GitOps Sync Engine                               |
|  - Continuously monitors repository state vs live cluster state                   |
|  - Performs automated zero-downtime rollouts and self-healing                     |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                        Target Kubernetes Cluster (EKS/GKE)                        |
|  - High-Availability FastAPI Microservice                                         |
|  - HorizontalPodAutoscaler (HPA) CPU-based dynamic scaling                        |
+-----------------------------------------------------------------------------------+
```

---

## Key Features

* **Declarative GitOps Delivery:** Automated ArgoCD synchronization with continuous drift detection, auto-pruning, and self-healing.
* **Pre-Deployment FinOps Guardrail:** Computes monthly run rates from CPU/Memory requests using custom cost modeling prior to merge.
* **Automated Cost Rejection:** Fails CI pipelines and halts deployment rollouts if resource updates exceed defined monthly team budget caps.
* **Proactive Notification Engine:** Generates Slack Block Kit alerts detailing cost deltas, CPU/memory allocations, and pass/fail statuses.
* **Full Automated Test Coverage:** Unit test suites for microservice endpoints, cost calculation models, and budget gate boundaries.

---

## Project Structure

```bash
gitops-cost-auditor/
├── .github/
│   └── workflows/
│       ├── ci-cd.yml                # CI build, cost delta evaluation, and GitOps trigger
│       └── cost-audit-cron.yml      # Scheduled periodic cost scans
├── app/
│   ├── main.py                      # FastAPI microservice
│   ├── Dockerfile                   # Multi-stage production container build
│   └── requirements.txt             # Service dependencies
├── auditor/
│   ├── cost_analyzer.py             # Parses K8s resource specs and computes cost models
│   ├── slack_notifier.py            # Formats and posts Slack Block Kit alerts
│   └── main.py                      # CLI entrypoint for CI/CD FinOps execution
├── gitops/
│   ├── argocd/
│   │   ├── application.yaml         # ArgoCD Root Application manifest
│   │   └── project.yaml             # ArgoCD AppProject RBAC settings
│   └── charts/
│       └── web-service/             # Production Helm chart (Deployment, Service, HPA)
├── tests/
│   ├── conftest.py                  # Pytest shared fixtures
│   ├── test_app.py                  # API health and endpoint tests
│   └── test_cost_analyzer.py        # Cost estimation and budget gate tests
├── Makefile                         # Unified automation commands
├── requirements-dev.txt             # Development and testing tools
└── README.md
```

---

## Prerequisites

Ensure you have the following installed on your local workstation:

* **Python:** `3.11+`
* **Docker:** `24.0+`
* **Helm:** `v3.12+`
* **kubectl:** `v1.28+`
* **Minikube** or **Kind** (for local Kubernetes testing)
* **ArgoCD CLI** (optional, for cluster inspection)

---

## Step-by-Step Installation & Local Run Guide

### 1. Clone the Repository & Set Up Environment

```bash
git clone [https://github.com/your-username/gitops-cost-auditor.git](https://github.com/your-username/gitops-cost-auditor.git)
cd gitops-cost-auditor

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install all runtime, test, and development dependencies
make setup
```

### 2. Run the Microservice Locally

Run the sample FastAPI application with hot reload:

```bash
make run-local
```

Access the endpoints:
* **Root:** `http://localhost:8080/`
* **Health Check:** `http://localhost:8080/healthz`
* **Swagger API Docs:** `http://localhost:8080/docs`

### 3. Execute the Automated Test Suite

Run unit tests and verify test coverage:

```bash
make test
```

Run code formatters and linters:

```bash
make lint
```

### 4. Run the FinOps Cost Auditor Locally

The auditor renders your Helm templates into raw Kubernetes manifests and evaluates whether projected monthly costs fit within your budget.

```bash
# Render Helm templates and execute auditor with a $150.00/month budget cap
make run-audit
```

**Example Output:**
```text
--- FinOps Audit Result ---
Projected Monthly Cost: $6.21 USD
Budget Limit:           $150.0 USD
Status:                 APPROVED
```

To test budget rejection scenarios, set a lower threshold:

```bash
python auditor/main.py --manifest build/rendered.yaml --budget 1.00
```

---

## Local Kubernetes & GitOps Deployment (Kind / Minikube)

### 1. Start a Local Cluster

```bash
# Using Kind
kind create cluster --name gitops-cluster

# Or using Minikube
minikube start
```

### 2. Install ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f [https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml](https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml)

# Wait for ArgoCD server components to become ready
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd
```

### 3. Port-Forward ArgoCD Web UI

```bash
kubectl port-forward svc/argocd-server -n argocd 8081:443
```

* **URL:** `https://localhost:8081`
* **Username:** `admin`
* **Initial Password:**
  ```bash
  kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
  ```

### 4. Deploy the Application via ArgoCD

Apply the declarative ArgoCD application manifest:

```bash
kubectl apply -f gitops/argocd/application.yaml
```

Check sync status:

```bash
kubectl get applications -n argocd
kubectl get pods -n production
```

---

## CI/CD Pipeline & GitHub Secrets Setup

To enable automated Docker image builds, cost gate audits, and Slack notifications on every push, configure the following secrets in your GitHub repository (**Settings > Secrets and variables > Actions**):

| Secret Name | Description | Required |
|---|---|---|
| `SLACK_WEBHOOK_URL` | Incoming webhook URL for FinOps alerts | Optional |
| `CR_PAT` | Personal Access Token for Container Registry | Optional |

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

```
