# db.py — SQLite persistence for WhatsApp bot

import sqlite3
from datetime import datetime

DB_PATH = "bot.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            message TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_state (
            phone TEXT PRIMARY KEY,
            state TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            description TEXT,
            urgency TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS flow_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            event TEXT,
            value TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_message(phone, message):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (phone, message, created_at) VALUES (?, ?, ?)",
        (phone, message, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def get_user_state(phone):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT state FROM user_state WHERE phone = ?", (phone,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def set_user_state(phone, state):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "REPLACE INTO user_state (phone, state) VALUES (?, ?)",
        (phone, state)
    )
    conn.commit()
    conn.close()


def create_support_ticket(phone):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO support_tickets (phone, created_at) VALUES (?, ?)",
        (phone, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def save_support_description(phone, description):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE support_tickets
        SET description = ?
        WHERE phone = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (description, phone)
    )
    conn.commit()
    conn.close()


def save_support_urgency(phone, urgency):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE support_tickets
        SET urgency = ?
        WHERE phone = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (urgency, phone)
    )
    conn.commit()
    conn.close()


def log_flow_event(phone, event, value=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO flow_events (phone, event, value, created_at) VALUES (?, ?, ?, ?)",
        (phone, event, value, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()
