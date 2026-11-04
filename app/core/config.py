from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[2]
VENDORS = ROOT / "vendors"
SSH_REPO = VENDORS / "idrive7-8-ssh-root"
STORE_REPO = VENDORS / "mgu-store"
SSH_ENTRY = SSH_REPO / "ssh_enable.py"
SSH_GUI_ASSETS = SSH_REPO / "data" / "assets"
STORE_INSTALLER = STORE_REPO / "deploy" / "mgu-install.js"
STORE_DEPLOY = STORE_REPO / "deploy" / "hu"

def find_executable(name):
    from shutil import which
    return which(name)

def default_identity(vin=""):
    enroll = SSH_REPO / "data" / "enrollments"
    if vin:
        safe = "".join(c for c in vin.upper() if c.isalnum() or c in "-_.") or vin
        candidates = [enroll / safe / "id_rsa"]
        candidates += [enroll / safe / "id_rsa.pkcs1.pem",
                       enroll / safe / "id_rsa.pkcs8.pem"]
        for p in candidates:
            if p.is_file():
                return p
    if enroll.is_dir():
        keys = []
        for folder in enroll.iterdir():
            for filename in ("id_rsa", "id_rsa.pkcs1.pem", "id_rsa.pkcs8.pem"):
                p = folder / filename
                if p.is_file():
                    keys.append(p)
        if keys:
            return max(keys, key=lambda p: p.stat().st_mtime)
    return None
