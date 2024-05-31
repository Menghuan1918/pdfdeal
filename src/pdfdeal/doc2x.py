import requests
import json
import os
import zipfile

Base_URL = "https://api.doc2x.noedgeai.com/api"


def refresh_key(personal_key):
    """
    Get a new key by refreshing the old key
    """
    url = Base_URL + "/token/refresh"
    get_res = requests.post(url, headers={"Authorization": "Bearer " + personal_key})
    if get_res.status_code == 200:
        return json.loads(get_res.content.decode("utf-8"))["data"]["token"]
    else:
        raise RuntimeError(
            f"Refresh key failed, status code: {get_res.status_code}:{get_res.text}"
        )


def un_zip(zip_path):
    """
    Unzip the file
    """
    folder_name = os.path.splitext(os.path.basename(zip_path))[0]
    extract_path = os.path.join(os.path.dirname(zip_path), folder_name)

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
        os.remove(zip_path)
        return extract_path
    except Exception as e:
        raise RuntimeError(f"Unzip failed: {e}")


def uuid2file(api_key, uuid, output_format, output_path=None):
    """
    `api_key`: personal key, get from function 'refresh_key'
    `uuid`: uuid of the file
    `output_path`: output file path, default is None, which means same directory as the input file
    `output_format`: Accept "md", "md_dollar", "latex", "docx", which will save to output_path
    """
    url = Base_URL + f"/export?request_id={uuid}&to={output_format}"
    output_format = output_format if output_format == "docx" else "zip"
    get_res = requests.get(url, headers={"Authorization": "Bearer " + api_key})
    if get_res.status_code == 200:
        if output_path is None:
            path = os.getcwd()
            output_path = os.path.join(path, "doc2xoutput", f"{uuid}.{output_format}")
        else:
            if not output_path.endswith(output_format):
                output_path = os.path.join(output_path, f"{uuid}.{output_format}")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(get_res.content)
        if output_format == "zip":
            output_path = un_zip(output_path)
        return output_path
    else:
        raise RuntimeError(
            f"Uuid2file failed, status code: {get_res.status_code}:{get_res.text}"
        )


def pic2file(
    api_key, image_file, output_path=None, output_format="text", img_correction=True
):
    """
    `api_key`: personal key, get from function 'refresh_key'
    `image_file`: image file path
    `output_path`: output file path, default is None, which means same directory as the input file
    `output_format`: output format, default is 'text', which will return the text content.
    Also accept "md", "md_dollar", "latex", "docx", which will save to output_path
    `img_correction`: whether to correct the image, default is True
    """
    url = Base_URL + "/platform/img"
    img_correction = "true" if img_correction else "false"
    get_res = requests.post(
        url,
        headers={"Authorization": "Bearer " + api_key},
        files={"file": open(image_file, "rb")},
        data={"img_correction": img_correction},
        stream=True,
    )
    text_json = []
    if get_res.status_code == 200:
        decode_res = get_res.content.decode("utf-8")
        for line in decode_res.split("\n"):
            if len(line) > 0:
                if line.startswith("data:"):
                    line = line[len("data: ") :]
                    text_json.append(json.loads(line))
    else:
        raise RuntimeError(
            f"Pic2file failed, status code: {get_res.status_code}:{get_res.text}"
        )
    uuid = text_json[0]["uuid"]
    text = ""
    for text_temp in text_json:
        try:
            text += text_temp["data"]["pages"][0]["md"]
        except:
            pass
    if output_format == "text":
        return text
    else:
        if output_format not in ["md", "latex", "docx", "md_dollar"]:
            raise ValueError(
                "output_format should be one of 'text', 'md', 'latex', 'docx', 'md_dollar'"
            )
        try:
            return uuid2file(api_key, uuid, output_format, output_path)
        except Exception as e:
            raise RuntimeError(f"Deal with uuid: \n {uuid} \n failed: {e}")


def pdf2file(api_key, pdf_file, output_path=None, output_format="text", ocr=True):
    """
    `api_key`: personal key, get from function 'refresh_key'
    `pdf_file`: pdf file path
    `output_path`: output file path, default is None, which means same directory as the input file
    `output_format`: output format, default is 'text', which will return the text content.
    Also accept "md", "md_dollar", "latex", "docx", which will save to output_path
    `ocr`: whether to use OCR, default is True
    """
    url = Base_URL + "/platform/pdf"
    ocr = "true" if ocr else "false"
    get_res = requests.post(
        url,
        headers={"Authorization": "Bearer " + api_key},
        files={"file": open(pdf_file, "rb")},
        data={"ocr": ocr},
        stream=True,
    )
    text_json = []
    if get_res.status_code == 200:
        decode_res = get_res.content.decode("utf-8")
        for line in decode_res.split("\n"):
            if len(line) > 0:
                if line.startswith("data:"):
                    line = line[len("data: ") :]
                    text_json.append(json.loads(line))
    else:
        raise RuntimeError(
            f"Pdf2file failed, status code: {get_res.status_code}:{get_res.text}"
        )
    uuid = text_json[0]["uuid"]
    text = ""
    for text_temp in text_json:
        try:
            text += text_temp["data"]["pages"][0]["md"]
        except:
            pass
    if output_format == "text":
        return text
    else:
        if output_format not in ["md", "latex", "docx", "md_dollar"]:
            raise ValueError(
                "output_format should be one of 'text', 'md', 'latex', 'docx', 'md_dollar'"
            )
        try:
            return uuid2file(api_key, uuid, output_format, output_path)
        except Exception as e:
            raise RuntimeError(f"Deal with uuid: \n {uuid} \n failed: {e}")


class Doc2x:
    def __init__(self, api_key) -> None:
        self.key = refresh_key(api_key)

    def pic2file(
        self, image_file, output_path=None, output_format="text", img_correction=True
    ):
        return pic2file(
            self.key, image_file, output_path, output_format, img_correction
        )

    def OCR(self, path, language=["None"], GPU=False):
        return pic2file(self.key, path, output_format="text", img_correction=True)

    def pdf2file(self, pdf_file, output_path=None, output_format="text", ocr=True):
        return pdf2file(self.key, pdf_file, output_path, output_format, ocr)
