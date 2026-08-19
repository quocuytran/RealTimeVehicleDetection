from ultralytics import YOLO
import cv2

print("OpenCV:", cv2.__version__)

model = YOLO("yolov8n.pt")

print("YOLO loaded successfully!")