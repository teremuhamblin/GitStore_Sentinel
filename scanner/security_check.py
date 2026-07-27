import os
import re
from datetime import datetime

REPORT_DIR_NAME = "reports"


class SecurityChecker:
    def __init__(self, logger):
        self.log = logger
        self.sensitive_patterns = [
            r"AKIA[0-9A-Z]{16}",          # Exemple clé AWS
            r"(?i)api[_-]?key\s*[:=]\s*['\"][0-9a-zA-Z]{16,}['\"]",
            r"(?i)token\s*[:=]\s*['\"][0-9a-zA-Z]{16,}['\"]"
        ]
        self.sensitive_files = [
            ".env",
            "id_rsa",
            "id_rsa.pub",
            "config.yml",
            "config.yaml",
            "secrets.json"
        ]

    def scan_repo(self, repo_path):
        self.log(f"[SEC] Scan de sécurité pour {repo_path}")
        findings = {
            "repo_path": repo_path,
            "timestamp": datetime.utcnow().isoformat(),
            "sensitive_files_found": [],
            "patterns_found": []
        }

        for root, dirs, files in os.walk(repo_path):
            for fname in files:
                rel_path = os.path.relpath(os.path.join(root, fname), repo_path)

                if fname in self.sensitive_files:
                    self.log(f"[SEC] Fichier sensible détecté: {rel_path}")
                    findings["sensitive_files_found"].append(rel_path)

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

    def save_report(self, repo_name, report):
        base_log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
        reports_dir = os.path.join(base_log_dir, REPORT_DIR_NAME)
        os.makedirs(reports_dir, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        filename = f"security-{repo_name}-{timestamp}.json"
        path = os.path.join(reports_dir, filename)

        import json
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log(f"[SEC] Rapport sauvegardé: {path}")
