import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

def generate_pdf(counts, video_name, avg_fps):

    os.makedirs("output/reports", exist_ok=True)

    filename = datetime.now().strftime(
        "output/reports/report_%Y%m%d_%H%M%S.pdf"
    )

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "<b>Real-Time Vehicle Detection System Report</b>",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"<b>Video:</b> {video_name}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Export Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Average FPS:</b> {avg_fps:.2f}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    total = sum(counts.values())

    elements.append(
        Paragraph(
            "<b>Vehicle Statistics</b>",
            styles["Heading2"]
        )
    )

    table_data = [
        ["Vehicle", "Count", "Percentage"]
    ]

    for name, count in counts.items():

        percent = 0

        if total > 0:
            percent = count / total * 100

        table_data.append([
            name.capitalize(),
            str(count),
            f"{percent:.2f}%"
        ])

    table = Table(table_data)

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),

            ("ALIGN", (0, 0), (-1, -1), "CENTER"),

            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ])
    )

    elements.append(table)

    elements.append(Spacer(1, 20))
    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"<b>Total Vehicles:</b> {total}",
            styles["Heading2"]
        )
    )

    doc.build(elements)

    return filename