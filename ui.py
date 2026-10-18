import tkinter as tk

from stats import Stats

import config

from reminder import Reminder

from datetime import date

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


class Popup(tk.Toplevel):
     def __init__(self, app):
          super().__init__(app.root)
          self.overrideredirect(True)
          self.attributes("-topmost", True)
          self.configure(bg=config.BG, highlightthickness=2,
                         highlightbackground=config.BUTTON)
          center(self, 340, 190)

          tk.Label(self, text="Time for WATAAAHHH", font=(FONT, 18, "bold"),
                   bg=config.BG, fg=config.DIM).pack()

          row = tk.Frame(self, bg=config.BG)
          row.pack(pady=26)
          make_buttons(row, "Yeah did bro", app.record_drink).pack(side="left", padx=6)
          make_buttons(row, "Not yet", app.snooze, primary=False).pack(side="left", padx=6)


          self.lift()
          self.focus_force()





class App:
     def __init__(self):
          self.stats = Stats()
          self.reminder = Reminder(config.DEFAULT_MINUTES * 60,
                                   config.SNOOZE_MINUTES * 60)

          self.popup = None
          self.day = date.today()

          self.root = tk.Tk()
          self.root.title("Stoneless")
          self.root.configure(bg=config.BG)
          self.root.geometry("340x520")
          self.root.resizable(False, False)


          tk.Label(self.root, text="Stoneless", font=(FONT, 20, "bold"),
                   bg=config.BG, fg=config.DIM).pack(pady=(26, 14))

          self.glass = Glass(self.root)
          self.glass.pack()

          self.count = tk.Label(self.root, font=(FONT, 40, "bold"),
                                bg=config.BG, fg=config.TEXT)

          self.count.pack(pady=(14, 0))

          tk.Label(self.root, text="drinks today", font=(FONT, 11),
                   bg=config.BG, fg=config.DIM).pack()

          make_buttons(self.root, "I Drank", self.record_drink).pack(pady=(24, 0))

          self.refresh()


     def record_drink(self):
          self.stats.add_drink()
          self.reminder.reset()
          self.close_popup()
          self.refresh()


     def snooze(self):
          self.reminder.snooze()
          self.close_popup()

     def show_popup(self):
          if self.popup is None:
               self.close_popup = Popup(self)

     def close_popup(self):
          if self.popup is not None:
               self.popup.destroy()
               self.popup = None

    
     def refresh(self):
          n = self.stats.count()
          self.count.config(text=f"{n} / {config.GOAL}")
          self.glass.set_level(n / config.GOAL)


     def goal_met(self):
          return self.stats.count() >= config.GOAL


     def tick(self):
          today = date.today()
          if today != self.day:
               self.day = today
               self.reminder.reset()
               self.close_popup()
               self.refresh()

          if self.goal_met():
               self.next.config(text="Goal Reached, Good job")
          else:
               self.next.config(text=f"Next reminder in {fmt(self.reminder.remaining())}")
               if self.reminder.is_due():
                    self.show_popup()
          self.root.after(1000, self.tick)

     def run (self):
          self.root.mainloop()


    