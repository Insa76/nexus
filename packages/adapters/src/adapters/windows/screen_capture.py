from __future__ import annotations

from mss import mss

from PIL import Image


class WindowsScreenCapture:

    def capture(self) -> Image.Image:

        with mss() as sct:

            screenshot = sct.grab(

                sct.monitors[1]

            )

            return Image.frombytes(

                "RGB",

                screenshot.size,

                screenshot.rgb,

            )