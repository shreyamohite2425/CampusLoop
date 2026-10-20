
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB = Path(__file__).with_name("campusloop.db")


def connect_db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with connect_db() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                date TEXT NOT NULL,
                kind TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Active'
            )
        """)
        count = con.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        if count == 0:
            con.execute("""
                INSERT INTO items
                (title, description, category, location, date, kind)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("Black Calculator", "Scientific calculator",
                  "Electronics", "Library", "2026-10-20", "Found"))


@app.route("/")
def home():
    q = request.args.get("q", "").strip()
    with connect_db() as con:
        items = con.execute("""
            SELECT * FROM items
            WHERE title LIKE ? OR description LIKE ?
            ORDER BY id DESC
        """, (f"%{q}%", f"%{q}%")).fetchall()
        stats = con.execute("""
            SELECT COUNT(*) AS total,
            SUM(CASE WHEN kind='Lost' AND status='Active' THEN 1 ELSE 0 END) AS lost,
            SUM(CASE WHEN kind='Found' AND status='Active' THEN 1 ELSE 0 END) AS found,
            SUM(CASE WHEN status='Recovered' THEN 1 ELSE 0 END) AS recovered
            FROM items
        """).fetchone()
    return render_template("index.html", items=items, stats=stats, q=q)


@app.route("/add", methods=["POST"])
def add_item():
    fields = ["title", "description", "category", "location", "date", "kind"]
    values = [request.form.get(field, "").strip() for field in fields]

    if not all(values) or values[5] not in ("Lost", "Found"):
        return "Please complete every field correctly.", 400

    with connect_db() as con:
        con.execute("""
            INSERT INTO items (title, description, category, location, date, kind)
            VALUES (?, ?, ?, ?, ?, ?)
        """, values)

    return redirect(url_for("home"))


@app.route("/recover/<int:item_id>", methods=["POST"])
def recover(item_id):
    with connect_db() as con:
        con.execute(
            "UPDATE items SET status='Recovered' WHERE id=?",
            (item_id,)
        )
    return redirect(url_for("home"))


@app.route("/health")
def health():
    return {"status": "healthy"}, 200


@app.route("/metrics")
def metrics():
    with connect_db() as con:
        total = con.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    return f"campusloop_items_total {total}\n", 200, {
        "Content-Type": "text/plain; version=0.0.4"
    }


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
