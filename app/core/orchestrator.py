from app.adapters.ssh_root.adapter import SSHRootAdapter
from app.adapters.mgu_store.adapter import MGUStoreAdapter
from app.core.process import ProcessRunner

class Orchestrator:
    def __init__(self, emit, logger):
        self.emit = emit
        self.logger = logger
        self.runner = ProcessRunner(logger)
        self.ssh = SSHRootAdapter(emit, logger)
        self.store = MGUStoreAdapter(self.runner, emit)

    def health(self):
        import shutil, sys
        from app.core.config import SSH_ENTRY, STORE_INSTALLER
        return {
            "python": sys.version.split()[0],
            "node": self.store.node_version(),
            "ssh_cli": shutil.which("ssh") or "Not installed",
            "ssh_repository": SSH_ENTRY.is_file(),
            "store_repository": STORE_INSTALLER.is_file()
        }
