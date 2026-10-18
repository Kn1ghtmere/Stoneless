import pystray
from PIL import Image, ImageDraw

import config


def make_image():
    img = Image.new("RGBA",(64,64),(0,0,0,0))
    ImageDraw.Draw(img).ellipse((6, 6, 58, 58), fill=config.WATER)
    return img


class Tray:

    def __init__(self, on_open, on_quit):
        menu = pystray.Menu(
            pystray.MenuItem("Open Stoneless", on_open, default=True),
            pystray.MenuItem("Quit", on_quit),
        )
        self.icon = pystray.Icon("Stoneless", make_image(), "Stoneless", menu)

    def start(self):
        self.icon.run_detached()

    def stop(self):
        self.icon.stop()