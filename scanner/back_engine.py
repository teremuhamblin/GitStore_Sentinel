import os
import shutil
from datetime import datetime


class BackupEngine:
    def __init__(self, backup_root, logger):
        self.backup_root = backup_root
        self.log = logger
        os.makedirs(self.backup_root, exist_ok=True)

    def create_backup(self, repo_name, repo_path):
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        backup_name = f"{repo_name}-{timestamp}"
        backup_path = os.path.join(self.backup_root, backup_name)

        self.log(f"[BACKUP] Création de la sauvegarde {backup_name}")
        shutil.make_archive(backup_path, "zip", repo_path)
        self.log(f"[BACKUP] Archive créée: {backup_path}.zip")
