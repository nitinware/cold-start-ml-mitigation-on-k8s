# Cold-Start ML Mitigation on Kubernetes

This project demonstrates **cold-start mitigation for ML models** running on Kubernetes StatefulSets using **Istio traffic mirroring** and a **dynamic pod labeling controller**.
---

## Prerequisites
- Kubernetes cluster (Minikube recommended for local testing)
- kubectl installed and configured
- Docker installed (for building the controller image)
- Python 3.10+ (for local testing, optional)

---

## 1. Build Docker Image for Controller
docker build -t your-dockerhub-username/dynamic-label-controller:latest .
docker push your-dockerhub-username/dynamic-label-controller:latest

For Minikube local build:
eval $(minikube docker-env)
docker build -t dynamic-label-controller:latest .

---

## 2. Apply RBAC (ServiceAccount)
kubectl apply -f k8s/controller-rbac.yaml

---

## 3. Deploy ML StatefulSet
kubectl apply -f k8s/ml-statefulset.yaml
kubectl get pods -l app=ml-model --watch

---

## 4. Deploy Dynamic Labeling Controller
kubectl apply -f k8s/controller-deployment.yaml
kubectl get pods -l app=dynamic-label-controller
kubectl logs -f deployment/dynamic-label-controller

---

## 5. Verify Cold-Start Mitigation
kubectl delete pod ml-model-0
kubectl get pods -l app=ml-model --show-labels

---

## 6. Optional: Local Testing
python controller/dynamic_label_controller.py
# Requires Python 3.10+ and 'kubernetes' package (pip install kubernetes)

---

## 7. GitHub Repository
https://github.com/yourusername/cold-start-ml-mitigation-on-k8s

---

## 8. Notes
- The dynamic pod labeling controller is generic: can be adapted to other readiness signals (HTTP/gRPC endpoints, metrics, event triggers)
- Works in Minikube or production Kubernetes clusters
- RBAC ensures minimal permissions and security
