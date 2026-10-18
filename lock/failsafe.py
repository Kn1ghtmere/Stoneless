import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None

HEARTBEAT_PATH = Path(tempfile.gettempdir()) / "waterlock.heartbeat"
WATCHDOG_SCRIPT = Path(__file__).with_name("watchdog.py")


class FailSafe:
    def __init__(self, stale_seconds, path=HEARTBEAT_PATH):
        self.stale_seconds = stale_seconds
        self.path = Path(path)
        self.proc = None

    @property
    def available(self):
        return psutil is not None

    def start(self):
        self.beat()
        if psutil is None:
            return False

        created = psutil.Process(os.getpid()).create_time()
        args = [
            sys.executable,
            str(WATCHDOG_SCRIPT),
            str(os.getpid()),
            repr(created),
            str(self.path),
            str(self.stale_seconds),
        ]
        kwargs = {
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }
        if sys.platform.startswith("win"):
            kwargs["creationflags"] = 0x08000000 | 0x00000200
        else:
            kwargs["start_new_session"] = True

        try:
            self.proc = subprocess.Popen(args, **kwargs)
        except OSError:
            self.proc = None
            return False
        return True

    def beat(self):
        try:
            self.path.write_text(str(time.time()))
        except OSError:
            pass

    def stop(self):
        try:
            self.path.unlink()
        except OSError:
            pass
        if self.proc is not None:
            try:
                self.proc.terminate()
            except OSError:
                pass
            self.proc = None
