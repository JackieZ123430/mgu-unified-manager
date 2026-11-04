import contextlib
import io
import os
import sys
import threading
from pathlib import Path

from app.core.config import SSH_REPO, SSH_ENTRY

class QueueWriter(io.TextIOBase):
    def __init__(self, emit):
        self.emit = emit
        self.pending = ""
    def write(self, value):
        self.pending += str(value)
        while "\n" in self.pending:
            line, self.pending = self.pending.split("\n", 1)
            self.emit(line)
        return len(value)
    def flush(self):
        if self.pending:
            self.emit(self.pending)
            self.pending = ""

class SSHRootAdapter:
    """Calls the original Python CLI entry point; no vendor source edits."""
    _execution_lock = threading.Lock()

    def __init__(self, emit, logger):
        self.emit = emit
        self.logger = logger

    def run(self, args):
        if not SSH_ENTRY.is_file():
            raise FileNotFoundError(f"SSH repository entry point missing: {SSH_ENTRY}")
        import sys
        sys.path.insert(0, str(SSH_REPO))
        import ssh_enable
        with self._execution_lock:
            old_out, old_err = sys.stdout, sys.stderr
            writer = QueueWriter(self.emit)
            try:
                sys.stdout = sys.stderr = writer
                rc = ssh_enable.main(list(args))
                writer.flush()
                return 0 if rc is None else int(rc)
            except SystemExit as exc:
                writer.flush()
                return int(exc.code) if isinstance(exc.code, int) else 1
            except Exception:
                self.logger.exception("SSH-root operation failed")
                raise
            finally:
                writer.flush()
                sys.stdout, sys.stderr = old_out, old_err

    def discover(self, emit):
        sys.path.insert(0, str(SSH_REPO))
        from mgu7 import discovery
        return discovery.discover(log=lambda *a, **k: emit(" ".join(map(str, a))))
