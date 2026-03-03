import sqlite3
import bcrypt

DB_NAME = "app.db"


def create_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password BLOB NOT NULL
        )
    """)

    # Reference documents
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reference_docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            content TEXT
        )
    """)

    # Questionnaires
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questionnaires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            content TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------- AUTH ---------------- #

def register_user(email, password):
    conn = create_connection()
    cursor = conn.cursor()

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, hashed_password)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def login_user(email, password):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, password FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    conn.close()

    if user:
        user_id, stored_password = user
        if bcrypt.checkpw(password.encode(), stored_password):
            return user_id

    return None


# ---------------- SAVE DOCS ---------------- #

def save_reference_doc(user_id, name, content):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO reference_docs (user_id, name, content) VALUES (?, ?, ?)",
        (user_id, name, content)
    )

    conn.commit()
    conn.close()


def save_questionnaire(user_id, name, content):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO questionnaires (user_id, name, content) VALUES (?, ?, ?)",
        (user_id, name, content)
    )

    conn.commit()
    conn.close()


# ---------------- FETCH DOCS ---------------- #

def get_reference_docs(user_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, content FROM reference_docs WHERE user_id = ?",
        (user_id,)
    )

    docs = cursor.fetchall()
    conn.close()
    return docs


def get_latest_questionnaire(user_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, content FROM questionnaires WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,)
    )

    q = cursor.fetchone()
    conn.close()
    return q