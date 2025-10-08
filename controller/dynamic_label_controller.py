#!/usr/bin/env python3
"""
Dynamic Labeling Controller for Cold-Start Mitigation
Assigns pods to 'canary' until model is loaded, then switches to 'stable'.
"""

import time
from kubernetes import client, config, watch
from kubernetes.stream import stream

# --- Configuration ---
NAMESPACE = "default"
APP_LABEL = "app=ml-model"
CHECK_INTERVAL = 5  # seconds

# --- Load Kubernetes config ---
config.load_kube_config()
v1 = client.CoreV1Api()

# --- Function to assign/update pod label ---
def label_pod(name, role):
    body = {"metadata": {"labels": {"role": role}}}
    try:
        v1.patch_namespaced_pod(name, NAMESPACE, body)
        print(f"[INFO] Pod '{name}' labeled as '{role}'")
    except Exception as e:
        print(f"[ERROR] Failed to label pod '{name}': {e}")

# --- Function to check if model is loaded in pod ---
def is_model_loaded(pod_name):
    try:
        resp = stream(
            v1.connect_get_namespaced_pod_exec,
            pod_name,
            NAMESPACE,
            command=["test", "-f", "/tmp/model_loaded"],
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
        )
        return resp == ""
    except Exception as e:
        print(f"[WARN] Cannot exec into pod '{pod_name}': {e}")
        return False

# --- Watch loop ---
w = watch.Watch()
print("[INFO] Starting Dynamic Labeling Controller...")
while True:
    try:
        for event in w.stream(
            v1.list_namespaced_pod,
            namespace=NAMESPACE,
            label_selector=APP_LABEL,
            timeout_seconds=30,
        ):
            pod = event["object"]
            pod_name = pod.metadata.name
            labels = pod.metadata.labels or {}

            model_ready = is_model_loaded(pod_name)

            # Assign canary if model not loaded
            if not model_ready and labels.get("role") != "canary":
                label_pod(pod_name, "canary")

            # Promote to stable if model loaded
            elif model_ready and labels.get("role") != "stable":
                label_pod(pod_name, "stable")

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print(f"[ERROR] Controller watch loop exception: {e}")
        time.sleep(CHECK_INTERVAL)
