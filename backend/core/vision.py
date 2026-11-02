import pytesseract

from PIL import Image

from pytesseract import Output


TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = (
    TESSERACT_PATH
)


def extract_text(image_path):

    image = Image.open(image_path)

    text = pytesseract.image_to_string(
        image
    )

    return text

def detect_ui_elements(
    image_path
):

    image = Image.open(image_path)

    data = pytesseract.image_to_data(

        image,

        output_type=Output.DICT
    )

    elements = []

    total = len(data["text"])

    for i in range(total):

        text = data["text"][i].strip()

        if not text:
            continue

        elements.append({

            "text": text,

            "x": data["left"][i],

            "y": data["top"][i],

            "w": data["width"][i],

            "h": data["height"][i]
        })

    return elements