import os
from pathlib import Path
from app.core.config import STORE_REPO, STORE_INSTALLER, STORE_DEPLOY, find_executable

class MGUStoreAdapter:
    """Runs the unmodified upstream Node.js installer/deploy CLI."""
    def __init__(self, runner, emit):
        self.runner = runner
        self.emit = emit
        self.node = find_executable("node")

    def _require_node(self):
        if not self.node:
            raise RuntimeError("Node.js was not found. Install Node.js 18 or newer and reopen the manager.")
        if not STORE_INSTALLER.is_file():
            raise FileNotFoundError(f"MGU Store installer missing: {STORE_INSTALLER}")

    def install_store(self, identity, extra=()):
        self._require_node()
        if not identity or not Path(identity).is_file():
            raise RuntimeError("A valid root SSH private key is required. Run SSH provisioning first or select a key in Settings.")
        args = [self.node, str(STORE_INSTALLER), "first-install",
                "--identity", str(identity), "--no-restart-prompt", *extra]
        return self.runner.run(args, STORE_REPO, self.emit, timeout=3600)

    def deploy_command(self, command, identity, extra=()):
        self._require_node()
        if not STORE_DEPLOY.is_file():
            raise FileNotFoundError(f"MGU deploy command missing: {STORE_DEPLOY}")
        if not identity or not Path(identity).is_file():
            raise RuntimeError("A valid root SSH private key is required.")
        args = [self.node, str(STORE_DEPLOY), command, *extra,
                "--identity", str(identity)]
        return self.runner.run(args, STORE_REPO, self.emit, timeout=3600)

    def node_version(self):
        if not self.node:
            return "Not installed"
        import subprocess
        try:
            p = subprocess.run([self.node, "--version"], capture_output=True,
                               text=True, timeout=10)
            return p.stdout.strip() or p.stderr.strip()
        except Exception as exc:
            return str(exc)
