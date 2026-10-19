import tkinter as tk
from datetime import date

import autostart
import config
import info
from widgets import FONT, Glass, WeekChart, make_buttons


class HomePage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=config.BG)
        self.app = app

        self.glass = Glass(self)
        self.glass.pack(pady=(24, 0))

        self.count = tk.Label(self, font=(FONT, 40, "bold"),
                              bg=config.BG, fg=config.TEXT)
        self.count.pack(pady=(14, 0))

        tk.Label(self, text="drink today", font=(FONT, 11),
                 bg=config.BG, fg=config.DIM).pack()

        self.next.pack(pady=(14,0))

        make_buttons(self,"I Drank", app.record_drink).pack(pady=(22, 0))
        make_buttons(self, "Undo", app.undo_drink, primary=False).pack(pady=(8, 0))


        if autostart.is_supported():
            self.startup = tk.BooleanVar(value=autostart.is_enabled())
            tk.Checkbutton(
                self, text="Launch on Startup", variable=self.startup,
                command=self.toggle_startup, font=(FONT, 10),
                bg=config.BG, fg=config.DIM, selectcolor=config.BG,
                activebackground=config.BG, activeforeground=config.DIM,
            ).pack(pady=(18,0))


    def toggle_startup(self):
        if self.startup.get():
            autostart.enable()
        else:
            autostart.disable()

    def refresh(self):
        n = self.app.stats.count()
        self.count.config(text=f"{n} / {config.GOAL}")
        self.glass.set_level(n / config.GOAL)

    def set_next(self, text):
        self.next.config(text=text)


    def on_show(self):
        self.refresh()

class HistoryPage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=config.BG)
        self.app = app
        self.body = None


    def on_show(self):
        if self.body is not None:
            self.body.destroy()
        self.body = tk.Frame(self, bg=config.BG)
        self.body.pack(fill="both", expand=True)
        history = self.app.stats.history()


        tk.label(self.body, text="Last 7 days", font=(FONT, 12, "bold"),
                 bg=config.BG, fg=config.WATER
                 ).pack(anchor="w", padx=24, pady=(20, 6))

        WeekChart(self.body, history).pack(anchor="w" , padx=24 , pady=(0,8))

        frame= tk.Frame(self.body, bg=config.BG)
        frame.pack(fill="both", expand=True, padx=(23, 12), pady=(0, 16))

        bar = tk.Scrollbar(frame)
        bar.pack(side="right", fill="y")

        text = tk.Text(frame, wrap="none", bg=config.BG, fg=config.DIM,
                       font=("Consolas", 10), relief="flat", bd=0,
                       highlightthickness=0, cursor="arrow", spacing1=4,
                       yscrollcommand=bar.set)

        text.pack(side="left", fill="both", expand=True)
        bar.config(command=text.yview)


        if not history:
            text.insert("end", "No drinks logget yet bruh")

        for day, n in reversed(history.items()):
            label = date.fromisoformat(day).srftime("%a %d %b %Y")
            bars = "█" * min(n, config.GOAL)
            mark = "  ✓" if n >= config.GOAL else ""
            text.insert("end", f"{label} {bars:<{config.GOAL}} {n}/{config.GOAL}{mark}\n")

        text.config(state="disabled")


class InfoPage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=config.BG)

        tk.Label(self, text=info.TITLE, font=(FONT, 16, "bold"),
                 bg=config.BG, fg=config.TEXT
                 ).pack(anchor="w", padx=24, pady=(20, 8))

        frame = tk.Frame(self, bg=config.BG)
        frame.pack(fill="both", expand=True, padx=(24, 12), pady=(0, 16))


        bar = tk.Scrollbar(frame)
        bar.pack(side="right", fill="y")

        text = tk.Text(frame, wrap="word", bg=config.BG, fg=config.DIM,
                       font=(FONT, 10), relief="flat", bd=0,
                       highlightthickness=0, cursor="arrow", spacing2=3,
                       yscrollcommand=bar.set)

        text.pack(side="left", fill="both", expand=True)
        bar.config(command=text.yview)

        text.tag_configure("heading", font=(FONT, 12, "bold"),
                           foreground=config.WATER, spacing1=14, spacings3=4)
        text.tag_configure("body", spacing3=6)

        for heading, body in info.SECTIONS:
            text.insert("end", heading + "\n" , "heading")
            text.insert("end", body + "\n","body")


        text.config(state="disabled")


    def on_show(self):
         pass


class SettingsPage(tk.Frame):

    FIELDS = (
        ("Daily goal (drinks)", "GOAL", 1 ,30),
        ("Remind me every (minutes)", "DEFAULT_MINUTES", 1, 240),
        ("Snooze for (minutes)", "SNOOZE_MINUTES", 1, 60),
    )

    def __init__(self, parent, app):
        super().__init__(parent, bg=config.BG)
        self.app = app

        self.spins = {}
        for label, key, low, high in self.FIELDS:
            row = tk.Frame(self, bg=config.BG)
            row.pack(fill="x", padx=24, pady=(14, 0))
            tk.Label(row, text=label, font=(FONT, 11),
                     bg=config.BG, fg=config.DIM).pack(side="left")
            spin = tk.Spinbox(row, from_=low, to=high, width=5, font=(FONT, 11),
                              bg=config.BUTTON, fg="white",
                              buttonbackground=config.BUTTON,
                              relief="flat", justify="center")

            spin.bind("<Return>", lambda e: self.save())
            spin.pack(side="right")
            self.spins[key] = (label, spin, low, high)

        tk.Label(self, text="Saving restarts the reminder timer",
                 font=(FONT, 9), bg=config.BG, fg=config.DIM
                 ).pack(anchor="w", padx=24, pady=(14,0))

        self.note = tk.Label(self, font=(FONT, 10), bg=config.BG, fg=config.TEXT)
        self.note.pack(pady=(10,0))

        make_buttons(self, "Save", self.save).pack(pady=(10, 0))

    def on_show(self):
        self.note.config(text="")
        for key, (label, spin, low, high) in self.spins.items():
            spin.delete(0, "end")
            spin.insert(0, min(max(int(getattr(config,key)), low), high))

    def save(self):
        values = {}
        for key, (label, spin, low, high) in self.spins.items():
            try:
                value = int(spin.get())
            except ValueError:
                value = None
            if value is None or not low <= value <= high:
                self.note.config(text=f"{label}: use {low} to {high}.")
                return
            values[key] = value

        self.app.apply_settings(values)
        self.note.config(text="Saved")