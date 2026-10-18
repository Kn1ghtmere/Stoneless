import os
import threading
import requests
import settings
import stats
from paths import data_dir

SERVICE = "stoneless"
TOKEN_FILE = os.path.join(data_dir(), "token")

def server_url() -> str:
    return settings.load()["server_url"].rstrip("/")

def _save_token(token: str):
    try: 
        import keyring
        keyring.set_password(SERVICE, "token", token)
        return
    except Exception:
        pass
    with open(TOKEN_FILE, "w") as f:
        f.write(token)
    try:
        os.chmod(TOKEN_FILE, 0o600)
    except OSError:
        pass

def _load_token():
    try:
        import keyring
        token = keyring.get_password(SERVICE, "token")
        if token:
            return token
    except Exception:
        pass
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            token = f.read().strip()
            return token or None
    return None

def logout():
    try:
        import keyring
        keyring.delete_password(SERVICE, "token")
    except Exception:
        pass
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)

def is_logged_in() -> bool:
    return _load_token() is not None

def _request(method, path, auth=True, **kw):
    headers = {}
    if auth:
        token = _load_token()
        if not token:
            raise RuntimeError("Not logged in")
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.request(method, server_url() + path, headers=headers, timeout=10, **kw)
    if resp.status_code == 401 and auth:
        logout()  
    resp.raise_for_status()
    return resp.json()

def explain(exc) -> str:
    """turning aaaa exception intooo a human understandable sentence so weird errors can be understood ig"""
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        try: 
            detail = exc.response.json().get("detail")
        except Exception:
            detail = None
        if isinstance(detail, list) and detail:
            detail = detail[0].get("msg", "Invalid input")
        return str(detail or f"Server error {exc.response.status_code}")
    if isinstance(exc, requests.Timeout):
        return "Server timed out"
    if isinstance(exc, requests.ConnectionError):
        return f"CANT REACH THE SERVER AT {server_url()}" 
    return str(exc)

def register(email, password, username):
    data = _request("POST", "/auth/register", auth=False,
                    json={"email": email, "password": password, "username": username})
    _save_token(data["access_token"])

def login(email, password):
    data = _request("POST", "/auth/login", auth=False,
                    data={"username": email, "password": password})
    _save_token(data["access_token"])

def me():
    return _request("GET", "/me")

def update_me(**fields):
    return _request("PATCH", "/me", json=fields)

def sync() -> int:
    """Push unsynced drinks so it returns howw many were sent (0 if nothing or idk maybe loggedout or no data to send or idkdkdkd)"""
    rows = stats.unsynced()
    if not rows or not is_logged_in():
        return 0
    payload = [{"client_id": r["id"], "amount_ml": r["amount_ml"], "logged_at": r["logged_at"]}
               for r in rows]
    try:
        _request("POST", "/drinks", json=payload)
    except (requests.RequestException, RuntimeError):
        return 0
    stats.mark_synced([r["id"] for r in rows])
    return len(rows)

def sync_in_background():
    threading.Thread(target=sync, daemon=True).start()