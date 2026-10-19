import argparse
import platform
import shutil
import sys
import time
import tkinter as tk

from lock import hyprland
from lock.failsafe import psutil
from lock.monitors import get_monitors
from lock.platform_tools import (
    compositor_warning,
    describe,
    desktop_name,
    enable_dpi_awareness,
    is_hyprland,
    platform_name,
    session_type,
)


def yes_no(value, no_text="no"):
    return "yes" if value else no_text


def collect_info(root, tk_version="unknown"):
    info = [
        ("platform", describe()),
        ("os", platform.platform()),
        ("python", sys.version.split()[0]),
        ("tk", tk_version),
        ("session", session_type() or "n/a"),
        ("desktop", desktop_name() or "n/a"),
        ("psutil (hang watchdog)", yes_no(psutil is not None, "no - run: pip install psutil")),
    ]

    if platform_name() == "linux":
        info.append(("xrandr", yes_no(shutil.which("xrandr"), "missing")))
        info.append(("wmctrl", yes_no(shutil.which("wmctrl"), "missing (optional, X11 only)")))
        info.append(("hyprctl", yes_no(shutil.which("hyprctl"), "missing")))

    if is_hyprland():
        version = hyprland.hyprland_version()
        if version:
            info.append(("hyprland version", ".".join(str(n) for n in version)))
        else:
            info.append(("hyprland version", "could not read it, run: hyprctl version"))
        info.append(("hyprland rule syntax", hyprland.rule_syntax(version)))

    info.append(("tk screen size", "%dx%d" % (root.winfo_screenwidth(), root.winfo_screenheight())))
    for index, monitor in enumerate(get_monitors(root)):
        flag = " (primary)" if monitor.primary else ""
        info.append(
            (
                "monitor %d" % (index + 1),
                "%dx%d at %d,%d%s" % (monitor.width, monitor.height, monitor.x, monitor.y, flag),
            )
        )
    return info


def pump(root, seconds):
    end = time.time() + seconds
    while time.time() < end:
        root.update()
        time.sleep(0.02)


def make_manager(root):
    from lock.manager import LockManager

    return LockManager(root, lambda: 0, lambda: None, lambda reason: None)


def run_lock_check(root, seconds=3):
    manager = make_manager(root)
    manager.lock()
    pump(root, seconds)

    lines = []
    for index, window in enumerate(manager.windows):
        monitor = window.monitor
        lines.append(
            "window %d: wanted %dx%d, got %dx%d, covered: %s, topmost: %s, fullscreen: %s"
            % (
                index + 1,
                monitor.width,
                monitor.height,
                window.winfo_width(),
                window.winfo_height(),
                window.covered,
                window.attributes("-topmost"),
                window.attributes("-fullscreen"),
            )
        )

    if is_hyprland():
        problems = hyprland.check_clients(hyprland.fetch_clients())
        if problems:
            lines.append("hyprland problems:")
            lines.extend("  - " + p for p in problems)
            lines.append("add these rules to your Hyprland config:")
            lines.append(hyprland.rules_snippet(hyprland.rule_syntax(hyprland.hyprland_version())))
        else:
            lines.append("hyprland rules look good (floating, pinned, fullscreen)")

    manager.unlock()
    return lines


def run_crash_test(root):
    manager = make_manager(root)
    manager.lock()
    root.after(500, lambda: 1 / 0)
    pump(root, 2)
    return ["still locked after a crash: %s (should be False)" % manager.is_locked]


def run_hang_test(root):
    if psutil is None:
        print("psutil is missing, the watchdog cannot run. pip install psutil")
        return
    manager = make_manager(root)
    manager.lock()
    pump(root, 2)
    print("freezing the app on purpose now. the watchdog should kill this process in about 15-20 seconds.")
    sys.stdout.flush()
    time.sleep(120)
    print("watchdog did NOT kill the app, something is wrong")
    manager.unlock()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Water Lock environment check")
    parser.add_argument("--lock", action="store_true", help="show a test lock for 3 seconds and check coverage")
    parser.add_argument("--crash-test", action="store_true", help="crash inside a callback while locked")
    parser.add_argument("--hang-test", action="store_true", help="freeze the app while locked, watchdog must kill it")
    args = parser.parse_args(argv)

    enable_dpi_awareness()
    root = tk.Tk()
    root.withdraw()

    for label, value in collect_info(root, str(root.tk.call("info", "patchlevel"))):
        print("%-24s %s" % (label, value))

    warning = compositor_warning()
    if warning:
        print()
        print(warning)

    if args.lock:
        print()
        for line in run_lock_check(root):
            print(line)
    if args.crash_test:
        print()
        for line in run_crash_test(root):
            print(line)
    if args.hang_test:
        print()
        run_hang_test(root)

    root.destroy()


if __name__ == "__main__":
    main()