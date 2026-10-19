import tkinter as tk

from stats import Stats

import config

import autostart

import info

import themes

import settings

import queue

from tray import Tray

from reminder import Reminder

from datetime import date, timedelta

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


    

class Popup(tk.Toplevel):
     def __init__(self, app):
          super().__init__(app.root)
          self.job = None
          self.overrideredirect(True)
          self.attributes("-topmost", True)
          self.attributes("-alpha", 0.0)
          self.configure(bg=config.BG, highlightthickness=2,
                         highlightbackground=config.BUTTON)
          center(self, 340, 200)

          tk.Label(self, text="Time for WATAAHHH", font=(FONT, 18, "bold"),
                   bg=config.BG, fg=config.TEXT).pack(pady=(30,4))
          tk.Label(self, text=f"{app.stats.count()} of {config.GOAL} so far today",
                   font=(FONT, 11), bg=config.BG, fg=config.DIM).pack()

          row = tk.Frame(self, bg=config.BG)
          row.pack(pady=26)
          make_buttons(row, "yeah did bro", app.record_drink).pack(side="left", padx=6)
          make_buttons(row, f"Not yet ({config.SNOOZE_MINUTES} min)", app.snooze,
                       primary=False).pack(side="left", padx=6)

          self.bind("<Escape>", lambda e: app.snooze())
          self.lift()
          self.focus_force()
          self.fade(0.0)


     def fade(self, alpha):
          alpha = min(1.0, alpha + 0.12)
          self.attributes("-alpha", alpha)
          if alpha < 1.0:
               self.job = self.after(16, self.fade, alpha)

     def destroy(self):
          if self.job is not None:
               self.after_cancel(self.job)
          super().destroy()



class InfoWindow(tk.Toplevel):

     def __init__(self, parent):
          super().__init__(parent)
          self.title("important info")
          self.configure(bg=config.BG)
          center_on(self, parent, 420, 560)
          self.bind("<Escape>", lambda e: self.destroy())
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



class HistoryWindow(tk.Toplevel):

     def __init__(self, parent, history):
          super().__init__(parent)
          self.title("History")
          self.configure(bg=config.BG)
          center_on(self, parent, 400, 540)
          self.bind("<Escape>", lambda e: self.destroy())
          self.minsize(340,240)

          tk.Label(self, text="History", font=(FONT, 18, "bold"),
                   bg=config.BG, fg=config.TEXT
                   ).pack(anchor="w", padx=24, pady=(20, 8))

          WeekChart(self, history).pack(anchor="w", padx=24, pady=(0, 8))

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

     FIELDS = (
          ("Daily goal (drinks)", "GOAL", 1, 30),
          ("Remind every (minutes)", "DEFAULT_MINUTES", 1, 240),
          ("Snooze for (minutes)", "SNOOZE_MINUTES", 1, 60),
     )


     def __init__(self, app):
          super().__init__(app.root)
          self.app = app
          self.title("Settings")
          self.configure(bg=config.BG)
          center_on(self, app.root, 360, 330)
          self.bind("<Escape>", lambda e: self.destroy())
          self.bind("<Return>",lambda e: self.save())
          self.resizable(False, False)


          tk.Label(self, text ="Settings" , font=(FONT, 18, "bold"),
                   bg=config.BG, fg=config.TEXT
                   ).pack(anchor="w", padx=24, pady=(20, 10))

          self.spins = {}
          for label, key, low, high in self.FIELDS:
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

          tk.Label(self, text="Saving restarts the reminder timer.",
                   font=(FONT, 9), bg=config.BG, fg=config.DIM
                   ).pack(anchor="w", padx=24, pady=(10, 0))
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
          themes.apply(config.THEME)
          self.stats = Stats()
          self.reminder = Reminder(config.DEFAULT_MINUTES * 60,
                                   config.SNOOZE_MINUTES * 60)

          self.popup = None
          self.info = None
          self.history_win = None
          self.settings_win = None
          self.pending = queue.SimpleQueue()
          self.day = date.today()

          self.root = tk.Tk()
          self.root.title("Stoneless")
          self.root.configure(bg=config.BG)
          center(self.root, 340, 560)
          self.root.resizable(False, False)
          self.root.protocol("WM_DELETE_WINDOW", self.hide)
          self.tray = Tray(lambda: self.pending.put("open"),
                           lambda: self.pending.put("quit"))
          self.tray.start()


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

          make_buttons(self.root, "I Drank", self.record_drink).pack(pady=(22, 0))

          row = tk.Frame(self.root, bg=config.BG)
          row.pack(pady=(14, 0))
          for text, command in (("Undo", self.undo_drink),
                                ("History", self.show_history),
                                ("Info", self.show_info),
                                ("Settings", self.show_settings)):
               small = make_buttons(row, text, command, primary=False)
               small.config(font=(FONT, 10), padx=10, pady=4)
               small.pack(side="left", padx=2)

          
          if autostart.is_supported():
               self.startup = tk.BooleanVar(value=autostart.is_enabled())
               tk.Checkbutton(
                    self.root, text="Launch on Startup", variable=self.startup,
                    command=self.toggle_startup, font=(FONT, 10),
                    bg=config.BG, fg=config.DIM , selectcolor=config.BG,
                    activebackground=config.BG, activeforeground=config.DIM,
               ).pack(pady=(18,0))

          if minimized:
               self.root.withdraw()

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


     def hide(self):
          self.root.withdraw()

     def show(self):
          self.root.deiconify()
          self.root.lift()
          self.root.focus_force()

     def quit(self):
          self.tray.stop()
          self.root.destroy()

     def tick(self):
          while not self.pending.empty():
               action = self.pending.get()
               if action == "open":
                    self.show()
               elif action == "quit":
                    self.quit()
                    return
               
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


    