import datetime as dt
import os
import sqlite3

import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from pydantic import BaseModel, EmailStr, Field

from db import get_db, init_db



SECRET = os.environ.get("STONELESS_SECRET", "HAVETOCHANGEEE")
TOKEN_DAYS=30
USERNAME_RE = r"^[a-zA-Z0-9_]+$"


hasher = PasswordHash.recommended()
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")
app = FastAPI(title="Stoneless")
init_db()



def make_token(user_id: int) -> str:
    exp = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=TOKEN_DAYS)
    return jwt.encode({"sub" : str(user_id), "exp" : exp}, SECRET, algorithm="HS256")


def current_user(token:str = Depends(oauth2)) -> int:
    try:
        return int(jwt.decode(token, SECRET, algorithms = ["HS256"])["sub"])
    except Exception: 
        raise HTTPException(401, "Invalid or expired token")



class Register(BaseModel):
    email : EmailStr
    password: str = Field(min_length=8, max_length =128)
    username: str = Field(min_length=3, max_length=20, pattern=USERNAME_RE)

class ProfileUpdate(BaseModel):
    username : str | None = Field(None, min_length=3, max_length=20, pattern = USERNAME_RE)
    avatar_color: str |None = Field (None, pattern=r"^#[0-9a-fA-F]{6}$")
    daily_goal_ml : int | None = Field(None, ge=500, le=10000)

class DrinkIn(BaseModel):
    client_id: int
    amount_ml:int = Field(gt=0, le=2000)
    logged_at:dt.datetime


def streak(db, user_id: int, goal_ml: int) -> int:
    rows = db.execute(
        "SELECT substr(logged_at, 1, 10) AS d, SUM(amount_ml) AS t "
        "FROM drinks WHERE user_id = ? GROUP BY d",
        (user_id,),
    ).fetchall()
    totals = {r["d"]: r["t"] for r in rows}

    day = dt.date.today()
    if totals.get(day.isoformat(), 0) < goal_ml:
        day -= dt.timedelta(days=1)  # today isn't over yet

    n = 0
    while totals.get(day.isoformat(), 0) >= goal_ml:
        n += 1
        day -= dt.timedelta(days=1)
    return n


def total_since(db, user_id: int, days: int) -> int:
    cutoff = (dt.date.today() - dt.timedelta(days=days - 1)).isoformat()
    row = db.execute(
        "SELECT COALESCE(SUM(amount_ml), 0) AS t FROM drinks WHERE user_id = ? AND logged_at >= ?",
        (user_id, cutoff),
    ).fetchone()
    return row["t"]






@app.post("/auth/register", status_code=201)


def register(body: Register, db=Depends(get_db)):
    email  = body.email.lower().strip()
    try:
        cur = db.execute(
            "INSERT INTO users(email, password_hash) VALUES (?, ?)",
            (email, hasher.hash(body.password)),

        )
        db.execute(
            "INSERT INTO profiles (user_id, username) VALUES (?, ?)",
            (cur.lastrowid, body.username.lower()),

        )


        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email or username already taken")
    return{"access_token" : make_token(cur.lastrowid), "token_type" : "bearer"}


@app.post("/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    row = db.execute(
        "SELECT id, password_hash FROM users WHERE email = ?",
        (form.username.lower().strip(),),

    ).fetchone()
    if not row or not hasher.verify(form.password, row["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    return {"access_token": make_token(row["id"]), "token_type" :"bearer"}



@app.get("/me")
def get_me(me:int = Depends(current_user), db = Depends(get_db)):
    row = db.execute(
        "SELECT u.email, p.username, p.avatar_color, p.daily_goal_ml"
        "FROM users u JOIN profiles p ON p.user_id = u.id WHERE u.id = ?",
        (me,),
    ).fetchone()
    if not row: 
        raise HTTPException(401, "User no longer exists....")
    return dict(row)

@app.patch("/me")
def update_me (body: ProfileUpdate, me: int = Depends(current_user), db = Depends(get_db)):
    fields = body.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(422, "Nothing to update")
    if "username" in fields:
        fields["username"] = fields["username"].lower()


    sets = ", ".join(f"{k} = ?" for k in fields)
    try: 
        db.execute(f"UPDATE profiles SET {sets} WHERE user_id = ?",[*fields.values(), me])
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        raise HTTPException(409, "Username already taken")
    return get_me(me=me, db=db)


@app.get("/users/{username}")
def public_profile(username: str, me :int = Depends(current_user), db = Depends(get_db)):
    p = db.execute(
        "SELECT user_id, username, avatar_color, daily_goal_ml FROM profiles WHERE username = ?",
        (username.lower(),),
    ).fetchone()
    if not p: 
        raise HTTPException(404, "NO SUCH USER")
    return {
      "username": p["username"],
      "avatar_color": p["avatar_color"],
      "week_ml" : total_since(db, p["user_id"], 7),
      "streak" : streak(db, p["user_id"], p["daily_goal_ml"]),

    }


@app.post("/drinks")
def add_drinks(items : list [DrinkIn], me :int = Depends(current_user),db =Depends(get_db)):
    if len(items) > 500:
        raise HTTPException(413, "Too many drinks in one request")
    for d in items:
        db.execute(
            "INSERT OR IGNORE INTO drinks (user_id, client_id, amount_ml, logged_at) VALUES (?,?,?,?)",
            (me, d.client_id, d.amount_ml, d.logged_at.replace(tzinfo=None).isoformat()),

        )

    db.commit()
    return {"synced": len(items)} 