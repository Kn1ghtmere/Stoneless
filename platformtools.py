"""Everything OS-specific. Linux/macOS functions are harmless no-ops so you can develop on Fedora."""
import ctypes
import os
import platform
import sys
import threading

IS_WINDOWS = sys.platform.startswith("win")


def describe() -> str:
    session = os.environ.get("XDG_SESSION_TYPE", "")
    return f"{platform.system()} {platform.release()}" + (f" ({session})" if session else "")


def compositor_warning():
    if os.environ.get("XDG_SESSION_TYPE") == "wayland":
        return ("NOTE: Wayland session. Tk runs through XWayland, so 'always on top' is not enforced. "
                "Use STONELESS_DEV=1 for layout/logic; real lock behaviour must be tested on Windows.")
    return None


def enable_dpi_awareness():
    if not IS_WINDOWS:
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def force_foreground(win):
    if not IS_WINDOWS:
        try:
            win.focus_force()
        except Exception:
            pass
        return
    try:
        user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
        win.update_idletasks()
        hwnd = user32.GetParent(win.winfo_id()) or win.winfo_id()
        fg = user32.GetForegroundWindow()
        fg_thread = user32.GetWindowThreadProcessId(fg, None)
        me = kernel32.GetCurrentThreadId()
        user32.AttachThreadInput(fg_thread, me, True)
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
        user32.AttachThreadInput(fg_thread, me, False)
        win.focus_force()
    except Exception:
        pass


class _KeyBlocker:
    """Low-level keyboard hook on its own thread. Swallows the keys people use to escape.

    Cannot block Ctrl+Alt+Del or Win+L (Windows reserves them). That is fine: the lock
    also has an emergency exit, a 10 minute timeout and a watchdog.
    """

    WH_KEYBOARD_LL, WM_QUIT, LLKHF_ALTDOWN = 13, 0x0012, 0x20
    VK_TAB, VK_ESC, VK_F4, VK_CTRL, VK_LWIN, VK_RWIN = 0x09, 0x1B, 0x73, 0x11, 0x5B, 0x5C

    def __init__(self):
        self.thread = None
        self.thread_id = None
        self.ready = threading.Event()

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.ready.clear()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self.ready.wait(2)

    def stop(self):
        if self.thread and self.thread.is_alive() and self.thread_id:
            ctypes.windll.user32.PostThreadMessageW(self.thread_id, self.WM_QUIT, 0, 0)

    def _run(self):
        from ctypes import wintypes
        user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32

        class KBDLLHOOKSTRUCT(ctypes.Structure):
            _fields_ = [("vkCode", wintypes.DWORD), ("scanCode", wintypes.DWORD),
                        ("flags", wintypes.DWORD), ("time", wintypes.DWORD),
                        ("dwExtraInfo", ctypes.c_size_t)]

        hook_proc = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
        user32.SetWindowsHookExW.argtypes = [ctypes.c_int, hook_proc, wintypes.HINSTANCE, wintypes.DWORD]
        user32.SetWindowsHookExW.restype = ctypes.c_void_p
        user32.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
        user32.CallNextHookEx.restype = ctypes.c_ssize_t
        user32.UnhookWindowsHookEx.argtypes = [ctypes.c_void_p]
        user32.GetAsyncKeyState.restype = ctypes.c_short
        kernel32.GetModuleHandleW.restype = wintypes.HINSTANCE

        def proc(n_code, w_param, l_param):
            try:
                if n_code == 0:
                    kb = ctypes.cast(l_param, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                    vk = kb.vkCode
                    alt = bool(kb.flags & self.LLKHF_ALTDOWN)
                    ctrl = bool(user32.GetAsyncKeyState(self.VK_CTRL) & 0x8000)
                    if vk in (self.VK_LWIN, self.VK_RWIN):
                        return 1
                    if alt and vk in (self.VK_TAB, self.VK_ESC, self.VK_F4):
                        return 1
                    if ctrl and vk == self.VK_ESC:  
                        return 1
            except Exception:
                pass
            return user32.CallNextHookEx(None, n_code, w_param, l_param)

        callback = hook_proc(proc)  
        self.thread_id = kernel32.GetCurrentThreadId()
        msg = wintypes.MSG()
        user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 0) 
        hook = user32.SetWindowsHookExW(self.WH_KEYBOARD_LL, callback, kernel32.GetModuleHandleW(None), 0)
        self.ready.set()
        if not hook:
            return
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        user32.UnhookWindowsHookEx(hook)


_blocker = _KeyBlocker() if IS_WINDOWS else None


def block_keys():
    if _blocker:
        _blocker.start()


def unblock_keys():
    if _blocker:
        _blocker.stop()


_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_RUN_NAME = "Stoneless"


def _launch_command():
    if getattr(sys, "frozen", False):        
        return f'"{sys.executable}"'
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    return f'"{pythonw}" "{os.path.abspath(sys.argv[0])}"'


def set_autostart(enabled: bool) -> bool:
    if not IS_WINDOWS:
        return False
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, _RUN_NAME, 0, winreg.REG_SZ, _launch_command())
        else:
            try:
                winreg.DeleteValue(key, _RUN_NAME)
            except FileNotFoundError:
                pass
    return True