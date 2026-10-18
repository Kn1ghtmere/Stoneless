import json
import os

import config

from paths import data_dir


SETTINGS_PATH = os.path.join(data_dir(), "settings.json")


DEFAULTS = {
    "interval_minutes" : config.DEFAULT_MINUTES,
    "autostart": False,
    "server_url" : config.DEFAULT_SERVER_URL,

}

def load() -> dict:
    data = dict(DEFAULTS)
    try : 
        with open(SETTINGS_PATH) as f:
            data.update(json.load(f))
    except (OSError, ValueError):
        pass
    return data

def save(data: dict):
    with open(SETTINGS_PATH,"w") as f:
        json.dump(data, f , indent=2)


def update(**changes) -> dict:
    data = load()
    data.update(changes)
    save(data)
    return data


