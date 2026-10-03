"""
==============================================================================
DATABASE ACCESS LAYER (SQLite)
Maintainer: Person 4 (Database Engineer)
==============================================================================
Provides clean, thread-safe database connections, parameterized query helpers,
schema initialization, and imports for 120 Government of India schemes.
==============================================================================
"""

import os
import sqlite3
from flask import g, current_app

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, 'database.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')
CSV_PATH = os.path.join(BASE_DIR, 'data', 'government_schemes_120.csv')


def get_db(db_path=None):
    """
    Get or create a thread-safe database connection.
    If running within a Flask application context, binds the connection to Flask's `g`.
    Otherwise, returns an independent standalone connection.
    """
    target_path = db_path or (
        current_app.config.get('DATABASE', DEFAULT_DB_PATH)
        if current_app else DEFAULT_DB_PATH
    )

    if current_app:
        if 'db' not in g:
            conn = sqlite3.connect(target_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            g.db = conn
        return g.db
    else:
        conn = sqlite3.connect(target_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn


def close_db(e=None):
    """Closes current database connection if one was opened in the request."""
    if current_app:
        db = g.pop('db', None)
        if db is not None:
            db.close()


def query_db(query, args=(), one=False, db_path=None):
    """
    Executes a SELECT query using parameterized arguments.
    Returns list of dicts (or a single dict if one=True).
    """
    db = get_db(db_path)
    cur = db.execute(query, args)
    rv = cur.fetchall()
    cur.close()

    if not current_app:
        db.close()

    result = [dict(row) for row in rv]
    return (result[0] if result else None) if one else result


def execute_db(query, args=(), db_path=None):
    """
    Executes an INSERT, UPDATE, or DELETE query with parameterized arguments.
    Returns (lastrowid, rowcount).
    """
    db = get_db(db_path)
    cur = db.cursor()
    cur.execute(query, args)
    db.commit()
    last_id = cur.lastrowid
    row_count = cur.rowcount
    cur.close()

    if not current_app:
        db.close()

    return last_id, row_count


def init_db(db_path=None):
    """Initializes tables using schema.sql."""
    target_path = db_path or (
        current_app.config.get('DATABASE', DEFAULT_DB_PATH)
        if current_app else DEFAULT_DB_PATH
    )
    conn = sqlite3.connect(target_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()


def seed_db(force=False, db_path=None, csv_path=None):
    """
    Seeds database from data/government_schemes_120.csv.
    Only seeds if the schemes table is empty, or if force=True.
    """
    target_path = db_path or (
        current_app.config.get('DATABASE', DEFAULT_DB_PATH)
        if current_app else DEFAULT_DB_PATH
    )
    target_csv = csv_path or CSV_PATH

    conn = sqlite3.connect(target_path)
    try:
        cur = conn.cursor()
        # Check if schemes table exists and has rows
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schemes'")
        table_exists = cur.fetchone() is not None

        if table_exists and not force:
            cur.execute("SELECT COUNT(*) as count FROM schemes")
            count = cur.fetchone()[0]
            if count >= 120:
                return False  # Already seeded with 120 schemes
    finally:
        conn.close()

    from scripts.seed_database import seed_database
    summary = seed_database(csv_path=target_csv, db_path=target_path, schema_path=SCHEMA_PATH, verbose=False)
    return summary
