from collections import defaultdict, Counter


class VehicleCounter:

    def __init__(self):

        # Lưu các class mà từng Track ID đã được nhận diện
        # Ví dụ:
        # ID 10 -> ["truck", "truck", "bus", "bus", "bus"]
        self.track_classes = defaultdict(list)

        # Số lần quan sát của từng Track ID
        self.observation_counts = defaultdict(int)

        # Những ID đã được đếm
        self.counted_ids = set()

        # Tổng số phương tiện
        self.total_counts = {
            "person": 0,
            "car": 0,
            "motorcycle": 0,
            "bus": 0,
            "truck": 0
        }

        # Số frame tối thiểu để xác nhận
        self.min_observations = 10

    def update(self, results, model_names):

        if not results:
            return self.total_counts

        result = results[0]

        # Không có Track ID
        if result.boxes.id is None:
            return self.total_counts

        ids = result.boxes.id.cpu().tolist()
        classes = result.boxes.cls.cpu().tolist()
        confidences = result.boxes.conf.cpu().tolist()

        for track_id, cls, confidence in zip(
            ids,
            classes,
            confidences
        ):

            track_id = int(track_id)
            cls = int(cls)
            confidence = float(confidence)

            name = model_names[cls]

            # Chỉ đếm các class cần thiết
            if name not in self.total_counts:
                continue

            # Nếu ID đã được đếm rồi thì bỏ qua
            if track_id in self.counted_ids:
                continue

            # Lưu class
            self.track_classes[track_id].append(name)

            # Tăng observation
            self.observation_counts[track_id] += 1

            observations = self.observation_counts[track_id]

            # Debug
            print(
                f"[TRACK] "
                f"ID={track_id} "
                f"CLASS={name} "
                f"CONF={confidence:.2f} "
                f"OBS={observations}"
            )

            # Chưa đủ dữ liệu
            if observations < self.min_observations:
                continue

            # -----------------------------------------
            # XÁC ĐỊNH CLASS PHỔ BIẾN NHẤT
            # -----------------------------------------

            class_list = self.track_classes[track_id]

            class_counter = Counter(class_list)

            final_class, votes = class_counter.most_common(1)[0]

            # -----------------------------------------
            # XÁC NHẬN ID
            # -----------------------------------------

            self.counted_ids.add(track_id)

            self.total_counts[final_class] += 1

            print(
                f"[CONFIRMED] "
                f"ID={track_id} "
                f"CLASS={final_class} "
                f"OBS={observations} "
                f"VOTES={dict(class_counter)}"
            )

        return self.total_counts

    def reset(self):

        self.track_classes.clear()

        self.observation_counts.clear()

        self.counted_ids.clear()

        for key in self.total_counts:
            self.total_counts[key] = 0