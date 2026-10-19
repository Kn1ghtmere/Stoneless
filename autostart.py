import sys
from pathlib import Path

APP_NAME = "Stoneless"
RUN_KEY = r"Software\Micorosft\Windows\CurrentVersion\Run"



def is_supported():
    return sys.platform == "win32"


def _command():
    if getattr(sys, "frozen",False):
        return f'"{sys.executable}" --minimized'
    exe = Path(sys.executable)
    windowless = exe.with_name("pythonw.exe")
    if windowless.exists():
        exe = windowless
    script = Path(__file__).resolve().with_name("main.py")
    return f'"{exe}" "{script}" --minimized'



def is_enabled():
    if not is_supported():
        return False
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.QueryValueEx(key, APP_NAME)
            return True
    except FileNotFoundError:
        return False


def enable():
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0 , winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, APP_NAME, 0 , winreg.REG_SZ, _command())


def disable():
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0 , winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, APP_NAME)

    except FileNotFoundError:
        pass