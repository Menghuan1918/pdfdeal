import io
from PIL import Image
from pypdf import PdfReader
import re
import emoji
import unicodedata
import os


def OCR_easyocr(path, language=["ch_sim", "en"], GPU=False):
    try:
        import easyocr
    except ImportError:
        raise ImportError("Please install easyocr first, use 'pip install easyocr'")
    reader = easyocr.Reader(language, gpu=GPU)
    texts = ""
    if os.path.isfile(path) and path.endswith((".jpg", ".png", ".jpeg")):
        result = reader.readtext(path, detail=0, paragraph=True)
        texts += "\n".join(result)
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.endswith((".jpg", ".png", ".jpeg")):
                    result = reader.readtext(file_path, detail=0, paragraph=True)
                    texts += "\n".join(result)
    return texts


def OCR_pytesseract(path, language=["eng"], GPU=False):
    try:
        import pytesseract
    except ImportError:
        raise ImportError(
            "Please install pytesseract first, use 'pip install pytesseract'"
        )
    text = ""
    if os.path.isfile(path) and path.endswith((".jpg", ".png", ".jpeg")):
        text += pytesseract.image_to_string(path, lang=language[0])
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.endswith((".jpg", ".png", ".jpeg")):
                    text += pytesseract.image_to_string(file_path, lang=language[0])
                    text += "\n"
    return text


def OCR_pass(path, language=["ch_sim", "en"], GPU=False):
    return ""

def clean_text(text):
    # remove extra whitespaces
    text = re.sub(r"\n\s*\n", "\n\n", text)

    # remove special characters
    text = re.sub(r"-\d+-", "", text)

    def is_valid_unicode(char):
        # Check if a character is a valid unicode character
        try:
            char_name = unicodedata.name(char)
            return True
        except ValueError:
            return False

    cleaned_text = []
    for char in text:
        if (
            char.isalnum()
            or char.isspace()
            or emoji.is_emoji(char)
            or is_valid_unicode(char)
        ):
            cleaned_text.append(char)
    text = "".join(cleaned_text)

    return text


def clear_cache():
    temp_image_folder = os.path.join(
        os.path.expanduser("~"), ".cache", "pdfdeal", "pictures"
    )
    for file in os.listdir(temp_image_folder):
        file_path = os.path.join(temp_image_folder, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


def extract_text_and_images(
    pdf_path, ocr=OCR_easyocr, language=["ch_sim", "en"], GPU=False
):
    Text = []

    # Open the PDF file
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)

        for page in reader.pages:
            # Get the text content of the page
            text = page.extract_text()
            temp_image_folder = os.path.join(
                os.path.expanduser("~"), ".cache", "pdfdeal", "pictures"
            )
            os.makedirs(temp_image_folder, exist_ok=True)
            clear_cache()
            # Get the images on the page
            images = page.images
            for id, image in enumerate(images):
                image_data = image.data
                image_stream = io.BytesIO(image_data)
                pil_image = Image.open(image_stream)
                # Save to HOME/.cache/pdfdeal/pictures, if the directory does not exist, create it
                temp_image_path = os.path.join(
                    os.path.expanduser("~"),
                    ".cache",
                    "pdfdeal",
                    "pictures",
                    f"{id}.png",
                )
                pil_image.save(temp_image_path)

            # Use ocr to extract text from images
            ocr_text = ocr(temp_image_folder, language, GPU)
            text += f"\n{ocr_text}"
            Text.append(clean_text(text))
        clear_cache()
    return Text
