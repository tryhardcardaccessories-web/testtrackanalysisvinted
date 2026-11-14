import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path("vinted_tracker.db")

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            listing_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            price REAL,
            condition TEXT,
            shipping_cost REAL,
            total_price REAL,
            date_published TEXT,
            url TEXT,
            image_url TEXT,
            source TEXT,
            imported_at TEXT NOT NULL
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            query TEXT NOT NULL,
            excluded TEXT,
            states TEXT,
            min_price REAL DEFAULT 0,
            max_price REAL DEFAULT 0,
            created_at TEXT NOT NULL
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS seen (
            listing_id TEXT PRIMARY KEY,
            seen_at TEXT NOT NULL
        )""")

def upsert_listings(rows):
    count = 0
    with _connect() as conn:
        for row in rows:
            listing_id = str(row.get("listing_id") or row.get("url") or "").strip()
            title = str(row.get("title") or "").strip()
            if not listing_id or not title:
                continue
            price = _number(row.get("price"))
            shipping = _number(row.get("shipping_cost"))
            total = price + shipping if price is not None and shipping is not None else None
            conn.execute("""
                INSERT INTO listings
                (listing_id,title,price,condition,shipping_cost,total_price,date_published,url,image_url,source,imported_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(listing_id) DO UPDATE SET
                  title=excluded.title, price=excluded.price, condition=excluded.condition,
                  shipping_cost=excluded.shipping_cost, total_price=excluded.total_price,
                  date_published=excluded.date_published, url=excluded.url,
                  image_url=excluded.image_url, source=excluded.source
            """, (
                listing_id, title, price, row.get("condition"), shipping, total,
                row.get("date_published"), row.get("url"), row.get("image_url"),
                row.get("source") or "unknown", datetime.utcnow().isoformat(timespec="seconds")
            ))
            count += 1
    return count

def _number(value):
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace(",", ".").replace("€", "").strip())
    except (TypeError, ValueError):
        return None

def get_listings():
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM listings ORDER BY imported_at DESC").fetchall()
    return [dict(r) for r in rows]

def save_search(name, query, excluded, states, min_price, max_price):
    with _connect() as conn:
        conn.execute(
            "INSERT INTO searches(name,query,excluded,states,min_price,max_price,created_at) VALUES(?,?,?,?,?,?,?)",
            (name, query, excluded, json.dumps(states, ensure_ascii=False), min_price, max_price, datetime.utcnow().isoformat())
        )

def list_searches():
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM searches ORDER BY created_at DESC").fetchall()
    result = []
    for r in rows:
        item = dict(r)
        try:
            item["states"] = ", ".join(json.loads(item["states"] or "[]"))
        except Exception:
            item["states"] = item["states"] or ""
        result.append(item)
    return result

def delete_search(search_id):
    with _connect() as conn:
        conn.execute("DELETE FROM searches WHERE id=?", (search_id,))

def mark_seen(listing_id):
    with _connect() as conn:
        conn.execute("INSERT OR REPLACE INTO seen(listing_id,seen_at) VALUES(?,?)",
                     (str(listing_id), datetime.utcnow().isoformat()))

def get_seen_ids():
    with _connect() as conn:
        rows = conn.execute("SELECT listing_id FROM seen").fetchall()
    return {r["listing_id"] for r in rows}
