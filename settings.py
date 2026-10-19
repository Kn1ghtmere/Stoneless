import json

import config

import themes

from stats import default_path

LIMITS = {
    "GOAL" : (1, 30),
    "DEFAULT_MINUTES": (1, 240),
    "SNOOZE_MINUTES": (1, 60),
}

CHOICES = {
    "THEME": list(themes.THEMES),
    "LAST_TAB": list(config.TABS)
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
    for key, options in CHOICES.items():
        value = saved.get(key)
        if value in options:
            setattr(config, key, value)



def save():
    p = path()
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {key: getattr(config, key) for key in (*LIMITS, *CHOICES)}
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def update(values):
    for key, value in values.items():
        setattr(config, key, value)
    save()