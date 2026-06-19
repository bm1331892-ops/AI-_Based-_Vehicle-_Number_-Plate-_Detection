from ultralytics import YOLO

model = YOLO("yolov8_model/best.pt")

def detect_plate(image_path):
    results = model(image_path)
    return results