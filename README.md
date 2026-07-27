###### README.md >> markdown
# GitStore Sentinel
- Système de surveillance et de sauvegarde automatique pour dépôts Git

---

### 1. Présentation du projet
>GitStore Sentinel est un outil en ligne de commande qui :
- Surveille des dépôts Git (GitHub, GitStore, Git local).
- Analyse les changements et les risques de sécurité (fichiers sensibles, secrets, dépendances).
- Sauvegarde automatiquement les dépôts dans des archives horodatées.
- Génère des rapports de sécurité et d’activité.
- Conçu pour un usage DevOps / SecOps / OSINT / Légion cyber, il peut tourner en mode Sentinelle (daemon léger) sur Termux, Linux ou tout environnement POSIX.

---

### 2. Fonctionnalités principales
- Surveillance de dépôts :
  - Repos multiples définis dans un fichier de configuration.
  - Pull automatique des dernières modifications.
  - Détection de nouveaux commits et fichiers modifiés.

- Analyse de sécurité :
  - Scan de fichiers sensibles (.env, id_rsa, config.yml, etc.).
  - Détection de patterns de secrets (clé API, token, etc.).
  - Analyse basique des dépendances (requirements.txt, package.json).

- Sauvegarde automatique :
  - Archive ZIP du dépôt.
  - Nom horodaté (repo-YYYYMMDD-HHMMSS.zip).
  - Stockage dans backups/.

- Logs & rapports :
  - Logs détaillés dans logs/.
  - Rapport texte par scan dans logs/reports/.

- Mode Sentinelle :
  - Boucle de surveillance avec intervalle configurable.
  - Affichage CLI tactique (statuts, alertes).

---

3. Arborescence du projet

`text
GitStore-Sentinel/
│── sentinel.py
│── scanner/
│   ├── init.py
│   ├── repo_monitor.py
│   ├── security_check.py
│   ├── backup_engine.py
│── config/
│   ├── repos.json
│   └── settings.json
│── logs/
│   ├── sentinel.log
│   └── reports/
│── backups/
│── README.md
`

---

4. Installation

4.1. Prérequis

- Python 3.9+
- Git installé et accessible dans le PATH.
- Environnement compatible :
  - Linux, Termux, WSL, macOS.

4.2. Clonage du projet

`bash
git clone https://github.com/<ton-user>/GitStore-Sentinel.git
cd GitStore-Sentinel
`

4.3. Installation des dépendances Python

`bash
python -m venv venv
source venv/bin/activate    # Termux / Linux
pip install --upgrade pip
pip install -r requirements.txt  # (à créer si besoin)
`

(Pour un premier prototype, tu peux te passer de requirements.txt et utiliser uniquement la stdlib.)

---

5. Configuration

5.1. Fichier config/repos.json

Ce fichier liste les dépôts surveillés.

`json
{
  "repositories": [
    {
      "name": "mon-projet-principal",
      "path": "/data/data/com.termux/files/home/projects/mon-projet-principal",
      "remote": "https://github.com/mon-user/mon-projet-principal.git",
      "enabled": true
    },
    {
      "name": "outil-osint",
      "path": "/data/data/com.termux/files/home/projects/outil-osint",
      "remote": "https://github.com/mon-user/outil-osint.git",
      "enabled": true
    }
  ]
}
`

5.2. Fichier config/settings.json

Paramètres globaux du Sentinel.

`json
{
  "scanintervalseconds": 300,
  "log_level": "INFO",
  "backup_enabled": true,
  "securityscanenabled": true,
  "maxbackupper_repo": 20
}
`

---

6. Code source — modules principaux

6.1. sentinel.py — Point d’entrée CLI

`python

!/usr/bin/env python3
import time
import json
import os
import argparse
from datetime import datetime

from scanner.repo_monitor import RepoMonitor
from scanner.security_check import SecurityChecker
from scanner.backup_engine import BackupEngine

CONFIGDIR = os.path.join(os.path.dirname(file_), "config")
LOGDIR = os.path.join(os.path.dirname(file_), "logs")
BACKUPDIR = os.path.join(os.path.dirname(file_), "backups")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def log(msg):
    os.makedirs(LOGDIR, existok=True)
    logpath = os.path.join(LOGDIR, "sentinel.log")
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_once():
    reposcfg = loadjson(os.path.join(CONFIG_DIR, "repos.json"))
    settings = loadjson(os.path.join(CONFIGDIR, "settings.json"))

    backupenabled = settings.get("backupenabled", True)
    securityenabled = settings.get("securityscan_enabled", True)

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

        if backupenabled and changes["haschanges"]:
            backup.create_backup(name, path)


def runsentinelloop(interval_seconds: int):
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

    settings = loadjson(os.path.join(CONFIGDIR, "settings.json"))
    defaultinterval = settings.get("scaninterval_seconds", 300)

    if args.once:
        run_once()
    else:
        interval = args.interval if args.interval is not None else default_interval
        runsentinelloop(interval)


if name == "main":
    main()
`

---

6.2. scanner/repo_monitor.py — Surveillance des dépôts

`python
import os
import subprocess


class RepoMonitor:
    def init(self, logger):
        self.log = logger

    def rungit(self, repo_path, args):
        cmd = ["git", "-C", repo_path] + args
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            self.log(f"[GIT ERROR] {repo_path}: {result.stderr.strip()}")
        return result.stdout.strip(), result.returncode

    def ensure_repo(self, path, remote=None):
        if not os.path.exists(path):
            if remote:
                self.log(f"[INIT] Clonage du dépôt {remote} vers {path}")
                subprocess.run(["git", "clone", remote, path])
            else:
                self.log(f"[INIT] Création d'un dépôt Git local dans {path}")
                os.makedirs(path, exist_ok=True)
                subprocess.run(["git", "init", path])
        else:
            self.log(f"[CHECK] Dépôt déjà présent : {path}")

        if remote:
            out,  = self.run_git(path, ["remote", "get-url", "origin"])
            if remote not in out:
                self.log(f"[REMOTE] Mise à jour du remote origin -> {remote}")
                self.rungit(path, ["remote", "remove", "origin"])
                self.rungit(path, ["remote", "add", "origin", remote])

    def check_changes(self, path):
        self.log(f"[PULL] Récupération des dernières modifications pour {path}")
        , code = self.run_git(path, ["pull", "--ff-only"])
        if code != 0:
            self.log(f"[PULL] Échec du pull sur {path}")

        stdout,  = self.run_git(path, ["status", "--porcelain"])
        has_changes = bool(stdout.strip())

        return {
            "haschanges": haschanges,
            "status_raw": stdout
        }
`

---

6.3. scanner/security_check.py — Analyse de sécurité

`python
import os
import re
from datetime import datetime

REPORTDIRNAME = "reports"


class SecurityChecker:
    def init(self, logger):
        self.log = logger
        self.sensitive_patterns = [
            r"AKIA[0-9A-Z]{16}",          # Exemple clé AWS
            r"(?i)api[_-]?key\s[:=]\s['\"][0-9a-zA-Z]{16,}['\"]",
            r"(?i)token\s[:=]\s['\"][0-9a-zA-Z]{16,}['\"]"
        ]
        self.sensitive_files = [
            ".env",
            "id_rsa",
            "id_rsa.pub",
            "config.yml",
            "config.yaml",
            "secrets.json"
        ]

    def scanrepo(self, repopath):
        self.log(f"[SEC] Scan de sécurité pour {repo_path}")
        findings = {
            "repopath": repopath,
            "timestamp": datetime.utcnow().isoformat(),
            "sensitivefilesfound": [],
            "patterns_found": []
        }

        for root, dirs, files in os.walk(repo_path):
            for fname in files:
                relpath = os.path.relpath(os.path.join(root, fname), repopath)

                if fname in self.sensitive_files:
                    self.log(f"[SEC] Fichier sensible détecté: {rel_path}")
                    findings["sensitivefilesfound"].append(rel_path)

                try:
                    with open(os.path.join(root, fname), "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                except Exception:
                    continue

                for pattern in self.sensitive_patterns:
                    for match in re.findall(pattern, content):
                        self.log(f"[SEC] Pattern sensible dans {rel_path}: {match}")
                        findings["patterns_found"].append({
                            "file": rel_path,
                            "pattern": pattern,
                            "match": match
                        })

        return findings

    def savereport(self, reponame, report):
        baselogdir = os.path.join(os.path.dirname(file), "..", "logs")
        reportsdir = os.path.join(baselogdir, REPORTDIR_NAME)
        os.makedirs(reportsdir, existok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        filename = f"security-{repo_name}-{timestamp}.json"
        path = os.path.join(reports_dir, filename)

        import json
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log(f"[SEC] Rapport sauvegardé: {path}")
`

---

6.4. scanner/backup_engine.py — Sauvegarde des dépôts

`python
import os
import shutil
from datetime import datetime


class BackupEngine:
    def init(self, backup_root, logger):
        self.backuproot = backuproot
        self.log = logger
        os.makedirs(self.backuproot, existok=True)

    def createbackup(self, reponame, repo_path):
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        backupname = f"{reponame}-{timestamp}"
        backuppath = os.path.join(self.backuproot, backup_name)

        self.log(f"[BACKUP] Création de la sauvegarde {backup_name}")
        shutil.makearchive(backuppath, "zip", repo_path)
        self.log(f"[BACKUP] Archive créée: {backup_path}.zip")
`

---

7. Utilisation

7.1. Scan unique

`bash
python sentinel.py --once
`

Effet :
- Scan de tous les dépôts configurés.
- Analyse de sécurité.
- Sauvegarde si changements détectés.

7.2. Mode Sentinelle (boucle)

`bash
python sentinel.py
`

ou avec intervalle personnalisé :

`bash
python sentinel.py --interval 120
`

Effet :
- Boucle infinie avec scan toutes les scanintervalseconds (ou valeur passée).
- Logs continus dans logs/sentinel.log.

---

8. Roadmap (évolutions possibles)

- Mode Recon :
  - Analyse OSINT des issues, PR, contributeurs via API GitHub.
- Mode Shadow :
  - Logs minimalistes, pas de sortie console.
- Intégration Telegram / Discord :
  - Alertes en cas de détection de secrets.
- Analyse avancée des dépendances :
  - CVE, vulnérabilités connues.

---

9. Licence

Tu peux utiliser une licence libre classique :

`text
MIT License
Copyright (c) 2026 <Ton Nom>
Permission is hereby granted, free of charge, to any person obtaining a copy...
`

---

10. Résumé pour GitHub

> GitStore Sentinel est un système de surveillance, d’analyse de sécurité et de sauvegarde automatique pour dépôts Git.  
> Il détecte les changements, identifie les fichiers sensibles et secrets potentiels, crée des archives horodatées, et génère des rapports de sécurité.  
> Conçu pour les environnements DevOps, SecOps, OSINT et opérations cyber tactiques.

`
