import io
from PIL import Image
from pypdf import PdfReader
import re
import emoji
import unicodedata
import os
import zipfile

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


def gen_folder_list(path: str, mode: str) -> list:
    """
    Generate a list of files in the folder
    `path`: folder path
    `mode`: 'pdf' or 'img'

    return: list of files
    """
    if mode == "pdf":
        return [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".pdf")]
    elif mode == "img":
        return [
            os.path.join(path, f)
            for f in os.listdir(path)
            if f.endswith(".png") or f.endswith(".jpg") or f.endswith(".jpeg")
        ]
    else:
        raise ValueError("Mode should be 'pdf' or 'img'")

def unzip(zip_path: str) -> str:
    """
    Unzip file and return the extract path
    """
    folder_name = os.path.splitext(os.path.basename(zip_path))[0]
    extract_path = os.path.join(os.path.dirname(zip_path), folder_name)
    os.makedirs(extract_path, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
        os.remove(zip_path)
        return extract_path
    except Exception as e:
        raise Exception(f"Unzip file error! {e}")

def texts_to_file(texts, filepath, output_format="txt"):
    """
    Write texts to a file.
    `texts`: a list of strings, each string is a paragraph.
    `filepath`: the folder path of the file to write.
    `output_format`: the format of the output file, default is "txt",acceptable values are "txt", "md".

    Return the path of the output file.
    """
    import time

    if output_format not in ["txt", "md"]:
        raise ValueError("The output format is not supported.")
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    try:
        temp_file = os.path.join(filepath, f"{time.time()}.{output_format}")
    except Exception as e:
        raise RuntimeError(f"Error: {e}")
    with open(temp_file, "w") as file:
        for text in texts:
            file.write(text)
            file.write("\n")
    return temp_file
