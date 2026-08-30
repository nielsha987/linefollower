import sqlite3
import os
import time

DB_PATH = "robot_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Tabel voor runs
    c.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT
        )
    """)

    # Tabel voor sensordata
    c.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            name TEXT,
            value REAL,
            timestamp INTEGER,
            FOREIGN KEY(run_id) REFERENCES runs(run_id)
        )
    """)

    conn.commit()
    conn.close()

def start_new_run():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    start_time = time.strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO runs (start_time) VALUES (?)", (start_time,))
    run_id = c.lastrowid
    conn.commit()
    conn.close()
    return run_id

def insert_sensor_data(run_id, name, value, timestamp=None):
    if timestamp is None:
        timestamp = int(time.time() * 1000)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO sensor_data (run_id, name, value, timestamp) VALUES (?, ?, ?, ?)",
        (run_id, name, value, timestamp)
    )
    conn.commit()
    conn.close()
