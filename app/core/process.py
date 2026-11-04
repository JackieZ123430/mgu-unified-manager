import os
import subprocess
import threading
from pathlib import Path

class ProcessRunner:
    def __init__(self, logger):
        self.logger = logger
        self._lock = threading.Lock()

    def run(self, argv, cwd: Path, emit, timeout=3600, env=None):
        argv = [str(x) for x in argv]
        self.logger.info("Executing component=%s", Path(argv[0]).name if argv else "unknown")
        emit("$ " + " ".join(argv))
        try:
            proc = subprocess.Popen(
                argv, cwd=str(cwd), stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                errors="replace", bufsize=1, env=env or os.environ.copy()
            )
            lines = []
            try:
                for line in iter(proc.stdout.readline, ""):
                    line = line.rstrip("\r\n")
                    lines.append(line)
                    emit(line)
                rc = proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                emit("ERROR: process timed out and was terminated.")
                return 124, "\n".join(lines)
            output = "\n".join(lines)
            self.logger.info("Process finished rc=%s", rc)
            return rc, output
        except FileNotFoundError as exc:
            emit(f"ERROR: executable not found: {exc.filename}")
            self.logger.exception("Executable missing")
            return 127, str(exc)
        except Exception as exc:
            emit(f"ERROR: {exc}")
            self.logger.exception("Process failed")
            return 1, str(exc)
