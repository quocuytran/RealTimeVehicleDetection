import csv
import os
from datetime import datetime


def export_csv(counts, video_name, avg_fps):

    os.makedirs("output", exist_ok=True)

    filename = datetime.now().strftime(
        "output/report_%Y%m%d_%H%M%S.csv"
    )

    total = sum(counts.values())

    with open(filename, "w", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow(["Real-Time Vehicle Detection System"])
        writer.writerow([])

        writer.writerow(["Video Name", video_name])
        writer.writerow([
            "Export Time",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
        writer.writerow(["Average FPS", f"{avg_fps:.2f}"])
        writer.writerow([])

        writer.writerow([
            "Vehicle Type",
            "Count",
            "Percentage"
        ])

        for vehicle, count in counts.items():

            percent = 0

            if total > 0:
                percent = count / total * 100

            writer.writerow([
                vehicle,
                count,
                f"{percent:.2f}%"
            ])

        writer.writerow([])

        writer.writerow([
            "Total Vehicles",
            total
        ])

    return filename