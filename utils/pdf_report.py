import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    KeepTogether
)

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


# ============================================================
# GENERATE BAR CHART
# ============================================================

def create_bar_chart(counts, path):

    names = [
        "Person",
        "Car",
        "Motorcycle",
        "Bus",
        "Truck"
    ]

    values = [
        counts.get("person", 0),
        counts.get("car", 0),
        counts.get("motorcycle", 0),
        counts.get("bus", 0),
        counts.get("truck", 0)
    ]

    plt.figure(figsize=(8, 4.5))

    bars = plt.bar(
        names,
        values
    )

    plt.title(
        "Vehicle Count",
        fontsize=14,
        fontweight="bold"
    )

    plt.ylabel(
        "Number of Vehicles"
    )

    plt.grid(
        axis="y",
        alpha=0.25
    )

    # Hiển thị số trên đầu cột
    for bar, value in zip(bars, values):

        if value > 0:

            plt.text(
                bar.get_x() + bar.get_width() / 2,
                value,
                str(value),
                ha="center",
                va="bottom",
                fontweight="bold"
            )

    plt.tight_layout()

    plt.savefig(
        path,
        dpi=180,
        bbox_inches="tight"
    )

    plt.close()


# ============================================================
# GENERATE PIE CHART
# ============================================================

def create_pie_chart(counts, path):

    names = [
        "Person",
        "Car",
        "Motorcycle",
        "Bus",
        "Truck"
    ]

    values = [
        counts.get("person", 0),
        counts.get("car", 0),
        counts.get("motorcycle", 0),
        counts.get("bus", 0),
        counts.get("truck", 0)
    ]

    # Chỉ lấy những loại có xe
    filtered = [
        (name, value)
        for name, value in zip(names, values)
        if value > 0
    ]

    if not filtered:

        plt.figure(figsize=(6, 4))

        plt.text(
            0.5,
            0.5,
            "No vehicle data",
            ha="center",
            va="center",
            fontsize=14
        )

        plt.axis("off")

    else:

        chart_names = [
            item[0]
            for item in filtered
        ]

        chart_values = [
            item[1]
            for item in filtered
        ]

        plt.figure(figsize=(6, 4.5))

        plt.pie(
            chart_values,
            labels=chart_names,
            autopct="%1.1f%%",
            startangle=90
        )

        plt.title(
            "Vehicle Distribution",
            fontsize=14,
            fontweight="bold"
        )

        plt.axis("equal")

    plt.tight_layout()

    plt.savefig(
        path,
        dpi=180,
        bbox_inches="tight"
    )

    plt.close()


# ============================================================
# GENERATE PDF
# ============================================================

def generate_pdf(
    counts,
    video_name,
    avg_fps
):

    # ========================================================
    # CREATE OUTPUT DIRECTORY
    # ========================================================

    output_dir = "output/reports"

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    filename = datetime.now().strftime(
        f"{output_dir}/report_%Y%m%d_%H%M%S.pdf"
    )

    # ========================================================
    # TEMP CHART DIRECTORY
    # ========================================================

    chart_dir = os.path.join(
        output_dir,
        "_charts"
    )

    os.makedirs(
        chart_dir,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    bar_chart_path = os.path.join(
        chart_dir,
        f"bar_{timestamp}.png"
    )

    pie_chart_path = os.path.join(
        chart_dir,
        f"pie_{timestamp}.png"
    )

    # ========================================================
    # CREATE CHARTS
    # ========================================================

    create_bar_chart(
        counts,
        bar_chart_path
    )

    create_pie_chart(
        counts,
        pie_chart_path
    )

    # ========================================================
    # PDF DOCUMENT
    # ========================================================

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )

    styles = getSampleStyleSheet()

    # ========================================================
    # CUSTOM STYLES
    # ========================================================

    title_style = ParagraphStyle(
        "DashboardTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        leading=26,
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.grey
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        spaceBefore=8,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "NormalCustom",
        parent=styles["Normal"],
        fontSize=9,
        leading=13
    )

    # ========================================================
    # ELEMENTS
    # ========================================================

    elements = []

    # ========================================================
    # HEADER
    # ========================================================

    elements.append(
        Paragraph(
            "Real-Time Vehicle Detection System",
            title_style
        )
    )

    elements.append(
        Paragraph(
            "Traffic Analysis Dashboard",
            subtitle_style
        )
    )

    elements.append(
        Spacer(
            1,
            12
        )
    )

    # ========================================================
    # REPORT INFORMATION
    # ========================================================

    export_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    info_data = [
        [
            Paragraph(
                "<b>Video</b>",
                normal_style
            ),
            Paragraph(
                str(video_name),
                normal_style
            )
        ],
        [
            Paragraph(
                "<b>Export Time</b>",
                normal_style
            ),
            Paragraph(
                export_time,
                normal_style
            )
        ],
        [
            Paragraph(
                "<b>Average FPS</b>",
                normal_style
            ),
            Paragraph(
                f"{avg_fps:.2f}",
                normal_style
            )
        ],
        [
            Paragraph(
                "<b>Detection Model</b>",
                normal_style
            ),
            Paragraph(
                "YOLO11n",
                normal_style
            )
        ],
        [
            Paragraph(
                "<b>Tracking</b>",
                normal_style
            ),
            Paragraph(
                "ByteTrack",
                normal_style
            )
        ],
        [
            Paragraph(
                "<b>Counting Method</b>",
                normal_style
            ),
            Paragraph(
                "Line Crossing",
                normal_style
            )
        ]
    ]

    info_table = Table(
        info_data,
        colWidths=[
            42 * mm,
            135 * mm
        ]
    )

    info_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#E8EAF6")
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#BDBDBD")
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    elements.append(
        info_table
    )

    elements.append(
        Spacer(
            1,
            15
        )
    )

    # ========================================================
    # TOTAL
    # ========================================================

    total = sum(
        counts.values()
    )

    elements.append(
        Paragraph(
            "Key Performance Indicators",
            section_style
        )
    )

    # ========================================================
    # KPI DATA
    # ========================================================

    kpi_values = [
        (
            "TOTAL",
            total
        ),
        (
            "CAR",
            counts.get("car", 0)
        ),
        (
            "MOTORCYCLE",
            counts.get("motorcycle", 0)
        ),
        (
            "BUS",
            counts.get("bus", 0)
        ),
        (
            "TRUCK",
            counts.get("truck", 0)
        ),
        (
            "PERSON",
            counts.get("person", 0)
        )
    ]

    kpi_cells = []

    for name, value in kpi_values:

        cell = Table(
            [
                [
                    Paragraph(
                        f"<b>{name}</b>",
                        ParagraphStyle(
                            "KPIName",
                            parent=normal_style,
                            alignment=TA_CENTER,
                            fontSize=8
                        )
                    )
                ],
                [
                    Paragraph(
                        f"<b>{value}</b>",
                        ParagraphStyle(
                            "KPIValue",
                            parent=normal_style,
                            alignment=TA_CENTER,
                            fontSize=18
                        )
                    )
                ]
            ],
            colWidths=[
                27 * mm
            ],
            rowHeights=[
                8 * mm,
                12 * mm
            ]
        )

        cell.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#F5F5F5")
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.HexColor("#BDBDBD")
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                )
            ])
        )

        kpi_cells.append(
            cell
        )

    kpi_table = Table(
        [
            kpi_cells[:3],
            kpi_cells[3:]
        ],
        colWidths=[
            58 * mm,
            58 * mm,
            58 * mm
        ],
        hAlign="CENTER"
    )

    kpi_table.setStyle(
        TableStyle([
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                3
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                3
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                3
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                3
            )
        ])
    )

    elements.append(
        kpi_table
    )

    elements.append(
        Spacer(
            1,
            15
        )
    )

    # ========================================================
    # CHARTS
    # ========================================================

    elements.append(
        Paragraph(
            "Vehicle Analysis",
            section_style
        )
    )

    bar_image = Image(
        bar_chart_path,
        width=88 * mm,
        height=55 * mm
    )

    pie_image = Image(
        pie_chart_path,
        width=88 * mm,
        height=55 * mm
    )

    chart_table = Table(
        [
            [
                bar_image,
                pie_image
            ]
        ],
        colWidths=[
            90 * mm,
            90 * mm
        ]
    )

    chart_table.setStyle(
        TableStyle([
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            )
        ])
    )

    elements.append(
        chart_table
    )

    elements.append(
        Spacer(
            1,
            10
        )
    )

    # ========================================================
    # STATISTICS TABLE
    # ========================================================

    elements.append(
        Paragraph(
            "Vehicle Statistics",
            section_style
        )
    )

    table_data = [
        [
            "Vehicle Type",
            "Count",
            "Percentage"
        ]
    ]

    vehicle_order = [
        "person",
        "car",
        "motorcycle",
        "bus",
        "truck"
    ]

    for name in vehicle_order:

        count = counts.get(
            name,
            0
        )

        percentage = 0

        if total > 0:

            percentage = (
                count / total * 100
            )

        table_data.append(
            [
                name.capitalize(),
                str(count),
                f"{percentage:.2f}%"
            ]
        )

    table_data.append(
        [
            "TOTAL",
            str(total),
            "100.00%" if total > 0 else "0.00%"
        ]
    )

    statistics_table = Table(
        table_data,
        colWidths=[
            75 * mm,
            45 * mm,
            55 * mm
        ]
    )

    statistics_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#263238")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "BACKGROUND",
                (0, 1),
                (-1, -2),
                colors.HexColor("#FAFAFA")
            ),

            (
                "BACKGROUND",
                (0, -1),
                (-1, -1),
                colors.HexColor("#E8EAF6")
            ),

            (
                "FONTNAME",
                (0, -1),
                (-1, -1),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#BDBDBD")
            ),

            (
                "ALIGN",
                (1, 1),
                (-1, -1),
                "CENTER"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    elements.append(
        statistics_table
    )

    elements.append(
        Spacer(
            1,
            15
        )
    )

    # ========================================================
    # FOOTER
    # ========================================================

    elements.append(
        Paragraph(
            "Generated by Real-Time Vehicle Detection System",
            ParagraphStyle(
                "Footer",
                parent=normal_style,
                alignment=TA_CENTER,
                fontSize=8,
                textColor=colors.grey
            )
        )
    )

    # ========================================================
    # BUILD PDF
    # ========================================================

    doc.build(
        elements
    )

    return filename