import tkinter as tk

from lock.logger import get_logger

log = get_logger()

TOLERANCE = 4


def covers(width, height, monitor):
    return abs(width - monitor.width) <= TOLERANCE and abs(height - monitor.height) <= TOLERANCE


def apply_borderless(window):
    monitor = window.monitor
    try:
        window.attributes("-fullscreen", False)
    except tk.TclError:
        pass
    window.overrideredirect(True)
    window.geometry("%dx%d+%d+%d" % (monitor.width, monitor.height, monitor.x, monitor.y))
    window.attributes("-topmost", True)
    window.lift()


def ensure_covering(window):
    window.update_idletasks()
    monitor = window.monitor
    width = window.winfo_width()
    height = window.winfo_height()

    if covers(width, height, monitor):
        return True

    log.warning(
        "fullscreen did not cover the monitor (got %dx%d, wanted %dx%d), using borderless fallback",
        width,
        height,
        monitor.width,
        monitor.height,
    )
    apply_borderless(window)
    window.update_idletasks()

    ok = covers(window.winfo_width(), window.winfo_height(), monitor)
    if ok:
        log.info("borderless fallback worked")
    else:
        log.error("borderless fallback also failed, this window manager is ignoring us")
    return ok