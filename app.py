from flask import Flask, render_template, request
import sqlite3
import os
import cv2
import easyocr
from ultralytics import YOLO

app = Flask(__name__)

# Load Vehicle Detection Model
vehicle_model = YOLO("yolov8n.pt")

# OCR
reader = easyocr.Reader(['en'])

# -----------------------------
# Database
# -----------------------------
def init_db():
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

init_db()

# -----------------------------
# Home
# -----------------------------
@app.route('/')
def home():
    return render_template('index.html')

# -----------------------------
# Upload
# -----------------------------
@app.route('/upload', methods=['GET', 'POST'])
def upload():

    if request.method == 'POST':

        if 'vehicle_image' not in request.files:
            return "No file uploaded"

        file = request.files['vehicle_image']

        if file.filename == '':
            return "No file selected"

        os.makedirs("static/uploads", exist_ok=True)

        filepath = os.path.join(
            "static",
            "uploads",
            file.filename
        )

        file.save(filepath)

        image = cv2.imread(filepath)

        # -----------------------------
        # Vehicle Detection
        # -----------------------------
        vehicle_type = "Unknown"

        try:

            results = vehicle_model(filepath)

            for result in results:

                if len(result.boxes) > 0:

                    cls = int(result.boxes[0].cls[0].item())
                    vehicle_type = vehicle_model.names[cls]
                    break

        except Exception as e:
            print("Vehicle Detection Error:", e)

        # -----------------------------
        # Vehicle Number Detection
        # -----------------------------
        vehicle_number = "Not Detected"

        try:

            h, w, _ = image.shape

            plate_region = image[
                int(h * 0.55):h,
                0:w
            ]

            gray = cv2.cvtColor(
                plate_region,
                cv2.COLOR_BGR2GRAY
            )

            ocr_result = reader.readtext(gray)

            print("OCR RESULT:", ocr_result)

            texts = []

            for item in ocr_result:

                if len(item) >= 2:
                    texts.append(item[1])

            if len(texts) > 0:

                combined_text = "".join(texts)

                combined_text = (
                    combined_text
                    .replace(" ", "")
                    .replace("-", "")
                    .upper()
                )

                vehicle_number = combined_text

        except Exception as e:
            print("OCR Error:", e)

        # -----------------------------
        # Color Detection
        # -----------------------------
        color = "Unknown"

        try:

            resized = cv2.resize(
                image,
                (100, 100)
            )

            avg_color = resized.mean(axis=0).mean(axis=0)

            b, g, r = avg_color

            if r > 180 and g > 180 and b > 180:
                color = "White"

            elif r > g and r > b:
                color = "Red"

            elif g > r and g > b:
                color = "Green"

            elif b > r and b > g:
                color = "Blue"

            else:
                color = "Gray"

        except Exception as e:
            print("Color Error:", e)

        # -----------------------------
        # Save Database
        # -----------------------------
        try:

            conn = sqlite3.connect("vehicles.db")
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO vehicles
                (
                    vehicle_number,
                    vehicle_type,
                    color,
                    image_path
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    vehicle_number,
                    vehicle_type,
                    color,
                    filepath
                )
            )

            conn.commit()
            conn.close()

        except Exception as e:
            print("Database Error:", e)

        return render_template(
            "result.html",
            vehicle_number=vehicle_number,
            vehicle_type=vehicle_type,
            color=color,
            image_path=filepath
        )

    return render_template('upload.html')

# -----------------------------
# Search
# -----------------------------
@app.route('/search', methods=['GET', 'POST'])
def search():

    vehicle = None

    if request.method == 'POST':

        vehicle_number = request.form[
            'vehicle_number'
        ].strip().upper()

        conn = sqlite3.connect(
            "vehicles.db"
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                vehicle_number,
                vehicle_type,
                color,
                image_path
            FROM vehicles
            WHERE UPPER(vehicle_number) = ?
            """,
            (vehicle_number,)
        )

        vehicle = cursor.fetchone()

        conn.close()

    return render_template(
        'search.html',
        vehicle=vehicle
    )

if __name__ == '__main__':
    app.run(debug=True)