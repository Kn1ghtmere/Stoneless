import random

import tkinter as tk

from config import BG, DIM, EMERGENCY_CODE_LENGTH,EMERGENCY_DELAY_SECONDS, PANEL , TEXT
from widgets import FONT, button, entry



class EmergencyPanel(tk.Frame):
    def __init__(self, parent, on_emergency):
        super().__init__(parent, bg=BG)
        self.on_emergency = on_emergency
        self.code = None
        self.job = None
        self.left = 0
        self.btn = button( self, "Emergency exit" , self.begin)
        self.btn.config(bg=PANEL, font = (FONT, 9), padx=10, pady=4)
        self.btn.pack()
        self.info = tk.Label(self, text ="" ,bg =BG, fg=DIM, font = (FONT, 11))
        self.info.pack(pady=(6, 0))
        self.box = None


    def begin(self):
        self.btn.config(state = "disabled")
        self.left = EMERGENCY_DELAY_SECONDS
        self.countdown()

    def countdown(self) : 
        if self.left > 0 :
            self.info.config(text=f"Hold on...{self.left}s")
            self.left -=1
            self.job = self.after(1000,  self.countdown)
        else:
            self.show_code()


    def show_code(self):
        self.code = "".join(random.choice("0123456789") for _ in range(EMERGENCY_CODE_LENGTH))
        self.info.config(text=f"Type this code to leave: {self.code}", fg=TEXT)
        self.box = entry(self, width=12)
        self.box.pack(pady=6)
        self.box.focus_force()
        self.box.bind("<KeyRelease>", self.check)

    def check(self, _event=None):
        if self.box.get().strip() == self.code:
            self.on_emergency()

    def destroy(self):
        if self.job:
            try:
                self.after_cancel(self.job)
            except Exception:
                pass
        super().destroy()
