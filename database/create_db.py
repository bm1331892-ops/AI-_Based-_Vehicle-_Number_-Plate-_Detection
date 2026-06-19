import sqlite3

conn = sqlite3.connect("vehicles.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_number TEXT,
    vehicle_type TEXT,
    color TEXT,
    image_path TEXT
)
""")

conn.commit()
conn.close()

print("Database Created Successfully")