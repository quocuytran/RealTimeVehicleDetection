import subprocess


class YouTubeLiveStream:

    def __init__(self, url):
        self.url = url

    def get_stream_url(self):

        command = [
            "yt-dlp",
            "-g",
            self.url
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(
                result.stderr
            )

        stream_url = result.stdout.strip()

        if not stream_url:
            raise RuntimeError(
                "Không lấy được stream URL."
            )

        return stream_url