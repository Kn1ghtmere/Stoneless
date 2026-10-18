import ctypes
import os 
import platform
import sys


def enable_dpi_awareness():
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass



def compositor_warning():
    if os.environ.get("XDG_SESSION_TYPE") == "wayland":
        return "wayland detected: always-on-top popups may be ignored."

    return None


def describe():
    return f"{platform.system()} {platform.release()}"