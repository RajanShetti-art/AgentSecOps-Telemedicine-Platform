# Helm Install Commands (Minikube + local testing)

## 1) Create namespaces

```bash
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace falco --dry-run=client -o yaml | kubectl apply -f -
```

## 2) Add required Helm repositories

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update
```

## 3) Install Prometheus + Grafana

```bash
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  -f k8s/observability/kube-prometheus-stack-values.yaml
```

## 4) Install Loki + Promtail for log aggregation

```bash
helm upgrade --install loki grafana/loki-stack \
  --namespace monitoring \
  -f k8s/observability/loki-values.yaml
```

## 5) Install Falco runtime security with custom rules

```bash
helm upgrade --install falco falcosecurity/falco \
  --namespace falco \
  -f k8s/observability/falco-values.yaml
```

## 6) Apply service monitoring and alerts

```bash
kubectl apply -f k8s/observability/servicemonitors.yaml
kubectl apply -f k8s/observability/prometheus-alerts.yaml
kubectl apply -f k8s/observability/grafana-dashboards-configmap.yaml
```

## 7) Access Grafana locally

```bash
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80
```

Default username:

```text
admin
```

Get password:

```bash
kubectl get secret -n monitoring kube-prometheus-stack-grafana -o jsonpath='{.data.admin-password}' | base64 --decode
```
