import queue
import threading
import tkinter as tk
from typing import Callable, Any

import settings
import sync
from config import BG, PANEL, TEXT
from widgets import button, entry, label


class Async:
    def __init__(self, root: tk.Misc):
        self.root = root
        self.q = queue.Queue()
        self._poll()

    def run(self, fn: Callable[[], Any], ok: Callable[[Any], None], err: Callable[[Exception], None]) -> None:
        def work():
            try:
                result = fn()
            except Exception as exc:
                self.q.put((err, exc))
            else:
                self.q.put((ok, result))
        threading.Thread(target=work, daemon=True).start()

    def _poll(self) -> None:
        try: 
            while True:
                callback, value = self.q.get_nowait()
                try:
                    callback(value)
                except tk.TclError:
                    pass
        except queue.Empty:
            pass 
        
        self.root.after(100, self._poll)


class AccountDialog(tk.Toplevel):
    # FIX: Added missing double underscores
    def __init__(self, app: Any):
        super().__init__(app.root)
        self.app = app
        self.title("Account")
        self.configure(bg=BG, padx=26, pady=20)
        self.geometry("400x520")
        self.transient(app.root)
        self.mode = "login"
        self.v_server = tk.StringVar(value=settings.load()["server_url"])
        self.v_email = tk.StringVar()
        self.v_pass = tk.StringVar()
        self.v_user = tk.StringVar()
        self.v_goal = tk.StringVar()
        self.v_color = tk.StringVar()
        self.status = None
        self.render()

    def set_status(self, text: str, ok: bool = False) -> None:
        if self.status and self.status.winfo_exists():
            self.status.config(text=text, fg=TEXT if ok else '#ff8a80')

    def on_err(self, exc: Exception) -> None:
        self.set_status(sync.explain(exc))

    def field(self, caption: str, var: tk.StringVar, show: str = "") -> tk.Entry:
        label(self, caption, size=10, dim=True).pack(anchor="w", pady=(10, 2))
        box = entry(self, width=36, show=show, textvariable=var)
        box.pack(fill="x", ipady=4)
        return box

    def render(self) -> None:
        for w in self.winfo_children():
            w.destroy()
        self.status = label(self, "", size=10, wraplength=340, justify="left")
        if sync.is_logged_in():
            self.render_profile()
        else:
            self.render_auth()

    def render_auth(self) -> None:
        register = self.mode == "register"
        label(self, "Create account" if register else "Log in", size=18, bold=True).pack(anchor="w")
        self.field("Server URL", self.v_server)
        self.field("Email", self.v_email)

        if register:
            self.field("Username(3-20 letters, numbers, _)", self.v_user)
        self.field("Password(8+ characters)", self.v_pass, show="*")
        
        button(self, "Create account" if register else "Log in", self.submit).pack(fill="x", pady=(15, 5))
        button(self, "I need an account" if not register else "I already have an account", self.toggle).pack(fill="x")
        
        self.status.pack(anchor="w", pady=10)

    def toggle(self) -> None:
        self.mode = "login" if self.mode == "register" else "register"
        self.render()

    def submit(self) -> None:
        settings.update(server_url=self.v_server.get().strip().rstrip("/"))
        email = self.v_email.get().strip()
        password = self.v_pass.get()
        username = self.v_user.get().strip()
        
        if not email or not password or (self.mode == "register" and not username):
            return self.set_status("Fill in every field")
        
        self.set_status("Working...", ok=True)
        if self.mode == "register":
            work = lambda: sync.register(email, password, username)
        else:
            work = lambda: sync.login(email, password)
        self.app.async_.run(work, self.after_auth, self.on_err)

    def after_auth(self, _: Any) -> None:
        self.app.refresh_account()
        sync.sync_in_background()
        self.render()

    def render_profile(self) -> None:
        label(self, "Your Profile", size=18, bold=True).pack(anchor="w")
        self.who = label(self, "loadinggggggg......", size=11, dim=True)
        self.who.pack(anchor="w", pady=(4, 0))
        
        self.field("Username", self.v_user) 
        self.field("Daily goal(ml)", self.v_goal)
        self.field("Avatar color (#rrggbb)", self.v_color)
        
        self.swatch = tk.Frame(self, height=8, bg=PANEL)
        self.swatch.pack(fill="x", pady=(6, 0))
        button(self, "Save", self.save).pack(fill="x", pady=(10, 0))
        self.status.pack(anchor="w", pady=10)
        self.app.async_.run(sync.me, self.fill_profile, self.on_err)

    def fill_profile(self, data: dict) -> None:
        self.who.config(text=data["email"])
        self.v_user.set(data["username"])
        self.v_goal.set(str(data["daily_goal_ml"]))
        self.v_color.set(data["avatar_color"])
        self.swatch.config(bg=data["avatar_color"])

    def save(self) -> None:
        try:
            goal = int(self.v_goal.get())
        except ValueError:
            return self.set_status("Goal must be a number")
            
        fields = {
            "username": self.v_user.get().strip(), 
            "daily_goal_ml": goal, 
            "avatar_color": self.v_color.get().strip()
        }

        def done(data: dict) -> None:
            self.fill_profile(data)
            self.app.refresh_account()
            self.set_status("Saved", ok=True)

        self.set_status("Saving....", ok=True)
        self.app.async_.run(lambda: sync.update_me(**fields), done, self.on_err)

    def logout(self) -> None:
        sync.logout()
        self.app.refresh_account()
        self.render()