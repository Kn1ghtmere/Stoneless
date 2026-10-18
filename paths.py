import os 
import sys

def data_dir()  -> str:
    """per user flder for the database and settings and the token and same ideas for both windows and linux"""

    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    path = os.path.join(base, "Stoneless")
    os.makedirs(path, exist_ok =True)
    return path

