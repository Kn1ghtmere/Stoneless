import tkinter as tk
from datetime import date, timedelta

import config

FONT = "Segoe UI"

def center(win, w, h):
     x = (win.winfo_screenwidth() - w) // 2
     y = (win.winfo_screenheight() - h) // 2
     win.geometry(f"{w}x{h}+{x}+{y}")

def center_on(win, parent, w, h):
     parent.update_idletasks()
     x = parent.winfo_x() + (parent.winfo_width() - w) // 2
     y = parent.winfo_y() + (parent.winfo_height() - h) // 2
     win.geometry(f"{w}x{h}+{max(x, 0)}+{max(y, 0)}")


def fmt(seconds):
     s = int(seconds)
     h, rem = divmod(s, 3600)
     m, s = divmod(rem, 60)
     return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"



def make_buttons(parent, text, command, primary=True):
     normal = config.BUTTON if primary else config.BG
     active = config.BUTTON_ACTIVE if primary else config.SURFACE
     btn = tk.Button(
          parent,
          text=text,
          command=command,
          font=(FONT, 12, "bold" if primary else "normal"),
          bg=normal,
          fg="white" if primary else config.DIM,
          activebackground=active,
          activeforeground="white",
          relief="flat",
          bd=0,
          padx=22,
          pady=9,
          cursor="hand2"
     )
     btn.bind("<Enter>" , lambda e: btn.config(bg=active))
     btn.bind("<Leave>", lambda e: btn.config(bg=normal))
     return btn


class Glass(tk.Canvas):

    W, H, PAD, TAPER = 120, 200, 6, 14

    def __init__(self, parent):
         super().__init__(parent, width=self.W, height=self.H,
                          bg=config.BG, highlightthickness=0)

         self.level = 0.0
         self.target = 0.0
         self.job = None
         self.draw()

    def edges(self, y):
         p = self.PAD
         inset = self.TAPER * (y - p) / (self.H - 2 * p)
         return p + inset, self.W - p -inset

    def draw(self):
         self.delete("all")
         p = self.PAD
         bottom = self.H - p
         top = bottom - (self.H - 2 * p) * self.level

         if self.level > 0:
              lx, rx = self.edges(top)
              blx, brx = self.edges(bottom)
              self.create_polygon(lx, top, rx, top, brx, bottom, blx, bottom,
                                  fill=config.WATER, outline="")
              self.create_line(lx, top, rx, top, fill=config.SHINE, width=2)

         tl, tr = self.edges(p)
         bl, br = self.edges(bottom)
         self.create_polygon(tl, p, tr, p, br, bottom, bl, bottom,
                             fill="", outline=config.DIM, width=2)

    def set_level(self, fraction):
         self.target = max(0, min(1, fraction))
         if self.job is None:
              self.animate()

    def animate(self):
         diff = self.target - self.level
         if abs(diff) < 0.004:
              self.level = self.target
              self.draw()
              self.job = None
              return
         self.level += diff* 0.15
         self.draw()
         self.job = self.after(16, self.animate)







class WeekChart(tk.Canvas):

     W, H = 352, 160

     def __init__(self, parent, history):
          super().__init__(parent, width=self.W, height=self.H,
                           bg=config.BG, highlightthickness=0)

          today = date.today()
          days = [today - timedelta(days=i) for i in range(6, -1, -1)]
          counts = [history.get(d.isoformat(), 0) for d in days]

          peak = max(config.GOAL, max(counts))
          base = self.H - 26
          usable = base - 24
          slot = self.W / 7
          half = slot * 0.25

          goal_y = base - usable * config.GOAL / peak
          self.create_line(0, goal_y, self.W, goal_y,
                           fill=config.DIM, dash=(4, 4))
          self.create_text(self.W -2, goal_y - 8, text=f"goal {config.GOAL}",
                           anchor="e", fill=config.DIM, font=(FONT, 8))

          for i, (d, n) in enumerate(zip(days,counts)):
               cx = slot * i + slot / 2
               height = usable * n / peak
               color = config.TEXT if d == today else config.WATER
               if n:
                    self.create_rectangle(cx - half, base - height,
                                          cx + half, base,
                                          fill=color, outline="")
                    self.create_text(cx, base - height - 8, text=str(n),
                                     fill=config.DIM, font=(FONT, 9))
               self.create_text(cx, base + 12 , text=d.strftime("%a"),
                                fill=config.DIM, font=(FONT, 9))



class TabBar(tk.Frame):

     def __init__(self, parent, tabs, on_select):
          super().__init__(parent, bg=config.BG)
          self.on_select = on_select
          self.active = None
          self.items = {}
          for name in tabs:
               cell = tk.Frame(self, bg=config.BG)
               cell.pack(side="left", expand=True, fill="x")
               label = tk.Label(cell, text=name, font=(FONT, 11), bg=config.BG,
                                fg=config.DIM, cursor="hand2, pady=10")
               label.pack(fill="x")
               line = tk.Frame(cell, height=3, bg=config.BG)
               line.pack(fill="x")
               label.bind("<Button-1>", lambda e, n=name: self.on_select(n))
               label.blind("<Enter>", lambda e, n=name: self.paint(hover=n))
               label.bind("<Leave>", lambda e: self.paint())
               self.items[name] = (label, line)

     def select(self, name):
          self.active = name
          self.paint()

     def paint(self, hover=None):
          for name, (label, line) in self.items.items():
               on = name == self.active
               label.config(fg=config.TEXT if on or name == hover else config.DIM,
                            font=(FONT, 11, "bold" if on else "normal"))
               line.config(bg=config.WATER if on else config.BG)