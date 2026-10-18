import tkinter as tk

import config

FONT = "Segoe UI"

def center(win, w, h):
     x = (win.winfo_screenwidth() - w) // 2
     y = (win.winfo_screenheight() - h) // 2
     win.geometry(f"{w}x{h}+{x}+{y}")



def fmt(seconds):
     s = int(seconds)
     h, rem = divmod(s, 3600)
     m, s = divmod(rem, 60)
     return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"



def make_buttons(parent, text, command, primary=True):
     return tk.Button(
          parent,
          text=text,
          command=command,
          font=(FONT, 12, "bold" if primary else "normal"),
          bg=config.BUTTON if primary else config.BG,
          fg="white" if primary else config.DIM,
          activebackground=config.BUTTON_ACTIVE,
          activeforeground="white",
          relief="flat",
          bd=0,
          padx=22,
          pady=9,
          cursor="hand2",
     )


class Glass(tk.Canvas):

     W, H ,PAD = 120, 200, 6

     def __init__(self,parent):
          super().__init__(parent, width=self.W, height=self.H,
                        bg=config.BG, highlightthickness=0)
          self.set_level(0)

     def set_level(self, fraction):
          fraction = max(0, min(1, fraction))
          self.delete("all")
          p = self.PAD
          top = self.H - p - (self.H - 2 * p) * fraction
          if fraction > 0:
               self.create_rectangle(p, top, self.W - p, self.H - p,
                                     fill=config.WATER, outline="")
               self.create_rectangle(p, p, self.W - p, self.H - p,
                                       outline=config.DIM, width=2)

class App:
     def __init__(self):

          self.root = tk.Tk()
          self.root.title("Stoneless")
          self.root.configure(bg=config.BG)
          self.root.geometry("340x520")
          self.root.resizable(False, False)

    def run(self):
     self.root.mainloop()