import os
import time
import tkinter as tk

import pytest

import lock.manager as manager_module
from lock.manager import LockManager


@pytest.fixture
def root():
    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        pytest.skip("no display available")
    try:
        r = tk.Tk()
    except tk.TclError:
        pytest.skip("cannot open a display")
    yield r
    r.destroy()


def pump(root, seconds):
    end = time.time() + seconds
    while time.time() < end:
        root.update()
        time.sleep(0.02)


def make_manager(root):
    events = []
    m = LockManager(
        root,
        lambda: 3,
        lambda: events.append("drink"),
        lambda reason: events.append("skip:" + reason),
    )
    return m, events


def test_lock_creates_windows_and_unlock_removes_them(root):
    m, events = make_manager(root)
    assert m.lock() is True
    assert m.is_locked
    assert m.lock() is False
    pump(root, 0.5)
    assert m.windows[0].interactive
    assert m.windows[0].winfo_exists()
    m.unlock()
    assert not m.is_locked
    assert m.windows == []


def test_drinking_unlocks_and_reports(root):
    m, events = make_manager(root)
    m.lock()
    pump(root, 0.3)
    m.windows[0].view.on_done()
    assert not m.is_locked
    assert events == ["drink"]


def test_emergency_exit_unlocks_and_reports(root):
    m, events = make_manager(root)
    m.lock()
    panel = m.windows[0].emergency
    panel.delay = 0
    panel.begin()
    pump(root, 0.3)
    panel.entry.insert(0, panel.code)
    panel.submit()
    assert not m.is_locked
    assert events == ["skip:emergency"]


def test_wrong_emergency_code_keeps_lock(root):
    m, events = make_manager(root)
    m.lock()
    panel = m.windows[0].emergency
    panel.delay = 0
    panel.begin()
    pump(root, 0.3)
    panel.entry.insert(0, "nope")
    panel.submit()
    assert m.is_locked
    assert events == []
    m.unlock()


def test_max_lock_time_releases_the_lock(root, monkeypatch):
    monkeypatch.setattr(manager_module, "MAX_LOCK_SECONDS", 0.4)
    m, events = make_manager(root)
    m.lock()
    pump(root, 1.0)
    assert not m.is_locked
    assert events == ["skip:timeout"]


def test_error_in_a_callback_releases_the_lock(root, capsys):
    m, events = make_manager(root)
    m.lock()
    root.after(50, lambda: 1 / 0)
    pump(root, 0.5)
    assert not m.is_locked


def test_sip_flow_enables_done_button(root, monkeypatch):
    m, events = make_manager(root)
    m.lock()
    view = m.windows[0].view
    view.sip_seconds = 1
    view.start_sip()
    pump(root, 2.5)
    assert str(view.button["state"]) == "normal"
    assert view.button["text"] == "i drank my water"
    m.unlock()
