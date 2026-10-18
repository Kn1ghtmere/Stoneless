import random
import tkinter as tk

from config import BG, DIM, EMERGENCY_CODE_LENGTH, EMERGENCY_DELAY_SECONDS

ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"


def make_code(length=EMERGENCY_CODE_LENGTH, rng=None):
    rng = rng or random.SystemRandom()
    return "".join(rng.choice(ALPHABET) for _ in range(length))


def code_matches(typed, code):
    return typed.strip() == code


class EmergencyPanel(tk.Frame):
    def __init__(self, parent, on_success, delay=EMERGENCY_DELAY_SECONDS):
        super().__init__(parent, bg=BG)
        self.on_success = on_success
        self.delay = delay
        self.left = 0
        self.code = ""
        self.job = None

        self.link = tk.Label(self, text="emergency exit", bg=BG, fg=DIM, cursor="hand2")
        self.link.bind("<Button-1>", lambda e: self.begin())

        self.message = tk.Label(self, bg=BG, fg=DIM)
        self.row = tk.Frame(self, bg=BG)
        self.entry = tk.Entry(self.row, width=12, justify="center", font=("TkFixedFont", 14))
        self.entry.pack()
        self.entry.bind("<Return>", lambda e: self.submit())
        self.status = tk.Label(self, bg=BG, fg="#ff7b72")

        self.reset()

    def reset(self):
        self.cancel()
        self.message.pack_forget()
        self.row.pack_forget()
        self.status.pack_forget()
        self.entry.delete(0, "end")
        self.link.pack()

    def cancel(self):
        if self.job is not None:
            self.after_cancel(self.job)
            self.job = None

    def begin(self):
        self.link.pack_forget()
        self.code = make_code()
        self.left = self.delay
        self.message.pack()
        self.countdown()

    def countdown(self):
        if self.left <= 0:
            self.job = None
            self.message.config(text="type this code to skip the break:  %s" % self.code)
            self.row.pack(pady=4)
            self.entry.focus_set()
            return
        self.message.config(text="emergency exit opens in %d s. only use it if you really need your computer." % self.left)
        self.left -= 1
        self.job = self.after(1000, self.countdown)

    def submit(self):
        if code_matches(self.entry.get(), self.code):
            self.cancel()
            self.on_success()
            return
        self.reset()
        self.status.config(text="wrong code, start again")
        self.status.pack()

    def destroy(self):
        self.cancel()
        super().destroy()
