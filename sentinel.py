#!/usr/bin/env python3
import time
import json
import os
import argparse
from datetime import datetime

from scanner.repo_monitor import RepoMonitor
from scanner.security_check import SecurityChecker
from scanner.backup_engine import BackupEngine

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "backups")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def log(msg):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, "sentinel.log")
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_once():
    repos_cfg = load_json(os.path.join(CONFIG_DIR, "repos.json"))
    settings = load_json(os.path.join(CONFIG_DIR, "settings.json"))

    backup_enabled = settings.get("backup_enabled", True)
    security_enabled = settings.get("security_scan_enabled", True)

    monitor = RepoMonitor(log)
    security = SecurityChecker(log)
    backup = BackupEngine(BACKUP_DIR, log)

    for repo in repos_cfg.get("repositories", []):
        if not repo.get("enabled", True):
            continue

        name = repo["name"]
        path = repo["path"]
        remote = repo.get("remote")

        log(f"=== [REPO] {name} ===")
        monitor.ensure_repo(path, remote)
        changes = monitor.check_changes(path)

        if changes["has_changes"]:
            log(f"[{name}] Nouveaux commits ou fichiers détectés.")
        else:
            log(f"[{name}] Aucun changement détecté.")

        if security_enabled:
            report = security.scan_repo(path)
            security.save_report(name, report)

        if backup_enabled and changes["has_changes"]:
            backup.create_backup(name, path)


def run_sentinel_loop(interval_seconds: int):
    log(f"Mode Sentinelle activé — intervalle {interval_seconds} s.")
    try:
        while True:
            log("=== Scan global démarré ===")
            run_once()
            log("=== Scan global terminé ===")
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        log("Arrêt manuel du mode Sentinelle.")


def main():
    parser = argparse.ArgumentParser(
        description="GitStore Sentinel — Surveillance et sauvegarde de dépôts Git."
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Exécuter un seul scan puis quitter."
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Intervalle en secondes pour le mode Sentinelle."
    )

    args = parser.parse_args()

    settings = load_json(os.path.join(CONFIG_DIR, "settings.json"))
    default_interval = settings.get("scan_interval_seconds", 300)

    if args.once:
        run_once()
    else:
        interval = args.interval if args.interval is not None else default_interval
        run_sentinel_loop(interval)


if __name__ == "__main__":
    main()
