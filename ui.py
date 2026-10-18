import tkinter as tk

from stats import Stats

import config

import autostart

import info

import settings

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



class InfoWindow(tk.Toplevel):

     def __init__(self, parent):
          super().__init__(parent)
          self.title("important info")
          self.configure(bg=config.BG)
          self.geometry("420x560")
          self.minsize(360, 300)

          tk.Label(self, text=info.TITLE, font=(FONT, 18, "bold"),
                   bg=config.BG, fg=config.TEXT
                   ).pack(anchor="w", padx=24, pady=(20,8))

          frame = tk.Frame(self, bg=config.BG)
          frame.pack(fill="both", expand=True, padx=(24, 12), pady=(0,16))

          bar = tk.Scrollbar(frame)
          bar.pack(side="right", fill="y")

          text = tk.Text(frame, wrap="word", bg=config.BG, fg=config.DIM,
                         font=(FONT,10), relief="flat", bd=0,
                         highlightthickness=0, cursor="arrow", spacing2=3,
                         yscrollcommand=bar.set)
          text.pack(side="left", fill="both", expand=True)
          bar.config(command=text.yview)

          text.tag_configure("heading", font=(FONT, 12, "bold"),
                             foreground=config.WATER, spacing1=14, spacing3=4)
          text.tag_configure("body", spacing3=6)

          for heading, body in info.SECTIONS:
               text.insert("end", heading + "\n", "heading")
               text.insert("end", body + "\n", "body")

          text.config(state="disabled")





class HistoryWindow(tk.Toplevel):

     def __init__(self, parent, history):
          super().__init__(parent)
          self.title("History")
          self.configure(bg=config.BG)
          self.geometry("400x420")
          self.minsize(340,240)

          tk.Label(self, text="History", font=(FONT, 18, "bold"),
                   bg=config.BG, fg=config.TEXT
                   ).pack(anchor="w", padx=24, pady=(20, 8))

          frame = tk.Frame(self, bg=config.BG)
          frame.pack(fill="both", expand=True, padx=(24, 12), pady=(0,16))

          bar = tk.Scrollbar(frame)
          bar.pack(side="right", fill="y")

          text = tk.Text(frame, wrap="none", bg=config.BG, fg=config.DIM,
                         font=("Consolas", 10), relief="flat", bd=0,
                         highlightthickness=0, cursor="arrow", spacing1=4,
                         yscrollcommand=bar.set)
          text.pack(side="left", fill="both" , expand=True)
          bar.config(command=text.yview)


          if not history:
               text.insert("end", "No drinks logged yet bruh")

          for day, n in reversed(history.items()):
               label = date.fromisoformat(day).strftime("%a %d %b %Y")
               bars = "█" * min(n, config.GOAL)
               mark = "  ✓" if n >= config.GOAL else ""
               text.insert("end", f"{label} {bars:<{config.GOAL}} {n}/{config.GOAL}{mark}\n")

          text.config(state="disabled")


class SettingsWindow(tk.Toplevel):

     FEILDS = (
          ("Daily goal (drinks)", "GOAL", 1, 30),
          ("Remind every (minutes)", "DEFAULT_MINUTES", 1, 240),
          ("Snooze for (minutes)", "SNOOZE_MINUTES", 1, 60),
     )


     def __init__(self, app):
          super().__init__(app.root)
          self.app = app
          self.title("Settings")
          self.configure(bg=config.BG)
          self.geometry("360x300")
          self.resizable(False, False)


          tk.Label(self, text ="settings" , font=(FONT, 18, "bold"),
                   bg=config.BG, fg=config.TEXT
                   ).pack(anchor="w", padx=24, pady=(20, 10))

          self.spins = {}
          for label, key, low, high in self.FEILDS:
               row = tk.Frame(self, bg=config.BG)
               row.pack(fill="x", padx=24, pady=6)
               tk.Label(row, text=label, font=(FONT, 11),
                        bg=config.BG, fg=config.DIM).pack(side="left")
               spin = tk.Spinbox(row, from_=low, to=high, width=5, font=(FONT, 11),
                                 bg=config.BUTTON, fg="white",
                                 buttonbackground=config.BUTTON,
                                 relief="flat", justify="center")

               spin.delete(0, "end")
               spin.insert(0, min(max(int(getattr(config, key)), low), high))
               spin.pack(side="right")
               self.spins[key] = (label, spin, low, high)


          self.note = tk.Label(self, font=(FONT, 10), bg=config.BG, fg=config.TEXT)
          self.note.pack(pady=(10, 0))

          make_buttons(self, "Save", self.save).pack(pady=(10, 0))

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
          self.destroy()












class App:
     def __init__(self, minimized=False):
          settings.load()
          self.stats = Stats()
          self.reminder = Reminder(config.DEFAULT_MINUTES * 60,
                                   config.SNOOZE_MINUTES * 60)

          self.popup = None
          self.info = None
          self.history_win = None
          self.settings_win = None
          self.day = date.today()

          self.root = tk.Tk()
          self.root.title("Stoneless")
          self.root.configure(bg=config.BG)
          self.root.geometry("340x660")
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

          self.next = tk.Label(self.root, font=(FONT, 11),
                               bg=config.BG, fg=config.DIM)
          self.next.pack(pady=(14, 0))

          make_buttons(self.root, "I Drank", self.record_drink).pack(pady=(24, 0))
          make_buttons(self.root, "Undo", self.undo_drink, primary=False).pack(pady=(8, 0))

          row = tk.Frame(self.root, bg=config.BG)
          row.pack(pady=(8, 0))
          make_buttons(row, "info", self.show_info, primary=False).pack(side="left")
          make_buttons(row, "History", self.show_history, primary=False).pack(side="left")
          make_buttons(self.root, "Settings", self.show_settings, primary=False).pack(pady=(8, 0))

          
          if autostart.is_supported():
               self.startup = tk.BooleanVar(value=autostart.is_enabled())
               tk.Checkbutton(
                    self.root, text="Launch on Startup", variable=self.startup,
                    command=self.toggle_startup, font=(FONT, 10),
                    bg=config.BG, fg=config.DIM , selectcolor=config.BG,
                    activebackground=config.BG, activeforeground=config.DIM,
               ).pack(pady=(18,0))

          if minimized:
               self.root.iconify()

          self.refresh()
          self.tick()


     def record_drink(self):
          self.stats.add_drink()
          self.reminder.reset()
          self.close_popup()
          self.refresh()


     def undo_drink(self):
          self.stats.undo_drink()
          self.refresh()

     def snooze(self):
          self.reminder.snooze()
          self.close_popup()

     def show_popup(self):
          if self.popup is None:
               self.popup = Popup(self)

     def close_popup(self):
          if self.popup is not None:
               self.popup.destroy()
               self.popup = None


     def toggle_startup(self):
          if self.startup.get():
               autostart.enable()
          else:
               autostart.disable()


     def show_info(self):
          if self.info is None or not self.info.winfo_exists():
               self.info = InfoWindow(self.root)
          else:
               self.info.lift()

     def show_history(self):
          if self.history_win is not None and self.history_win.winfo_exists():
               self.history_win.destroy()
          self.history_win = HistoryWindow(self.root, self.stats.history())


     def show_settings(self):
          if self.settings_win is None or not self.settings_win.winfo_exists():
               self.settings_win = SettingsWindow(self)
          else:
               self.settings_win.lift()

     def apply_settings(self, values):
          settings.update(values)
          self.reminder.interval = config.DEFAULT_MINUTES * 60
          self.reminder.snooze_for = config.SNOOZE_MINUTES * 60
          self.reminder.reset()
          self.refresh()


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


    