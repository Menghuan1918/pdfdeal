import io
from PIL import Image
from pypdf import PdfReader
import re
import emoji
import unicodedata
import os
import easyocr


def OCR_easyocr(path, language=["ch_sim", "en"], GPU=False):
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

            # Get the images on the page
            images = page.images
            for image in images:
                image_data = image.data
                image_stream = io.BytesIO(image_data)
                pil_image = Image.open(image_stream)

                # Save to HOME/.cache/pdfdeal/pictures, if the directory does not exist, create it
                temp_image_path = os.path.join(
                    os.path.expanduser("~"),
                    ".cache",
                    "pdfdeal",
                    "pictures",
                    f"{image.id}.png",
                )
                os.makedirs(os.path.dirname(temp_image_path), exist_ok=True)
                pil_image.save(temp_image_path)

            # Use ocr to extract text from images
            temp_image_path = os.path.join(
                os.path.expanduser("~"), ".cache", "pdfdeal", "pictures"
            )
            ocr_text = ocr(temp_image_path, language, GPU)
            text += f"\n{ocr_text}"
            Text.append(clean_text(text))
    return Text