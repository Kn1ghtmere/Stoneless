import os
import subprocess
import sys
import time

import pytest

from lock import watchdog
from lock.failsafe import FailSafe, psutil


def test_heartbeat_age_and_decision(tmp_path):
    path = tmp_path / "beat"
    assert watchdog.heartbeat_age(str(path)) is None
    path.write_text("x")
    age = watchdog.heartbeat_age(str(path), now=os.path.getmtime(path) + 30)
    assert age == pytest.approx(30)
    assert watchdog.should_kill(age, 15)
    assert not watchdog.should_kill(5, 15)
    assert not watchdog.should_kill(None, 15)


def test_failsafe_creates_and_removes_heartbeat(tmp_path):
    fs = FailSafe(15, path=tmp_path / "beat")
    fs.start()
    assert (tmp_path / "beat").exists()
    fs.stop()
    assert not (tmp_path / "beat").exists()


@pytest.mark.skipif(psutil is None, reason="psutil not installed")
def test_watchdog_kills_a_hung_process(tmp_path):
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
    try:
        created = psutil.Process(child.pid).create_time()
        beat = tmp_path / "beat"
        beat.write_text("x")
        old = time.time() - 60
        os.utime(beat, (old, old))

        subprocess.run(
            [sys.executable, watchdog.__file__, str(child.pid), repr(created), str(beat), "5"],
            timeout=20,
        )
        child.wait(timeout=5)
        assert child.returncode is not None
        assert not beat.exists()
    finally:
        if child.poll() is None:
            child.kill()


@pytest.mark.skipif(psutil is None, reason="psutil not installed")
def test_watchdog_leaves_a_healthy_process_alone(tmp_path):
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(8)"])
    try:
        created = psutil.Process(child.pid).create_time()
        beat = tmp_path / "beat"
        beat.write_text("x")

        dog = subprocess.Popen(
            [sys.executable, watchdog.__file__, str(child.pid), repr(created), str(beat), "30"]
        )
        time.sleep(3)
        assert child.poll() is None
        beat.unlink()
        dog.wait(timeout=10)
        assert dog.returncode == 0
    finally:
        child.kill()


