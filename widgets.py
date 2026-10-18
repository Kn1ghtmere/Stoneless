import tkinter as tk
from tkinter import ttk

from config import BG, BUTTON, BUTTON_ACTIVE, DIM, PANEL, TEXT, WATER

FONT = "TkDefaultFont"

def label(parent, text="", size= 11, bold=False, dim=False, **kw):
    kw.setdefault("bg" , BG)
    return tk.Label(
        parent, text = text, fg=DIM if dim else TEXT,
        font = (FONT, size, "bold" if bold else "normal"), **kw    )


def button(parent, text, command, **kw):
    return tk.Button(
        parent, text= text, command= command,  bg = BUTTON, fg= TEXT,
        activebackground=BUTTON_ACTIVE, activeforeground=TEXT,
        disabledforeground=DIM, relief="flat",bd=0, padx=14, pady=8,
        font=(FONT,11), cursor="hand2",  **kw

    )

def entry(parent, width=30, show="", textvariable=None):
    return tk.Entry(
        parent, width=width, show=show, textvariable=textvariable, bg=PANEL, fg=TEXT,
        insertbackground=TEXT, relief="flat", font=(FONT, 11),
        highlightthickness= 1, highlightbackground=BUTTON, highlightcolor=WATER,

    )


def apply_theme(root):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("Treeview", background=PANEL, fieldbackground= PANEL, foreground=TEXT,
                    rowheight=28, borderwidth=0)
    style.configure("Treeview.Heading", background = BUTTON, foreground = TEXT, relief = "flat")
    style.map("Treeview", background=[("selected", BUTTON_ACTIVE)])
    style.configure("TNotebook", background=BG, borderwidth=0 )
    style.configure("TNotebook.Tab", background=PANEL, foreground=TEXT, padding=(14, 6))
    style.map("TNotebook.Tab",  background=[("selected", BUTTON)])
    style.configure("TFrame",background=BG)
    style.configure("TCombobox", fieldbackground=PANEL, Background=BUTTON, foreground= TEXT)



class GlassRow(tk.Canvas):

    def __init__(self, parent, filled, total, size=26, bg=BG):
        self.total, self.size = total, size

        super().__init__(parent, width=total * (size + 10) + 6, height=size + 12,
                         bg=bg, highlightthickness=0)
        self.set(filled)

    def set(self,filled):
        self.delete("all")
        s = self.size
        for i in range(self.total):
            x = 5 + i * (s + 10)
            full = i < filled
            self.create_polygon(
                x, 6, x + s, 6, x+s-4, 6+s, x+4, 6+s,
                fill = WATER if full else PANEL, outline=DIM, width =1,
            )