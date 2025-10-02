import sqlite3
from flask import g
import os


DATABASE = "library.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        db = get_db()
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")

        with open(schema_path, "r", encoding="utf8") as f:
            sql = f.read()
            db.executescript(sql)

        db.commit()