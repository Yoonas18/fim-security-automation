import os
import hashlib
import time
import json
import requests

def load_config():
    with open("agent_config.json", "r") as f:
        return json.load(f)

def hash_file(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None

def scan(paths):
    results = {}
    for root_path in paths:
        if not os.path.exists(root_path):
            print(f"[WARNING] Path does not exist: {root_path}")
            continue

        for root, dirs, files in os.walk(root_path):
            for name in files:
                full = os.path.join(root, name)
                full = full.replace("\\", "/")
                h = hash_file(full)
                if h:
                    results[full] = h
    return results

def send_alert(backend, agent_id, file_path, event_type):
    try:
        requests.post(
            backend,
            json={
                "agent_id": agent_id,
                "file": file_path,
                "event": event_type
            },
            timeout=5
        )
        print(f"[SENT] {event_type}: {file_path}")
    except Exception as e:
        print("[POST ERROR]:", e)

if __name__ == "__main__":
    config = load_config()
    agent_id = config["agent_id"]
    backend = config["backend_url"]
    watch_paths = config["watch_paths"]

    print("[INFO] Agent started")
    print("[INFO] Watching:", watch_paths)
    print("[INFO] Backend:", backend)

    last_scan = scan(watch_paths)

    while True:
        time.sleep(5)

        current_scan = scan(watch_paths)

        # Detect NEW FILES
        for file in current_scan:
            if file not in last_scan:
                print(f"[NEW] {file}")
                send_alert(backend, agent_id, file, "file_created")

        # Detect MODIFIED FILES
        for file in current_scan:
            if file in last_scan and current_scan[file] != last_scan[file]:
                print(f"[MODIFIED] {file}")
                send_alert(backend, agent_id, file, "file_modified")

        # Detect DELETED FILES
        for file in last_scan:
            if file not in current_scan:
                print(f"[DELETED] {file}")
                send_alert(backend, agent_id, file, "file_deleted")

        last_scan = current_scan
