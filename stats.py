import json
from datetime import date
from pathlib import Path

from config import DEFAULT_MINUTES

SAVE_FILE = Path.home() / ".waterlock.json"


def load_stats(path=SAVE_FILE):
    today = str(date.today())
    try:
        data = json.loads(Path(path).read_text())
        if not isinstance(data, dict):
            data = {}
    except (OSError, ValueError):
        data = {}
    if data.get("date") != today:
        data = {
            "date": today,
            "glasses": 0,
            "interval": data.get("interval", DEFAULT_MINUTES),
        }
    return data


def save_stats(data, path=SAVE_FILE):
    try:
        Path(path).write_text(json.dumps(data))
    except OSError:
        pass
