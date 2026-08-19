from ultralytics import YOLO
from config import MODEL_PATH


class VehicleDetector:

    def __init__(self):
        self.model = YOLO(MODEL_PATH)

    def detect(self, frame):
        return self.model(
            frame,
            conf=0.25,
            imgsz=640,
            classes=[0, 1, 2, 3, 5, 7],
            verbose=False
        )

    def track(self, frame):
        return self.model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            conf=0.25,
            imgsz=640,
            classes=[0, 1, 2, 3, 5, 7],
            verbose=False
        )

    def count_objects(self, results):

        counts = {}

        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                name = self.model.names[cls]
                counts[name] = counts.get(name, 0) + 1

        return counts