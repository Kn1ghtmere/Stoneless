import os
import sys
import time

def heartbeat_age(path, now=None):
    now = time.time() if now is None else now
    try:
        return now - os.path.getmtime(path)
    except OSError:
        return None


def should_kill(age, stale_seconds):
    return age is not None and age > stale_seconds


def remove(path):
    try:
        os.remove(path)
    except OSError:
        pass


def main(argv):
    if len(argv) < 5:
        return 1

    pid = int(argv[1])
    created = float(argv[2])
    path = argv[3]
    stale = float(argv[4])

    try:
        import psutil
    except ImportError:
        return 1

    while True:
        time.sleep(2)

        age = heartbeat_age(path)
        if age is None:
            return 0

        proc = None
        try:
            proc = psutil.Process(pid)
            same = abs(proc.create_time() - created) < 2
        except psutil.NoSuchProcess:
            same = False

        if not same:
            remove(path)
            return 0

        if should_kill(age, stale):
            try:
                proc.kill()
            except psutil.Error:
                pass
            remove(path)
            return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
