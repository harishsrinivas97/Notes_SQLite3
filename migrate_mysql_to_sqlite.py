"""Copy existing MySQL Notes database data into notes.db. Run once after init_db.py."""
import os
import sqlite3
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
SQLITE_DB = os.path.join(BASE_DIR, "notes.db")

# Update these values if your MySQL settings differ.
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "notes"),
}

def migrate():
    mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        mysql_cur = mysql_conn.cursor()
        mysql_cur.execute("SELECT id, username, email, password FROM users")
        users = mysql_cur.fetchall()
        mysql_cur.execute("SELECT nid, titel, content, created_at, user_id FROM note")
        notes = mysql_cur.fetchall()

        with sqlite3.connect(SQLITE_DB) as db:
            db.execute("PRAGMA foreign_keys = ON")
            existing_users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            existing_notes = db.execute("SELECT COUNT(*) FROM note").fetchone()[0]
            if existing_users or existing_notes:
                raise RuntimeError("SQLite tables already contain data. Backup first; refusing to duplicate or overwrite records.")

            db.executemany(
                "INSERT INTO users (id, username, email, password) VALUES (?, ?, ?, ?)",
                users,
            )
            db.executemany(
                "INSERT INTO note (nid, titel, content, created_at, user_id) VALUES (?, ?, ?, ?, ?)",
                notes,
            )
            # Ensure future AUTOINCREMENT values continue after imported IDs.
            db.commit()
        print(f"Migration complete: {len(users)} users and {len(notes)} notes copied.")
    finally:
        mysql_conn.close()

if __name__ == "__main__":
    migrate()
