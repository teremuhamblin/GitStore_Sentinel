#!/usr/bin/env python3
# ============================================================
# GitStore Sentinel — Légion Cyber Défense
# Unité de Surveillance & Protection des Dépôts Git
# ============================================================

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


# ------------------------------------------------------------
# Chargement JSON sécurisé
# ------------------------------------------------------------
def load_json(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Fichier de configuration introuvable : {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Erreur JSON dans {path} : {e}")


# ------------------------------------------------------------
# Système de logs tactiques
# ------------------------------------------------------------
def log(msg, level="INFO"):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, "sentinel.log")

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] {msg}"

    print(line)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ------------------------------------------------------------
# Exécution d’un scan unique
# ------------------------------------------------------------
def run_once():
    try:
        repos_cfg = load_json(os.path.join(CONFIG_DIR, "repos.json"))
        settings = load_json(os.path.join(CONFIG_DIR, "settings.json"))
    except Exception as e:
        log(f"Erreur de chargement des configurations : {e}", "ERROR")
        return

    backup_enabled = settings.get("backup_enabled", True)
    security_enabled = settings.get("security_scan_enabled", True)

    monitor = RepoMonitor(log)
    security = SecurityChecker(log)
    backup = BackupEngine(BACKUP_DIR, log)

    repositories = repos_cfg.get("repositories", [])

    if not repositories:
        log("Aucun dépôt configuré dans repos.json.", "WARNING")
        return

    for repo in repositories:
        if not repo.get("enabled", True):
            continue

        name = repo.get("name", "UNKNOWN")
        path = repo.get("path")
        remote = repo.get("remote")

        if not path:
            log(f"Dépôt {name} ignoré : chemin manquant.", "ERROR")
            continue

        log(f"=== [REPO] {name} ===", "INFO")

        try:
            monitor.ensure_repo(path, remote)
            changes = monitor.check_changes(path)
        except Exception as e:
            log(f"Erreur lors de la surveillance du dépôt {name} : {e}", "ERROR")
            continue

        if changes.get("has_changes"):
            log(f"{name} : Nouveaux commits ou fichiers détectés.", "CHANGE")
        else:
            log(f"{name} : Aucun changement détecté.", "OK")

        if security_enabled:
            try:
                report = security.scan_repo(path)
                security.save_report(name, report)
            except Exception as e:
                log(f"Erreur analyse sécurité pour {name} : {e}", "ERROR")

        if backup_enabled and changes.get("has_changes"):
            try:
                backup.create_backup(name, path)
            except Exception as e:
                log(f"Erreur sauvegarde pour {name} : {e}", "ERROR")


# ------------------------------------------------------------
# Mode Sentinelle — boucle infinie
# ------------------------------------------------------------
def run_sentinel_loop(interval_seconds: int):
    log(f"Mode Sentinelle ACTIVÉ — intervalle {interval_seconds} sec.", "START")

    try:
        while True:
            log("=== Scan global démarré ===", "SCAN")
            run_once()
            log("=== Scan global terminé ===", "SCAN")
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        log("Arrêt manuel du mode Sentinelle.", "STOP")
    except Exception as e:
        log(f"Erreur critique dans le mode Sentinelle : {e}", "CRITICAL")


# ------------------------------------------------------------
# CLI principale
# ------------------------------------------------------------
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

    try:
        settings = load_json(os.path.join(CONFIG_DIR, "settings.json"))
    except Exception as e:
        log(f"Impossible de charger settings.json : {e}", "ERROR")
        return

    default_interval = settings.get("scan_interval_seconds", 300)

    if args.once:
        run_once()
    else:
        interval = args.interval if args.interval is not None else default_interval
        run_sentinel_loop(interval)


if __name__ == "__main__":
    main()
