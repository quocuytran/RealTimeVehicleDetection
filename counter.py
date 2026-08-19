from collections import defaultdict


class VehicleCounter:

    def __init__(self):

        # ==================================================
        # CLASS CONFIDENCE
        # ==================================================

        # Track ID -> class -> tổng confidence
        self.class_scores = defaultdict(
            lambda: defaultdict(float)
        )

        # Track ID -> số lần quan sát
        self.observation_counts = defaultdict(int)

        # ==================================================
        # TRACK POSITION
        # ==================================================

        # Track ID -> vị trí bottom-center frame trước
        self.previous_positions = {}

        # ==================================================
        # COUNTED IDS
        # ==================================================

        # Những Track ID đã đi qua line
        self.counted_ids = set()

        # ==================================================
        # TOTAL COUNTS
        # ==================================================

        self.total_counts = {
            "person": 0,
            "car": 0,
            "motorcycle": 0,
            "bus": 0,
            "truck": 0
        }

        # ==================================================
        # COUNTING LINE
        # ==================================================

        # ((x1, y1), (x2, y2))
        self.line = None

        # Số frame line còn hiển thị màu đỏ
        self.line_red_frames = 0

        # Thời gian đỏ, tính theo số frame
        self.line_red_duration = 8

        # ==================================================
        # CLASS CONFIRMATION
        # ==================================================

        # Tối thiểu số observation trước khi xác định class
        self.min_observations = 3

    # ============================================================
    # SET LINE
    # ============================================================

    def set_line(self, point1, point2):

        self.line = (
            point1,
            point2
        )

        # Line mới → màu xanh
        self.line_red_frames = 0

        print(
            f"[LINE] "
            f"Point 1={point1}, "
            f"Point 2={point2}"
        )

    # ============================================================
    # RESET
    # ============================================================

    def reset(self):

        self.class_scores.clear()

        self.observation_counts.clear()

        self.previous_positions.clear()

        self.counted_ids.clear()

        # Reset total
        for key in self.total_counts:
            self.total_counts[key] = 0

        # Reset line state
        self.line_red_frames = 0

    # ============================================================
    # LINE STATE
    # ============================================================

    def is_line_triggered(self):
        return self.line_red_frames > 0

    # ============================================================
    # SIDE OF LINE
    # ============================================================

    def _side_of_line(self, point):

        if self.line is None:
            return 0

        (x1, y1), (x2, y2) = self.line

        px, py = point

        value = (
            (x2 - x1) * (py - y1)
            - (y2 - y1) * (px - x1)
        )

        if value > 0:
            return 1

        if value < 0:
            return -1

        return 0

    # ============================================================
    # CHECK POINT ON LINE SEGMENT
    # ============================================================

    def _point_on_segment(
        self,
        point
    ):

        if self.line is None:
            return False

        (x1, y1), (x2, y2) = self.line

        px, py = point

        # ------------------------------------------
        # LINE LENGTH
        # ------------------------------------------

        dx = x2 - x1
        dy = y2 - y1

        length_squared = (
            dx * dx
            + dy * dy
        )

        if length_squared == 0:
            return False

        # ------------------------------------------
        # PROJECT POINT ONTO LINE
        # ------------------------------------------

        t = (
            (px - x1) * dx
            + (py - y1) * dy
        ) / length_squared

        # ------------------------------------------
        # POINT MUST BE BETWEEN P1 AND P2
        # ------------------------------------------

        if t < 0 or t > 1:
            return False

        # ------------------------------------------
        # CLOSEST POINT ON LINE
        # ------------------------------------------

        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        # ------------------------------------------
        # DISTANCE FROM POINT TO LINE
        # ------------------------------------------

        distance_squared = (
            (px - closest_x) ** 2
            + (py - closest_y) ** 2
        )

        # Cho phép sai số vài pixel
        tolerance = 15

        return (
            distance_squared
            <= tolerance * tolerance
        )

    # ============================================================
    # CHECK SEGMENT INTERSECTION
    # ============================================================

    def _segments_intersect(
        self,
        p1,
        p2,
        p3,
        p4
    ):

        def orientation(
            a,
            b,
            c
        ):

            value = (
                (b[0] - a[0])
                * (c[1] - a[1])
                -
                (b[1] - a[1])
                * (c[0] - a[0])
            )

            if value > 0:
                return 1

            if value < 0:
                return -1

            return 0

        o1 = orientation(
            p1,
            p2,
            p3
        )

        o2 = orientation(
            p1,
            p2,
            p4
        )

        o3 = orientation(
            p3,
            p4,
            p1
        )

        o4 = orientation(
            p3,
            p4,
            p2
        )

        # Hai đoạn cắt nhau
        if (
            o1 != o2
            and o3 != o4
        ):
            return True

        return False

    # ============================================================
    # CHECK CROSSING
    # ============================================================

    def _crossed_line(
        self,
        previous_point,
        current_point
    ):

        if self.line is None:
            return False

        line_start, line_end = self.line

        # ==================================================
        # 1. TRACK MOVEMENT MUST INTERSECT LINE SEGMENT
        # ==================================================

        movement_intersects = self._segments_intersect(
            previous_point,
            current_point,
            line_start,
            line_end
        )

        if movement_intersects:
            return True

        # ==================================================
        # 2. CHECK CURRENT POINT NEAR LINE SEGMENT
        # ==================================================

        if self._point_on_segment(
            current_point
        ):

            return True

        # ==================================================
        # 3. CHECK PREVIOUS POINT NEAR LINE SEGMENT
        # ==================================================

        if self._point_on_segment(
            previous_point
        ):

            return True

        return False

    # ============================================================
    # UPDATE
    # ============================================================

    def update(
        self,
        results,
        model_names
    ):

        if self.line_red_frames > 0:
            self.line_red_frames -= 1
        if not results:
            return self.total_counts

        result = results[0]

        # ==================================================
        # NO TRACK IDS
        # ==================================================

        if result.boxes.id is None:
            return self.total_counts

        # ==================================================
        # GET DATA
        # ==================================================

        ids = (
            result.boxes.id
            .cpu()
            .tolist()
        )

        classes = (
            result.boxes.cls
            .cpu()
            .tolist()
        )

        confidences = (
            result.boxes.conf
            .cpu()
            .tolist()
        )

        boxes = (
            result.boxes.xyxy
            .cpu()
            .tolist()
        )

        # ==================================================
        # PROCESS EACH TRACK
        # ==================================================

        for (
            track_id,
            cls,
            confidence,
            box
        ) in zip(
            ids,
            classes,
            confidences,
            boxes
        ):

            track_id = int(
                track_id
            )

            cls = int(
                cls
            )

            confidence = float(
                confidence
            )

            name = model_names[cls]

            # ==================================================
            # ONLY TARGET CLASSES
            # ==================================================

            if name not in self.total_counts:
                continue

            # ==================================================
            # BOUNDING BOX
            # ==================================================

            x1, y1, x2, y2 = box

            # ==================================================
            # BOTTOM CENTER
            # ==================================================

            center_x = int(
                (x1 + x2) / 2
            )

            bottom_y = int(
                y2
            )

            current_position = (
                center_x,
                bottom_y
            )

            # ==================================================
            # SAVE CLASS CONFIDENCE
            # ==================================================

            if track_id not in self.counted_ids:

                self.class_scores[
                    track_id
                ][name] += confidence

                self.observation_counts[
                    track_id
                ] += 1

            # ==================================================
            # CHECK CROSSING
            # ==================================================

            if track_id in self.previous_positions:

                previous_position = (
                    self.previous_positions[
                        track_id
                    ]
                )

                crossed = self._crossed_line(
                    previous_position,
                    current_position
                )

                # ==================================================
                # VEHICLE CROSSED LINE
                # ==================================================

                if crossed:

                    # ------------------------------------------
                    # DON'T COUNT SAME TRACK ID AGAIN
                    # ------------------------------------------

                    if track_id not in self.counted_ids:

                        scores = self.class_scores[
                            track_id
                        ]

                        if scores:

                            # ----------------------------------
                            # FINAL CLASS
                            # ----------------------------------

                            final_class = max(
                                scores,
                                key=scores.get
                            )

                            # ----------------------------------
                            # COUNT
                            # ----------------------------------

                            self.counted_ids.add(
                                track_id
                            )

                            self.total_counts[
                                final_class
                            ] += 1

                            # ----------------------------------
                            # LINE → RED
                            # ----------------------------------

                            # Line chuyển sang đỏ
                            self.line_red_frames = self.line_red_duration

                            self.line_triggered = True

                            print(
                                f"[COUNTED] "
                                f"ID={track_id} "
                                f"Class={final_class} "
                                f"Observations="
                                f"{self.observation_counts[track_id]} "
                                f"Scores="
                                f"{dict(scores)}"
                            )

            # ==================================================
            # SAVE CURRENT POSITION
            # ==================================================

            self.previous_positions[
                track_id
            ] = current_position

        return self.total_counts