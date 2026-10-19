import config

DEFAULT = "Deep Sea"

THEMES = {
    "Deep Sea": {
        "BG" : "#0b1d2e",
        "SURFACE" : "#14324d",
        "TEXT" : "#eaf6ff",
        "DIM": "#8db4d0",
        "WATER": "#38b6ec",
        "SHINE" : "#bfe9ff",
        "BUTTON": "#1a6aa6",
        "BUTTON_ACTIVE": "#2784c8",
    },
    "Midnight" : {
        "BG" : "#0f1417",
        "SURFACE": "#1a2227",
        "TEXT": "#eef3f5",
        "DIM": "#8a9aa5",
        "WATER" : "#3fd0c0",
        "SHINE" : "#b8f3ec",
        "BUTTON": "#23726b",
        "BUTTON_ACTIVE": "#2e9087",
    },
    "Daylight": {
        "BG" : "#eef4f8",
        "SURFACE": "#dbe8f1",
        "TEXT" : "#0e2f46",
        "DIM" : "#4f6e84",
        "WATER": "1b86bb",
        "SHINE": "#ffffff",
        "BUTTON": "#1b6fa8",
        "BUTTON_ACTIVE": "#165a89",

    },
}


def apply(name):
    if name not in THEMES:
        name = DEFAULT
    for key, value in THEMES[name].items():
        setattr(config, key, value)
    config.THEME = name 