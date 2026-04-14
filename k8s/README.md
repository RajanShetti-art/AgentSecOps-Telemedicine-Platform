# Kubernetes + ArgoCD GitOps Deployment (Minikube)

This folder contains all Kubernetes manifests for the telemedicine platform and ArgoCD GitOps application.

## Manifest Inventory

- `namespace.yaml` dedicated namespace (`devsecops`)
- `configmap.yaml` non-sensitive configuration
- `secret.yaml` sensitive values (JWT and DB credentials)
- `auth-service.yaml` Deployment + Service
- `patient-service.yaml` Deployment + Service
- `appointment-service.yaml` Deployment + Service
- `argocd-application.yaml` ArgoCD Application for GitOps sync from `k8s/`

## 1) Start Minikube

```bash
minikube start
```

## 2) Build/Load Images for Minikube

Use your own image tags in manifests, or build directly in Minikube Docker daemon:

```bash
eval $(minikube docker-env)
docker build -t rajanshettiart/auth-service:latest ./auth-service
docker build -t rajanshettiart/patient-service:latest ./patient-service
docker build -t rajanshettiart/appointment-service:latest ./appointment-service
```

If you build outside Minikube:

```bash
minikube image load rajanshettiart/auth-service:latest
minikube image load rajanshettiart/patient-service:latest
minikube image load rajanshettiart/appointment-service:latest
```

## 3) Install ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

(Optional) Access ArgoCD UI:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

## 3.1) Install Kyverno (Policy Engine)

```bash
helm repo add kyverno https://kyverno.github.io/kyverno/
helm repo update
helm upgrade --install kyverno kyverno/kyverno --namespace kyverno --create-namespace
```

Apply Kyverno policies:

```bash
kubectl apply -f k8s/kyverno/policies.yaml
```

Optional policy test manifests:

```bash
kubectl apply -f k8s/kyverno/policy-test-examples.yaml
```

## 4) Bootstrap GitOps Application

```bash
kubectl apply -f k8s/argocd-application.yaml
```

ArgoCD will automatically sync manifests in `k8s/` to namespace `devsecops`.

## 5) GitOps Workflow

1. Commit changes under `k8s/`
2. Push to GitHub `main`
3. ArgoCD detects drift and auto-syncs
4. `selfHeal: true` reconciles manual cluster drift

## 6) Verify Deployments

```bash
kubectl get ns
kubectl get all -n devsecops
kubectl describe app -n argocd telemedicine-app
```

## Notes

- Update `secret.yaml` with secure values before real deployment.
- The current manifests expect PostgreSQL endpoints in cluster DNS names from `configmap.yaml`.
- Liveness/readiness probes use each service `/health` endpoint on ports `8000/8001/8002`.
