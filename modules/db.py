import sqlite3

import hashlib

from pathlib import Path

BASE_FOLDER = Path("/Users/larajohnston/Library/CloudStorage/OneDrive-Personal/APPS/SUBORDINATES/ACTIVITY LOG")

BASE_FOLDER.mkdir(parents=True, exist_ok=True)

TYPE_1_FOLDER = BASE_FOLDER / "TYPE 1 - ANY TIME"

TYPE_2_FOLDER = BASE_FOLDER / "TYPE 2 - FIXED DAY"

TYPE_3_FOLDER = BASE_FOLDER / "TYPE 3 - FIXED DATE"

TYPE_1_FOLDER.mkdir(parents=True, exist_ok=True)

TYPE_2_FOLDER.mkdir(parents=True, exist_ok=True)

TYPE_3_FOLDER.mkdir(parents=True, exist_ok=True)

DB_PATH = BASE_FOLDER / "subordinates.db"

MASTER_EXCEL_PATH = BASE_FOLDER / "activity_log_master.xlsx"

TYPE_1_EXCEL_PATH = TYPE_1_FOLDER / "type_1_any_time_log.xlsx"

TYPE_2_EXCEL_PATH = TYPE_2_FOLDER / "type_2_fixed_day_log.xlsx"

TYPE_3_EXCEL_PATH = TYPE_3_FOLDER / "type_3_fixed_date_log.xlsx"

def connect_db():

    return sqlite3.connect(DB_PATH, check_same_thread=False)

def hash_password(password):

    return hashlib.sha256(password.encode()).hexdigest()

def init_database():

    conn = connect_db()

    cur = conn.cursor()

    cur.execute("""

        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT,

            email TEXT UNIQUE,

            password_hash TEXT,

            colour TEXT

        )

    """)

    cur.execute("""

        CREATE TABLE IF NOT EXISTS activities (

            id TEXT PRIMARY KEY,

            activity TEXT,

            establishment TEXT,

            website_url TEXT,

            suggested_by TEXT,

            estimated_cost TEXT,

            address TEXT,

            activity_category TEXT,

            timing_type TEXT,

            fixed_event_date TEXT,

            fixed_event_time TEXT,

            fixed_days TEXT,

            fixed_day_times TEXT,

            preferred_option_1_date TEXT,

            preferred_option_1_time TEXT,

            preferred_option_2_date TEXT,

            preferred_option_2_time TEXT,

            preferred_option_3_date TEXT,

            preferred_option_3_time TEXT,

            status TEXT,

            created_at TEXT

        )

    """)

    cur.execute("""

        CREATE TABLE IF NOT EXISTS responses (

            id TEXT PRIMARY KEY,

            activity_id TEXT,

            responder TEXT,

            response TEXT,

            counter_date TEXT,

            counter_time TEXT,

            created_at TEXT

        )

    """)

    cur.execute("""

        CREATE TABLE IF NOT EXISTS calendar_events (

            id TEXT PRIMARY KEY,

            activity_id TEXT,

            event_date TEXT,

            event_time TEXT,

            event_status TEXT,

            created_from TEXT,

            created_at TEXT

        )

    """)

    cur.execute("""

        CREATE TABLE IF NOT EXISTS personal_times (

            id TEXT PRIMARY KEY,

            person TEXT,

            start_date TEXT,

            start_time TEXT,

            end_date TEXT,

            end_time TEXT,

            time_type TEXT,

            note TEXT

        )

    """)

    conn.commit()

    conn.close()

def create_user(name, email, password, colour):

    conn = connect_db()

    cur = conn.cursor()

    try:

        cur.execute("""

            INSERT INTO users (name, email, password_hash, colour)

            VALUES (?, ?, ?, ?)

        """, (name, email, hash_password(password), colour))

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()

def login_user(email, password):

    conn = connect_db()

    cur = conn.cursor()

    cur.execute("""

        SELECT name, email, colour

        FROM users

        WHERE email = ? AND password_hash = ?

    """, (email, hash_password(password)))

    user = cur.fetchone()

    conn.close()

    if user:

        return {

            "name": user[0],

            "email": user[1],

            "colour": user[2]

        }

    return None