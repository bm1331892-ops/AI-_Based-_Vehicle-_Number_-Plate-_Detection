import sqlite3

conn = sqlite3.connect('database/vehicle.db')

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_number TEXT,
    vehicle_type TEXT,
    plate_color TEXT,
    category TEXT
)
''')

cursor.execute('''
INSERT INTO vehicles
(vehicle_number, vehicle_type, plate_color, category)
VALUES
('AP39AB1234', 'Car', 'White', 'Private Vehicle')
''')

conn.commit()
conn.close()

print("Database Created Successfully")