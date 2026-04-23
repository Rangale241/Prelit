import sqlite3

conn = sqlite3.connect("ru_en.db", check_same_thread=False)
cur = conn.cursor()

def translate(word):
    cur.execute("SELECT en FROM dict WHERE ru = ?", (word,))
    row = cur.fetchone()
    return row[0] if row else None