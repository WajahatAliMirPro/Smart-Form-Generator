import sqlite3
import json

DB_NAME = "forms.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            fields TEXT NOT NULL -- JSON array of field names
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_id INTEGER,
            data TEXT, -- JSON object
            FOREIGN KEY(form_id) REFERENCES forms(id)
        )
    ''')
    conn.commit()
    conn.close()

def create_form_schema(name, fields):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO forms (name, fields) VALUES (?, ?)",
        (name, json.dumps(fields))
    )
    conn.commit()
    conn.close()

def get_all_forms():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM forms")
    forms = cursor.fetchall()
    conn.close()
    return forms

def get_form_schema(form_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, fields FROM forms WHERE id=?", (form_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row["id"], "name": row["name"], "fields": json.loads(row["fields"])}
    return None

def save_form_submission(form_id, data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO submissions (form_id, data) VALUES (?, ?)",
        (form_id, json.dumps(data))
    )
    conn.commit()
    conn.close()

def get_form_submissions(form_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM submissions WHERE form_id=?", (form_id,))
    submissions = [json.loads(row["data"]) for row in cursor.fetchall()]
    conn.close()
    return submissions