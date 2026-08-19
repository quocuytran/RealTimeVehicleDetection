import cv2
import time
import os

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QFileDialog,
    QMessageBox,
    QSlider
)

from counter import VehicleCounter
from detector import VehicleDetector
from utils.pdf_report import generate_pdf
from ui.style import STYLE


# ============================================================
# VIDEO LABEL
# ============================================================

class VideoLabel(QLabel):

    point_clicked = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.drawing_enabled = False

        self.setMouseTracking(True)

    def set_drawing_enabled(self, enabled):

        self.drawing_enabled = enabled

        if enabled:
            self.setCursor(Qt.CrossCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event):

        if (
            self.drawing_enabled
            and event.button() == Qt.LeftButton
        ):

            x = event.position().x()
            y = event.position().y()

            self.point_clicked.emit(
                int(x),
                int(y)
            )

        super().mousePressEvent(event)


# ============================================================
# MAIN WINDOW
# ============================================================

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        # ==================================================
        # COUNTER
        # ==================================================

        self.counter = VehicleCounter()

        # ==================================================
        # VIDEO
        # ==================================================

        self.cap = None

        self.video_name = "Camera"

        self.total_frames = 0

        # ==================================================
        # FRAME
        # ==================================================

        self.last_frame = None

        # ==================================================
        # FPS
        # ==================================================

        self.total_fps = 0

        self.frame_count = 0

        self.prev_time = time.time()

        self.fps = 0

        # ==================================================
        # LINE DRAWING
        # ==================================================

        self.line_points = []

        self.drawing_line = False

        # ==================================================
        # UI
        # ==================================================

        self.setWindowTitle(
            "Real-Time Vehicle Detection System"
        )

        self.resize(
            1280,
            720
        )

        self.setStyleSheet(STYLE)

        # ==================================================
        # DETECTOR
        # ==================================================

        self.detector = VehicleDetector()

        # ==================================================
        # TIMER
        # ==================================================

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.update_frame
        )

        # ==================================================
        # BUILD UI
        # ==================================================

        self.build_ui()

    # ============================================================
    # BUILD UI
    # ============================================================

    def build_ui(self):

        central = QWidget()

        self.setCentralWidget(
            central
        )

        main_layout = QVBoxLayout(
            central
        )

        # ==================================================
        # TITLE
        # ==================================================

        title = QLabel(
            "Real-Time Vehicle Detection System"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet(
            """
            font-size:26px;
            font-weight:bold;
            padding:10px;
            """
        )

        main_layout.addWidget(
            title
        )

        # ==================================================
        # CONTENT
        # ==================================================

        content_layout = QHBoxLayout()

        main_layout.addLayout(
            content_layout
        )

        # ==================================================
        # VIDEO
        # ==================================================

        self.video_label = VideoLabel(
            "No Video"
        )

        self.video_label.setAlignment(
            Qt.AlignCenter
        )

        self.video_label.setMinimumSize(
            850,
            550
        )

        self.video_label.setStyleSheet(
            """
            background:black;
            color:white;
            border:2px solid gray;
            border-radius:10px;
            """
        )

        self.video_label.point_clicked.connect(
            self.handle_line_click
        )

        content_layout.addWidget(
            self.video_label,
            3
        )

        # ==================================================
        # STATISTICS
        # ==================================================

        group = QGroupBox(
            "Statistics"
        )

        stats_layout = QGridLayout()

        group.setLayout(
            stats_layout
        )

        self.person_label = QLabel(
            "Person : 0"
        )

        self.car_label = QLabel(
            "Car : 0"
        )

        self.motorcycle_label = QLabel(
            "Motorcycle : 0"
        )

        self.bus_label = QLabel(
            "Bus : 0"
        )

        self.truck_label = QLabel(
            "Truck : 0"
        )

        self.fps_label = QLabel(
            "FPS : 0"
        )

        labels = [
            self.person_label,
            self.car_label,
            self.motorcycle_label,
            self.bus_label,
            self.truck_label,
            self.fps_label
        ]

        for i, label in enumerate(labels):

            label.setStyleSheet(
                "font-size:18px;"
            )

            stats_layout.addWidget(
                label,
                i,
                0
            )

        content_layout.addWidget(
            group,
            1
        )

        # ==================================================
        # PROGRESS SLIDER
        # ==================================================

        self.progress = QSlider(
            Qt.Horizontal
        )

        self.progress.setMinimum(
            0
        )

        self.progress.setMaximum(
            100
        )

        self.progress.setValue(
            0
        )

        main_layout.addWidget(
            self.progress
        )

        # ==================================================
        # BUTTONS
        # ==================================================

        button_layout = QHBoxLayout()

        # ------------------------------------------
        # OPEN VIDEO
        # ------------------------------------------

        self.open_btn = QPushButton(
            "📂 Open Video"
        )

        # ------------------------------------------
        # CAMERA
        # ------------------------------------------

        self.camera_btn = QPushButton(
            "📷 Camera"
        )

        # ------------------------------------------
        # DRAW LINE
        # ------------------------------------------

        self.draw_line_btn = QPushButton(
            "🔴 Draw Line"
        )

        # ------------------------------------------
        # CLEAR LINE
        # ------------------------------------------

        self.clear_line_btn = QPushButton(
            "❌ Clear Line"
        )

        # ------------------------------------------
        # START
        # ------------------------------------------

        self.start_btn = QPushButton(
            "▶ Start"
        )

        # ------------------------------------------
        # STOP
        # ------------------------------------------

        self.stop_btn = QPushButton(
            "⏹ Stop"
        )

        # ------------------------------------------
        # EXPORT
        # ------------------------------------------

        self.export_btn = QPushButton(
            "📊 Export PDF"
        )

        # ==================================================
        # BUTTON CONNECTIONS
        # ==================================================

        self.open_btn.clicked.connect(
            self.open_video
        )

        self.camera_btn.clicked.connect(
            self.open_camera
        )

        self.draw_line_btn.clicked.connect(
            self.start_drawing_line
        )

        self.clear_line_btn.clicked.connect(
            self.clear_line
        )

        self.start_btn.clicked.connect(
            self.start_detection
        )

        self.stop_btn.clicked.connect(
            self.stop_detection
        )

        self.export_btn.clicked.connect(
            self.export_statistics
        )

        # ==================================================
        # ADD BUTTONS
        # ==================================================

        button_layout.addWidget(
            self.open_btn
        )

        button_layout.addWidget(
            self.camera_btn
        )

        button_layout.addWidget(
            self.draw_line_btn
        )

        button_layout.addWidget(
            self.clear_line_btn
        )

        button_layout.addWidget(
            self.start_btn
        )

        button_layout.addWidget(
            self.stop_btn
        )

        button_layout.addWidget(
            self.export_btn
        )

        main_layout.addLayout(
            button_layout
        )

    # ============================================================
    # OPEN VIDEO
    # ============================================================

    def open_video(self):

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )

        if not file_name:
            return

        # ------------------------------------------
        # STOP CURRENT VIDEO
        # ------------------------------------------

        self.timer.stop()

        # ------------------------------------------
        # OPEN VIDEO
        # ------------------------------------------

        self.cap = cv2.VideoCapture(
            file_name
        )

        if not self.cap.isOpened():

            QMessageBox.warning(
                self,
                "Error",
                "Không thể mở video!"
            )

            self.cap = None

            return

        # ------------------------------------------
        # VIDEO NAME
        # ------------------------------------------

        self.video_name = os.path.basename(
            file_name
        )

        # ------------------------------------------
        # RESET
        # ------------------------------------------

        self.reset_detection()

        # ------------------------------------------
        # TOTAL FRAMES
        # ------------------------------------------

        self.total_frames = int(
            self.cap.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )

        # ------------------------------------------
        # FPS
        # ------------------------------------------

        video_fps = self.cap.get(
            cv2.CAP_PROP_FPS
        )

        if video_fps > 0:

            interval = int(
                1000 / video_fps
            )

            self.timer.setInterval(
                max(1, interval)
            )

        else:

            self.timer.setInterval(
                30
            )

        # ------------------------------------------
        # READ FIRST FRAME
        # ------------------------------------------

        ret, frame = self.cap.read()

        if ret:

            self.last_frame = frame.copy()

            self.show_frame(
            frame
        )

        # Return to first frame
            self.cap.set(
            cv2.CAP_PROP_POS_FRAMES,
            0
        )

    # ============================================================
    # OPEN CAMERA
    # ============================================================

    def open_camera(self):

        self.timer.stop()

        self.cap = cv2.VideoCapture(
            0
        )

        if not self.cap.isOpened():

            QMessageBox.warning(
                self,
                "Camera Error",
                "Không thể mở camera!"
            )

            self.cap = None

            return

        self.video_name = "Webcam"

        self.reset_detection()

        self.total_frames = 0

        self.timer.setInterval(
            30
        )
    # Đọc frame đầu tiên để có thể vẽ line
        ret, frame = self.cap.read()

        if ret:

            self.last_frame = frame.copy()

            self.show_frame(
                frame
            )

    # ============================================================
    # RESET DETECTION
    # ============================================================

    def reset_detection(self):

        self.counter.reset()

        self.line_points = []

        self.drawing_line = False

        self.video_label.set_drawing_enabled(
            False
        )

        self.total_fps = 0

        self.frame_count = 0

        self.prev_time = time.time()

        self.fps = 0

        self.progress.setValue(
            0
        )

        self.reset_statistics()

    # ============================================================
    # RESET STATISTICS
    # ============================================================

    def reset_statistics(self):

        self.person_label.setText(
            "Person : 0"
        )

        self.car_label.setText(
            "Car : 0"
        )

        self.motorcycle_label.setText(
            "Motorcycle : 0"
        )

        self.bus_label.setText(
            "Bus : 0"
        )

        self.truck_label.setText(
            "Truck : 0"
        )

        self.fps_label.setText(
            "FPS : 0"
        )

    # ============================================================
    # START DRAWING LINE
    # ============================================================

    def start_drawing_line(self):

        if self.cap is None:

            QMessageBox.warning(
                self,
                "Draw Line",
                "Hãy mở video hoặc camera trước!"
            )

            return

        self.timer.stop()

        self.line_points = []

        self.drawing_line = True

        self.video_label.set_drawing_enabled(
            True
        )

        self.draw_line_btn.setText(
            "🔴 Click 2 Points"
        )

    # ============================================================
    # HANDLE LINE CLICK
    # ============================================================

    def handle_line_click(
        self,
        x,
        y
    ):

        if not self.drawing_line:
            return

        # ------------------------------------------
        # CONVERT LABEL COORDINATE
        # TO FRAME COORDINATE
        # ------------------------------------------

        frame_point = self.label_to_frame(
            x,
            y
        )

        if frame_point is None:
            return

        self.line_points.append(
            frame_point
        )

        # ------------------------------------------
        # FIRST POINT
        # ------------------------------------------

        if len(self.line_points) == 1:

            self.draw_line_btn.setText(
                "🔴 Click Second Point"
            )

            self.redraw_last_frame()

            return

        # ------------------------------------------
        # SECOND POINT
        # ------------------------------------------

        if len(self.line_points) == 2:

            point1 = self.line_points[0]

            point2 = self.line_points[1]

            # Send line to counter
            self.counter.set_line(
                point1,
                point2
            )

            self.drawing_line = False

            self.video_label.set_drawing_enabled(
                False
            )

            self.draw_line_btn.setText(
                "🔴 Draw Line"
            )

            self.redraw_last_frame()

            QMessageBox.information(
                self,
                "Counting Line",
                "Vạch đếm đã được tạo!"
            )

    # ============================================================
    # LABEL → FRAME COORDINATE
    # ============================================================

    def label_to_frame(
        self,
        label_x,
        label_y
    ):

        if self.last_frame is None:
            return None

        frame_height, frame_width = (
            self.last_frame.shape[:2]
        )

        label_width = self.video_label.width()
        label_height = self.video_label.height()

        # ------------------------------------------
        # SCALE KEEP ASPECT RATIO
        # ------------------------------------------

        scale = min(
            label_width / frame_width,
            label_height / frame_height
        )

        displayed_width = int(
            frame_width * scale
        )

        displayed_height = int(
            frame_height * scale
        )

        # ------------------------------------------
        # CENTER OFFSET
        # ------------------------------------------

        offset_x = (
            label_width - displayed_width
        ) / 2

        offset_y = (
            label_height - displayed_height
        ) / 2

        # ------------------------------------------
        # OUTSIDE IMAGE
        # ------------------------------------------

        if (
            label_x < offset_x
            or label_x > offset_x + displayed_width
            or label_y < offset_y
            or label_y > offset_y + displayed_height
        ):

            return None

        # ------------------------------------------
        # CONVERT
        # ------------------------------------------

        frame_x = int(
            (label_x - offset_x) / scale
        )

        frame_y = int(
            (label_y - offset_y) / scale
        )

        frame_x = max(
            0,
            min(
                frame_x,
                frame_width - 1
            )
        )

        frame_y = max(
            0,
            min(
                frame_y,
                frame_height - 1
            )
        )

        return (
            frame_x,
            frame_y
        )

    # ============================================================
    # CLEAR LINE
    # ============================================================

    def clear_line(self):

        self.line_points = []

        self.drawing_line = False

        self.counter.line = None
        self.counter.line_triggered = False

        self.video_label.set_drawing_enabled(
            False
        )

        self.draw_line_btn.setText(
            "🔴 Draw Line"
        )

        self.redraw_last_frame()

    # ============================================================
    # START DETECTION
    # ============================================================

    def start_detection(self):

        if self.cap is None:

            QMessageBox.warning(
                self,
                "Start Detection",
                "Hãy mở video hoặc camera trước!"
            )

            return

        if self.counter.line is None:

            QMessageBox.warning(
                self,
                "Counting Line",
                "Hãy vẽ vạch đếm trước!"
            )

            return

        self.timer.start()

    # ============================================================
    # STOP DETECTION
    # ============================================================

    def stop_detection(self):

        self.timer.stop()

    # ============================================================
    # UPDATE FRAME
    # ============================================================

    def update_frame(self):

        if self.cap is None:
            return

        ret, frame = self.cap.read()

        if not ret:

            self.timer.stop()

            return

        # ==================================================
        # YOLO + BYTETRACK
        # ==================================================

        results = self.detector.track(
            frame
        )

        # ==================================================
        # COUNT VEHICLES CROSSING LINE
        # ==================================================

        total_counts = self.counter.update(
            results,
            self.detector.model.names
        )

        # ==================================================
        # ANNOTATE
        # ==================================================

        annotated = results[0].plot()

        # ==================================================
        # DRAW COUNTING LINE
        # ==================================================

        self.draw_counting_line(
            annotated
        )

        # ==================================================
        # SAVE LAST FRAME
        # ==================================================

        self.last_frame = annotated.copy()

        # ==================================================
        # FPS
        # ==================================================

        current = time.time()

        elapsed = (
            current - self.prev_time
        )

        if elapsed > 0:

            instant = 1 / elapsed

            self.fps = (
                0.9 * self.fps
                + 0.1 * instant
            )

        self.total_fps += self.fps

        self.frame_count += 1

        self.prev_time = current

        # ==================================================
        # UPDATE STATISTICS
        # ==================================================

        self.car_label.setText(
            f"Car : {total_counts['car']}"
        )

        self.motorcycle_label.setText(
            f"Motorcycle : "
            f"{total_counts['motorcycle']}"
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

        # ==================================================
        # PROGRESS
        # ==================================================

        if self.total_frames > 0:

            current_frame = int(
                self.cap.get(
                    cv2.CAP_PROP_POS_FRAMES
                )
            )

            value = int(
                current_frame
                * 100
                / self.total_frames
            )

            value = max(
                0,
                min(
                    value,
                    100
                )
            )

            self.progress.setValue(
                value
            )

        # ==================================================
        # SHOW FRAME
        # ==================================================

        self.show_frame(
            annotated
        )

    # ============================================================
    # DRAW COUNTING LINE
    # ============================================================

    def draw_counting_line(
        self,
        frame
    ):

        if len(self.line_points) == 0:
            return

        # ==================================================
        # LINE COLOR
        # ==================================================
        # GREEN = chưa có xe đi qua
        # RED   = đã có xe đi qua
        # ==================================================

        if self.counter.is_line_triggered():

            line_color = (
                0,
                0,
                255
            )

        else:

            line_color = (
                0,
                255,
                0
            )

        # ==================================================
        # FIRST POINT
        # ==================================================

        point1 = self.line_points[0]

        cv2.circle(
            frame,
            point1,
            7,
            line_color,
            -1
        )

        # ==================================================
        # SECOND POINT
        # ==================================================

        if len(self.line_points) == 2:

            point2 = self.line_points[1]

            cv2.circle(
                frame,
                point2,
                7,
                line_color,
                -1
            )

            cv2.line(
                frame,
                point1,
                point2,
                line_color,
                4
            )

    # ============================================================
    # SHOW FRAME
    # ============================================================

    def show_frame(
        self,
        frame
    ):

        if frame is None:
            return

        rgb = cv2.cvtColor(
            frame,
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

        pixmap = QPixmap.fromImage(
            image
        )

        self.video_label.setPixmap(
            pixmap.scaled(
                self.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    # ============================================================
    # REDRAW LAST FRAME
    # ============================================================

    def redraw_last_frame(self):

        if self.last_frame is None:
            return

        frame = self.last_frame.copy()

        self.draw_counting_line(
            frame
        )

        self.show_frame(
            frame
        )

    # ============================================================
    # AVERAGE FPS
    # ============================================================

    def get_average_fps(self):

        if self.frame_count == 0:
            return 0

        return (
            self.total_fps
            / self.frame_count
        )

    # ============================================================
    # EXPORT STATISTICS
    # ============================================================

    def export_statistics(self):

        counts = self.counter.total_counts

        if sum(counts.values()) == 0:

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

        QMessageBox.information(
            self,
            "Export PDF",
            f"Đã lưu báo cáo:\n{filename}"
        )