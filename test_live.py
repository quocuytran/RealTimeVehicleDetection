import cv2

from utils.live import YouTubeLiveStream


url = input(
    "YouTube Live URL: "
)

stream = YouTubeLiveStream(url)

try:

    stream_url = stream.get_stream_url()

    print("\nConnecting to live stream...")

    cap = cv2.VideoCapture(
        stream_url,
        cv2.CAP_FFMPEG
    )

    if not cap.isOpened():

        print(
            "ERROR: Không thể mở live stream."
        )

        exit()

    print(
        "LIVE STREAM CONNECTED!"
    )

    # ==========================================
    # CREATE RESIZABLE WINDOW
    # ==========================================

    window_name = "YouTube Live Test"

    cv2.namedWindow(
        window_name,
        cv2.WINDOW_NORMAL
    )

    cv2.resizeWindow(
        window_name,
        1280,
        720
    )

    # ==========================================
    # READ STREAM
    # ==========================================

    while True:

        ret, frame = cap.read()

        if not ret:

            print(
                "Không đọc được frame."
            )

            break

        cv2.imshow(
            window_name,
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            break

    cap.release()

    cv2.destroyAllWindows()

except Exception as e:

    print(
        "\nERROR:"
    )

    print(e)