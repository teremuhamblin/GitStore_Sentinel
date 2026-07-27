import os
import subprocess


class RepoMonitor:
    def __init__(self, logger):
        self.log = logger

    def _run_git(self, repo_path, args):
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
            out, _ = self._run_git(path, ["remote", "get-url", "origin"])
            if remote not in out:
                self.log(f"[REMOTE] Mise à jour du remote origin -> {remote}")
                self._run_git(path, ["remote", "remove", "origin"])
                self._run_git(path, ["remote", "add", "origin", remote])

    def check_changes(self, path):
        self.log(f"[PULL] Récupération des dernières modifications pour {path}")
        _, code = self._run_git(path, ["pull", "--ff-only"])
        if code != 0:
            self.log(f"[PULL] Échec du pull sur {path}")

        stdout, _ = self._run_git(path, ["status", "--porcelain"])
        has_changes = bool(stdout.strip())

        return {
            "has_changes": has_changes,
            "status_raw": stdout
        }
