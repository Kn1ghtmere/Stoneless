import time
import tkinter as tk
from datetime import date

from config import BG, BUTTON, BUTTON_ACTIVE, DEFAULT_MINUTES, DIM, GOAL, TEXT, WATER
from lock.manager import LockManager
from stats import load_stats, save_stats


def make_button(parent, text, command, **kwargs):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=BUTTON,
        fg=TEXT,
        activebackground=BUTTON_ACTIVE,
        activeforeground=TEXT,
        relief="flat",
        bd=0,
        cursor="hand2",
        **kwargs,
    )


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Water Lock")
        self.root.geometry("320x290")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.data = load_stats()
        self.interval = tk.StringVar(value=str(self.data.get("interval", DEFAULT_MINUTES)))
        self.running = False
        self.next_at = 0.0
        self.locker = LockManager(self.root, lambda: self.data["glasses"], self.on_drink, self.on_skip)

        tk.Label(self.root, text="water lock", font=("TkDefaultFont", 20, "bold"), bg=BG, fg=TEXT).pack(
            pady=(18, 4)
        )
        self.glasses = tk.Label(self.root, bg=BG, fg=WATER, font=("TkDefaultFont", 12))
        self.glasses.pack()
        self.status = tk.Label(self.root, text="paused", bg=BG, fg=DIM)
        self.status.pack(pady=6)

        row = tk.Frame(self.root, bg=BG)
        row.pack(pady=8)
        tk.Label(row, text="remind me every", bg=BG, fg=TEXT).pack(side="left")
        tk.Spinbox(row, from_=1, to=180, width=4, textvariable=self.interval).pack(side="left", padx=6)
        tk.Label(row, text="min", bg=BG, fg=TEXT).pack(side="left")

        self.toggle_btn = make_button(self.root, "start", self.toggle, width=16, pady=4)
        self.toggle_btn.pack(pady=4)
        make_button(self.root, "lock now (test)", self.locker.lock, width=16, pady=4).pack(pady=2)

        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.refresh()
        self.tick()

    def minutes(self):
        try:
            value = int(self.interval.get())
        except (tk.TclError, ValueError):
            value = DEFAULT_MINUTES
        return max(1, min(value, 180))

    def refresh(self):
        self.glasses.config(text="glasses today: %d / %d" % (self.data["glasses"], GOAL))

    def schedule(self):
        self.next_at = time.time() + self.minutes() * 60
        self.data["interval"] = self.minutes()
        save_stats(self.data)

    def toggle(self):
        self.running = not self.running
        if self.running:
            self.schedule()
            self.toggle_btn.config(text="pause")
        else:
            self.toggle_btn.config(text="start")

    def check_day(self):
        today = str(date.today())
        if self.data.get("date") != today:
            self.data = {"date": today, "glasses": 0, "interval": self.minutes()}
            save_stats(self.data)
            self.refresh()

    def tick(self):
        self.check_day()
        if self.locker.is_locked:
            self.status.config(text="locked until you drink water")
        elif self.running:
            left = int(self.next_at - time.time())
            if left <= 0:
                self.locker.lock()
            else:
                self.status.config(text="next water break in %d:%02d" % (left // 60, left % 60))
        else:
            self.status.config(text="paused")
        self.root.after(1000, self.tick)

    def on_drink(self):
        self.data["glasses"] += 1
        save_stats(self.data)
        self.refresh()
        if self.running:
            self.schedule()

    def on_skip(self, reason):
        if self.running:
            self.schedule()

    def quit(self):
        self.locker.unlock()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
