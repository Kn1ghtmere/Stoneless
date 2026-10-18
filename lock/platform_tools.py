import os
import sys


def platform_name():
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform.startswith("linux"):
        return "linux"
    return "other"


def session_type():
    if platform_name() != "linux":
        return ""
    kind = os.environ.get("XDG_SESSION_TYPE", "").lower()
    if kind:
        return kind
    if os.environ.get("WAYLAND_DISPLAY"):
        return "wayland"
    if os.environ.get("DISPLAY"):
        return "x11"
    return ""


def desktop_name():
    return os.environ.get("XDG_CURRENT_DESKTOP", "").lower()


def is_hyprland():
    return bool(os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")) or "hyprland" in desktop_name()


def describe():
    name = platform_name()
    if name == "linux":
        return "linux, session: %s, desktop: %s" % (session_type() or "unknown", desktop_name() or "unknown")
    return name


def compositor_warning():
    if platform_name() != "linux":
        return ""
    if is_hyprland():
        return (
            "Hyprland detected. Add the window rules from docs/HYPRLAND.md so the lock "
            "screen is fullscreen, floating and pinned. Run `hyprctl version` to see which "
            "syntax your version uses."
        )
    if session_type() == "wayland":
        return (
            "Wayland session. The lock screen runs through XWayland, so it covers the screen "
            "but your desktop shortcuts keep working. This is a soft lock."
        )
    return ""


def enable_dpi_awareness():
    if platform_name() != "windows":
        return
    import ctypes

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def force_foreground(widget):
    if platform_name() != "windows":
        return
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        user32.GetParent.argtypes = [wintypes.HWND]
        user32.GetParent.restype = wintypes.HWND
        user32.SetWindowPos.argtypes = [
            wintypes.HWND,
            wintypes.HWND,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.UINT,
        ]
        user32.SetForegroundWindow.argtypes = [wintypes.HWND]

        inner = widget.winfo_id()
        hwnd = user32.GetParent(inner) or inner
        flags = 0x0001 | 0x0002 | 0x0040
        user32.SetWindowPos(hwnd, wintypes.HWND(-1), 0, 0, 0, 0, flags)
        user32.SetForegroundWindow(hwnd)
    except Exception:
        pass
