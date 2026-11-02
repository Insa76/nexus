from ultralytics import YOLO

import cv2


model = YOLO("yolov8n.pt")


def detect_objects(
    image_path
):

    results = model(image_path)

    detections = []

    for r in results:

        boxes = r.boxes

        for box in boxes:

            cls = int(box.cls[0])

            conf = float(box.conf[0])

            coords = box.xyxy[0].tolist()

            label = model.names[cls]

            detections.append({

                "label": label,

                "confidence": conf,

                "x1": coords[0],

                "y1": coords[1],

                "x2": coords[2],

                "y2": coords[3]
            })

    return detections