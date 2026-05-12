import hashlib
import json
import time
from pathlib import Path
from typing import Any

import requests


DEFAULT_CONFIG = Path(__file__).with_name("agent_config.json")


def load_config() -> dict[str, Any]:
    if not DEFAULT_CONFIG.exists():
        raise SystemExit("Missing agent_config.json. Copy agent_config.example.json and edit it first.")

    with DEFAULT_CONFIG.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


def hash_file(path: Path, max_file_size_mb: int) -> str | None:
    try:
        if path.stat().st_size > max_file_size_mb * 1024 * 1024:
            return None

        digest = hashlib.sha256()
        with path.open("rb") as file_handle:
            for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def should_skip(path: Path, ignored_names: set[str]) -> bool:
    return any(part in ignored_names for part in path.parts)


def scan(paths: list[str], ignored_names: set[str], max_file_size_mb: int) -> dict[str, dict[str, Any]]:
    results = {}

    for root_path_text in paths:
        root_path = Path(root_path_text).expanduser()
        if not root_path.exists():
            print(f"[warning] path does not exist: {root_path}")
            continue

        for file_path in root_path.rglob("*"):
            if not file_path.is_file() or should_skip(file_path, ignored_names):
                continue

            file_hash = hash_file(file_path, max_file_size_mb)
            if file_hash:
                normalized = file_path.resolve().as_posix()
                results[normalized] = {
                    "hash": file_hash,
                    "size": file_path.stat().st_size,
                }

    return results


def send_alert(config: dict[str, Any], file_path: str, event_type: str, evidence: dict[str, Any] | None) -> None:
    payload = {
        "agent_id": config["agent_id"],
        "file": file_path,
        "event": event_type,
        "hash": evidence.get("hash") if evidence else None,
        "size": evidence.get("size") if evidence else None,
    }
    headers = {"X-Agent-Key": config["api_key"]}

    try:
        response = requests.post(config["backend_url"], json=payload, headers=headers, timeout=5)
        response.raise_for_status()
        print(f"[sent] {event_type}: {file_path}")
    except requests.RequestException as exc:
        print("[post error]", exc)


def main() -> None:
    config = load_config()
    interval = int(config.get("scan_interval_seconds", 5))
    ignored_names = set(config.get("ignore_names", []))
    max_file_size_mb = int(config.get("max_file_size_mb", 100))
    watch_paths = config["watch_paths"]

    print("[info] agent started")
    print("[info] watching:", watch_paths)
    print("[info] backend:", config["backend_url"])

    last_scan = scan(watch_paths, ignored_names, max_file_size_mb)

    while True:
        time.sleep(interval)
        current_scan = scan(watch_paths, ignored_names, max_file_size_mb)

        for file_path, evidence in current_scan.items():
            if file_path not in last_scan:
                send_alert(config, file_path, "file_created", evidence)
            elif current_scan[file_path]["hash"] != last_scan[file_path]["hash"]:
                send_alert(config, file_path, "file_modified", evidence)

        for file_path in last_scan:
            if file_path not in current_scan:
                send_alert(config, file_path, "file_deleted", last_scan[file_path])

        last_scan = current_scan


if __name__ == "__main__":
    main()
