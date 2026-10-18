import atexit
import time
import traceback

import config
from config import MAX_LOCK_SECONDS, WATCHDOG_STALE_SECONDS
from lock import platform_tools
from lock.failsafe import FailSafe
from lock.monitors import get_monitors
from lock.window import LockWindow


class LockManager:
    def __init__(self, root, get_glasses, on_drink, on_skip):
        self.root = root
        self.get_glasses = get_glasses
        self.on_drink = on_drink
        self.on_skip = on_skip
        self,windows = []
        self.jobs = {}
        self.locked_at = 0.0
        self.failsafe = FailSafe(WATCHDOG_STALE_SECONDS)


        root.report_callback_exception = self.handle_error
        atexit.register(self.failsafe.stop)
        atexit.register(platform_tools.unblock_keys)



    @property
    def is_locked(self):
        return bool(self.windows)


    def lock(self):
        if self.windows:
            return False


        
        monitors = get_monitors(self.root)
        glasses = self.get_glasses()
        for index, monitor in enumerate(monitors):
            self.windows.append(
                LockWindow(self.root, monitor, index == 0, glasses, self.drank, self.emergency_exit)
            )

            self.locked_at = time.time()
            self.failsafe.start()
            if config.BLOCK_KEYS and not config.DEV:
                platform_tools.block_keys()
            self.keep_on_top()
            self.heartbeat()
            self.jobs["timeout"] = self.root.after(int(MAX_LOCK_SECONDS * 1000), self.timed_out)
            return True


    def unlock(self):
        for job in self.jobs.values():
            try :
                self.root.after_cancel(job)
            except Exception:
                pass
        self.jobs = {}


        platform_tools.unblock_keys()
        for window in self.windows:
            try:
                window.destroy()
            except Exception:
                pass

        self.windows = []
        self.failsafe.stop()




    def keep_on_top(self):
        for window in self.windows:
            window.raise_up ()
        self.jobs["raise"] = self.root.after(400, self.keep_on_top)


    def heartbeat(self):
        self.failsafe.beat()
        self.jobs["beat"] = self.root.after(1000, self.heartbeat)

    def drank(self):

        self.unlock()
        self.on_drink()

    def emergency_exit(self):
        self.unlock()
        self.on_skip("emergency")

    def timed_out(self):
        self.unlock()
        self.on_skip("timeout")


    def handle_error(self, exc_type, exc_value, exc_tb):
        traceback.print_exception(exc_type, exc_value, exc_tb)
        if self.windows:       
            self.unlock()