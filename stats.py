import json
import os
import sys
from datetime import datetime
from pathlib import Path


def default_path():
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path.home() / ".local" / "share"
    return base / "Stoneless" / "data.json"


def _key(now):
    return (now or datetime.now()).date().isoformat()


class Stats:

    def __init__(self, path=None):
        self.path = Path(path) if path else default_path()
        self.days = self._load()

    def _load(self):
        try:
            days = json.loads(self.path.read_text(encoding="utf-8")) ["days"]
            if not isinstance(days, dict):
                raise TypeError
            return days 
        except FileNotFoundError:
            return {}
        except (ValueError, KeyError, TypeError):
            self.path.replace(self.path.with_suffix(".bad"))
            return {}

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"days": self.days}, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def count(self, now=None):
        return len(self.days.get(_key(now), []))


    def add_drink(self, now=None):
        now = now or datetime.now()
        self.days.setdefault(_key(now), []).append(now.strftime("%H:%M"))
        self._save()
        return self.count(now)

    def undo_drink(self, now=None):
        key = _key(now)
        times = self.days.get(key)
        if not times:
            return 0
        times.pop()
        if not times:
            del self.days[key]
        self._save()
        return self.count(now)

    def history(self):
        return {day: len(times) for day, times in sorted(self.days.items())}