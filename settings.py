import json

import config

from stats import default_path

LIMITS = {
    "GOAL" : (1, 30),
    "DEFAULT_MINUTES": (1, 240),
    "SNOOZE_MINUTES": (1, 60),
}

def path ():
    return default_path().with_name("settings.json")


def load():
    try:
        saved = json.loads(path().read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return
    if not isinstance(saved, dict):
        return
    for key, (low, high) in LIMITS.items():
        value = saved.get(key)
        if isinstance(value, int) and low <= value <= high:
            setattr(config, key, value)



def save():
    p = path()
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {key: getattr(config, key) for key in LIMITS}
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def update(values):
    for key, value in values.items():
        setattr(config, key, value)
    save()