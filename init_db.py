import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "notes.db")
SCHEMA_FILE = os.path.join(BASE_DIR, "schema.sql")

def initialize_database():
    if not os.path.exists(SCHEMA_FILE):
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_FILE}")
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema = f.read()
    with sqlite3.connect(DATABASE) as connection:
        connection.executescript(schema)
    print(f"Database initialized successfully: {DATABASE}")

if __name__ == "__main__":
    initialize_database()
