"""
===========================================================
 GitStore Sentinel — Module Scanner
 Légion Cyber Défense — Unité de Surveillance Git
===========================================================

Ce package regroupe les trois modules principaux :
 - RepoMonitor      : Surveillance et synchronisation des dépôts Git
 - SecurityChecker  : Analyse de sécurité (fichiers sensibles, secrets)
 - BackupEngine     : Système de sauvegarde horodatée des dépôts

Tous les modules sont exposés ici pour simplifier les imports :
    from scanner import RepoMonitor, SecurityChecker, BackupEngine
"""

from .repo_monitor import RepoMonitor
from .security_check import SecurityChecker
from .backup_engine import BackupEngine

__all__ = [
    "RepoMonitor",
    "SecurityChecker",
    "BackupEngine"
]
