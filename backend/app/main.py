from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Literal

import jwt
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from passlib.context import CryptContext

DB_PATH = Path(os.getenv("DB_PATH", "/data/app.db"))
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALG = "HS256"
ACCESS_TOKEN_MINUTES = 60 * 24 * 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@contextmanager
def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS preference_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                raw_text TEXT NOT NULL,
                interpreted_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS inventory_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                purchase_date TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(item_name, unit, purchase_date)
            );

            CREATE TABLE IF NOT EXISTS inventory_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                item_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                purchase_date TEXT,
                raw_text TEXT,
                created_at TEXT NOT NULL
            );
            """
        )

        existing = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
        if existing == 0:
            users = [
                ("you", pwd_context.hash("changeme123"), "Primary User", "owner"),
                ("wife", pwd_context.hash("changeme123"), "Wife User", "owner"),
            ]
            conn.executemany(
                "INSERT INTO users(username, password_hash, full_name, role) VALUES(?,?,?,?)",
                users,
            )


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PreferenceInterpretRequest(BaseModel):
    username: str
    text: str = Field(min_length=3)


class PreferenceInterpretResponse(BaseModel):
    raw_text: str
    interpreted: dict[str, Any]


class InventoryEventRequest(BaseModel):
    action: Literal["add", "use", "set"]
    item_name: str
    quantity: float = Field(gt=0)
    unit: str = "g"
    purchase_date: date | None = None
    text: str | None = None


class InventoryItem(BaseModel):
    item_name: str
    quantity: float
    unit: str
    purchase_date: date
    expiry_date: date
    updated_at: datetime


class PlanRequest(BaseModel):
    start_date: date | None = None


class DayPlan(BaseModel):
    date: date
    breakfast: str
    lunch: str
    servings: int
    notes: str


class WeekPlan(BaseModel):
    days: list[DayPlan]


def expiry_days_for_item(item_name: str) -> int:
    name = item_name.lower()
    if any(x in name for x in ["milk", "curd", "yogurt", "paneer"]):
        return 5
    if any(x in name for x in ["tomato", "spinach", "coriander", "lettuce"]):
        return 4
    if any(x in name for x in ["egg"]):
        return 21
    if any(x in name for x in ["rice", "lentil", "dal", "flour", "atta"]):
        return 90
    return 14


def interpret_preference_text(text: str) -> dict[str, Any]:
    t = text.lower()
    result: dict[str, Any] = {
        "priority": [],
        "avoid": [],
        "frequency_rules": [],
        "raw_summary": text.strip(),
    }

    if "high-protein" in t or "high protein" in t:
        result["priority"].append("high_protein")
    if "vegetarian" in t:
        result["priority"].append("vegetarian_bias")
    for avoid_item in ["egg", "eggs", "peanut", "peanuts", "gluten", "sugar"]:
        if avoid_item in t:
            result["avoid"].append(avoid_item)
    if "twice" in t and "chicken" in t:
        result["frequency_rules"].append("chicken_max_2_per_week")

    return result


def create_token(username: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    payload = {"sub": username, "exp": exp}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


app = FastAPI(title="ManageMyKitchen MVP API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/login", response_model=LoginResponse)
def login(body: LoginRequest) -> LoginResponse:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT username, password_hash FROM users WHERE username=?", (body.username,)
        ).fetchone()
    if not row or not pwd_context.verify(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return LoginResponse(access_token=create_token(body.username))


@app.post("/preferences/interpret", response_model=PreferenceInterpretResponse)
def preferences_interpret(body: PreferenceInterpretRequest) -> PreferenceInterpretResponse:
    interpreted = interpret_preference_text(body.text)
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO preference_events(username, raw_text, interpreted_json, created_at) VALUES(?,?,?,?)",
            (body.username, body.text, json.dumps(interpreted), now),
        )
    return PreferenceInterpretResponse(raw_text=body.text, interpreted=interpreted)


@app.post("/inventory/events")
def inventory_event(body: InventoryEventRequest) -> dict[str, str]:
    today = date.today()
    purchase_date = body.purchase_date or today
    expiry_date = purchase_date + timedelta(days=expiry_days_for_item(body.item_name))
    now = datetime.now(timezone.utc).isoformat()

    with get_conn() as conn:
        if body.action == "add":
            conn.execute(
                """
                INSERT INTO inventory_items(item_name, quantity, unit, purchase_date, expiry_date, updated_at)
                VALUES(?,?,?,?,?,?)
                ON CONFLICT(item_name, unit, purchase_date)
                DO UPDATE SET quantity=quantity+excluded.quantity, updated_at=excluded.updated_at
                """,
                (
                    body.item_name,
                    body.quantity,
                    body.unit,
                    purchase_date.isoformat(),
                    expiry_date.isoformat(),
                    now,
                ),
            )
        elif body.action == "use":
            row = conn.execute(
                """
                SELECT id, quantity FROM inventory_items
                WHERE item_name=? AND unit=?
                ORDER BY purchase_date ASC LIMIT 1
                """,
                (body.item_name, body.unit),
            ).fetchone()
            if not row:
                raise HTTPException(status_code=400, detail="Item not in inventory")
            new_qty = row["quantity"] - body.quantity
            if new_qty < 0:
                raise HTTPException(status_code=400, detail="Insufficient quantity")
            conn.execute(
                "UPDATE inventory_items SET quantity=?, updated_at=? WHERE id=?",
                (new_qty, now, row["id"]),
            )
        else:  # set
            conn.execute(
                """
                INSERT INTO inventory_items(item_name, quantity, unit, purchase_date, expiry_date, updated_at)
                VALUES(?,?,?,?,?,?)
                ON CONFLICT(item_name, unit, purchase_date)
                DO UPDATE SET quantity=excluded.quantity, updated_at=excluded.updated_at
                """,
                (
                    body.item_name,
                    body.quantity,
                    body.unit,
                    purchase_date.isoformat(),
                    expiry_date.isoformat(),
                    now,
                ),
            )

        conn.execute(
            "INSERT INTO inventory_events(action, item_name, quantity, unit, purchase_date, raw_text, created_at) VALUES(?,?,?,?,?,?,?)",
            (
                body.action,
                body.item_name,
                body.quantity,
                body.unit,
                purchase_date.isoformat(),
                body.text,
                now,
            ),
        )

    return {"status": "ok"}


@app.get("/inventory/current", response_model=list[InventoryItem])
def inventory_current() -> list[InventoryItem]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT item_name, quantity, unit, purchase_date, expiry_date, updated_at FROM inventory_items WHERE quantity > 0 ORDER BY item_name"
        ).fetchall()
    return [
        InventoryItem(
            item_name=r["item_name"],
            quantity=r["quantity"],
            unit=r["unit"],
            purchase_date=date.fromisoformat(r["purchase_date"]),
            expiry_date=date.fromisoformat(r["expiry_date"]),
            updated_at=datetime.fromisoformat(r["updated_at"]),
        )
        for r in rows
    ]


@app.post("/plans/generate-week", response_model=WeekPlan)
def generate_week_plan(body: PlanRequest) -> WeekPlan:
    start = body.start_date or date.today()
    dishes_breakfast = [
        "Moong chilla + curd",
        "Vegetable poha + peanuts",
        "Oats upma",
        "Besan cheela + mint chutney",
        "Idli + sambar",
        "Paneer toast",
        "Fruit + yogurt bowl",
    ]
    dishes_lunch = [
        "Dal, rice, cucumber salad",
        "Rajma, jeera rice, carrot salad",
        "Chole, chapati, onion salad",
        "Veg khichdi + curd",
        "Paneer bhurji + roti",
        "Sambar rice + beans poriyal",
        "Lentil soup + millet roti",
    ]
    days: list[DayPlan] = []
    for i in range(7):
        d = start + timedelta(days=i)
        days.append(
            DayPlan(
                date=d,
                breakfast=dishes_breakfast[i % len(dishes_breakfast)],
                lunch=dishes_lunch[i % len(dishes_lunch)],
                servings=2,
                notes="Auto-generated MVP plan; integrate recipe engine next.",
            )
        )
    return WeekPlan(days=days)
