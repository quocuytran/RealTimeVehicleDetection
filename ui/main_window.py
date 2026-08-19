import cv2
import time
import os

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QSlider
from counter import VehicleCounter
from utils.pdf_report import generate_pdf

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QFileDialog
)

from utils.exporter import export_csv
from detector import VehicleDetector
from ui.style import STYLE


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.counter = VehicleCounter()
        self.video_name = "Camera"
        self.video_name = "Webcam"

        self.total_fps = 0
        self.frame_count = 0

        self.last_frame = None

        self.setWindowTitle("Real-Time Vehicle Detection System")
        self.resize(1280, 720)

        self.current_counts = {}

        self.setStyleSheet(STYLE)

        self.total_frames = 0

        self.detector = VehicleDetector()

        self.cap = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.prev_time = time.time()
        self.fps = 0

        self.build_ui()

    # ==================================================

    def build_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        title = QLabel("Real-Time Vehicle Detection System")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:26px;
            font-weight:bold;
            padding:10px;
        """)

        main_layout.addWidget(title)

        content_layout = QHBoxLayout()

        main_layout.addLayout(content_layout)

        # ---------------- VIDEO ----------------

        self.video_label = QLabel("No Video")

        self.video_label.setAlignment(Qt.AlignCenter)

        self.video_label.setMinimumSize(850, 550)

        self.video_label.setStyleSheet("""
            background:black;
            color:white;
            border:2px solid gray;
            border-radius:10px;
        """)

        content_layout.addWidget(self.video_label, 3)

        # ---------------- Statistics ----------------

        group = QGroupBox("Statistics")

        stats_layout = QGridLayout()

        group.setLayout(stats_layout)

        self.person_label = QLabel("Person : 0")
        self.car_label = QLabel("Car : 0")
        self.motorcycle_label = QLabel("Motorcycle : 0")
        self.bus_label = QLabel("Bus : 0")
        self.truck_label = QLabel("Truck : 0")
        self.fps_label = QLabel("FPS : 0")

        labels = [
            self.person_label,
            self.car_label,
            self.motorcycle_label,
            self.bus_label,
            self.truck_label,
            self.fps_label
        ]

        for i, label in enumerate(labels):
            label.setStyleSheet("font-size:18px;")
            stats_layout.addWidget(label, i, 0)

        content_layout.addWidget(group, 1)

        # ==========================
        # Progress Slider
        # ==========================

        self.progress = QSlider(Qt.Horizontal)

        self.progress.setMinimum(0)

        self.progress.setMaximum(100)

        main_layout.addWidget(self.progress)

        # ---------------- Buttons ----------------

        button_layout = QHBoxLayout()

        self.open_btn = QPushButton("📂 Open Video")
        self.camera_btn = QPushButton("📷 Camera")
        self.start_btn = QPushButton("▶ Start")
        self.stop_btn = QPushButton("⏹ Stop")
        self.export_btn = QPushButton("📊 Export PDF")

        self.open_btn.clicked.connect(self.open_video)
        self.camera_btn.clicked.connect(self.open_camera)
        self.start_btn.clicked.connect(self.start_detection)
        self.stop_btn.clicked.connect(self.stop_detection)
        self.export_btn.clicked.connect(self.export_statistics)

        button_layout.addWidget(self.open_btn)
        button_layout.addWidget(self.camera_btn)
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.export_btn)

        main_layout.addLayout(button_layout)

    # ==================================================

    def open_video(self):

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )

        self.video_name = os.path.basename(file_name)

        if file_name:

            self.cap = cv2.VideoCapture(file_name)

            self.counter.reset()

            self.total_frames = int(
                self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            )

    # ==================================================

    def open_camera(self):

        self.cap = cv2.VideoCapture(0)

        self.counter.reset()

    # ==================================================

    def start_detection(self):

        if self.cap is not None:
            self.timer.start(30)

    # ==================================================

    def stop_detection(self):

        self.timer.stop()

    # ==================================================

    def update_frame(self):

        if self.cap is None:
            return

        ret, frame = self.cap.read()

        if not ret:
            return

        results = self.detector.track(frame)

        total_counts = self.counter.update(
            results,
            self.detector.model.names
        )

        if results[0].boxes.id is not None:
            ids = results[0].boxes.id.cpu().tolist()
            print("Tracking IDs:", ids)
        
        counts = self.detector.count_objects(results)

        print(total_counts)

        self.current_counts = counts

        annotated = results[0].plot()

        self.last_frame = annotated.copy()

        import cv2

        current = time.time()

        instant = 1 / (current - self.prev_time)

        self.fps = 0.9 * self.fps + 0.1 * instant

        self.total_fps += self.fps
        self.frame_count += 1

        self.prev_time = current

        self.car_label.setText(
            f"Car : {total_counts['car']}"
        )

        self.motorcycle_label.setText(
            f"Motorcycle : {total_counts['motorcycle']}"
        )

        self.bus_label.setText(
            f"Bus : {total_counts['bus']}"
        )

        self.truck_label.setText(
            f"Truck : {total_counts['truck']}"
        )

        self.person_label.setText(
            f"Person : {total_counts['person']}"
        )

        self.fps_label.setText(
            f"FPS : {self.fps:.1f}"
        )
        if self.total_frames > 0:

            current_frame = int(
                self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            )

            value = int(
                current_frame * 100 / self.total_frames
            )

        self.progress.setValue(value)

        self.progress.setValue(value)
        rgb = cv2.cvtColor(
            annotated,
            cv2.COLOR_BGR2RGB
        )

        h, w, ch = rgb.shape

        image = QImage(
            rgb.data,
            w,
            h,
            ch * w,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(image)

        self.video_label.setPixmap(
            pixmap.scaled(
                self.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )
    def get_average_fps(self):

        if self.frame_count == 0:
            return 0

        return self.total_fps / self.frame_count
    
    def export_statistics(self):

        counts = self.counter.total_counts

        if sum(counts.values()) == 0:

            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(
                self,
                "Export PDF",
                "Chưa có dữ liệu để xuất!"
            )

            return

        filename = generate_pdf(
            counts,
            self.video_name,
            self.get_average_fps()
        )

        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "Export PDF",
            f"Đã lưu báo cáo:\n{filename}"
        )
    def get_average_fps(self):

        if self.frame_count == 0:
            return 0

        return self.total_fps / self.frame_count