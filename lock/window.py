import tkinter as tk

from config import BG, DIM, GOAL, SIP_SECONDS, TEXT, WINDOW_CLASS
from lock.emergency import EmergencyPanel
from lock.platform_tools import force_foreground
from lock.view import LockView


class LockWindow(tk.Toplevel):
    def __init__(self, root, monitor, interactive, glasses, on_drink, on_emergency):
        super().__init__(root, class_=WINDOW_CLASS)
        self.monitor = monitor
        self.interactive = interactive
        self.view = None
        self.emergency = None

        self.title("Water Lock")
        self.configure(bg=BG, cursor="arrow")
        self.geometry("%dx%d+%d+%d" % (monitor.width, monitor.height, monitor.x, monitor.y))
        self.update_idletasks()
        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        if interactive:
            self.view = LockView(self, glasses, GOAL, SIP_SECONDS, on_drink)
            self.view.place(relx=0.5, rely=0.48, anchor="center")
            self.emergency = EmergencyPanel(self, on_emergency)
            self.emergency.place(relx=0.5, rely=0.95, anchor="center")
        else:
            tk.Label(self, text="water break", font=("TkDefaultFont", 38, "bold"), bg=BG, fg=TEXT).place(
                relx=0.5, rely=0.46, anchor="center"
            )
            tk.Label(
                self,
                text="finish your break on the main screen",
                font=("TkDefaultFont", 14),
                bg=BG,
                fg=DIM,
            ).place(relx=0.5, rely=0.54, anchor="center")

        force_foreground(self)

    def raise_up(self):
        self.lift()
        self.attributes("-topmost", True)
        force_foreground(self)
        if self.interactive and self.focus_displayof() is None:
            self.focus_force()
