import re
from typing import Tuple
import httpx
import os
from ..Doc2X.Exception import nomal_retry


def get_imgcdnlink_list(text: str) -> Tuple[list, list]:
    """
    Extract the image links from the text.
    Return the image links list and the image path list.
    """
    patterns = [
        (r'<img\s+src="([^"]+)"\s+alt="([^"]*)">', lambda m: (m.group(0), m.group(1))),
        (
            r'<img\s+style="[^"]*"\s+src="([^"]+)"\s*/>',
            lambda m: (m.group(0), m.group(1)),
        ),
        (r'<img\s+src="([^"]+)"\s*/>', lambda m: (m.group(0), m.group(1))),
        (r"!\[[^\]]*\]\(([^)]+)\)", lambda m: (m.group(0), m.group(1))),
    ]

    origin_text_list = []
    imgpath_list = []

    for pattern, extract in patterns:
        for match in re.finditer(pattern, text):
            origin_text, src = extract(match)
            origin_text_list.append(origin_text)
            imgpath_list.append(src)

    return origin_text_list, imgpath_list


@nomal_retry()
def download_img_from_url(url: str, savepath: str) -> None:
    """
    Download the image from the url to the savepath.
    """
    with httpx.stream("GET", url) as response:
        with open(savepath, "wb") as file:
            for chunk in response.iter_bytes():
                file.write(chunk)


def md_replace_imgs(
    mdfile: str,
    replace: str,
    outputpath: str,
    relative: bool = False,
) -> bool:
    """
    Replace the image links in the markdown file with the cdn links.
    Args:
        `mdfile`: `str`, the markdown file path.
        `replace`: `str`, only "local" accepted now, will add "R2", "S3", "OSS" in the future.
        `outputpath`: `str`, the output path to save the images.
        `relative`: `bool`, whether to save the images with relative path. Default is `False`.
    """
    with open(mdfile, "r", encoding="utf-8") as file:
        content = file.read()

    imglist, imgpath = get_imgcdnlink_list(content)
    if len(imglist) == 0:
        print("No image links found in the markdown file.")
        return True

    os.makedirs(outputpath, exist_ok=True)
    Fail_flag = True
    for i, imgurl in enumerate(imgpath):
        try:
            savepath = f"{outputpath}/img{i}.png"
            download_img_from_url(imgurl, savepath)
            if relative:
                savepath = os.path.relpath(savepath, os.path.dirname(mdfile))
                content = content.replace(imglist[i], f"![{imgurl}]({savepath})\n")
            else:
                savepath = os.path.abspath(savepath)
                content = content.replace(imglist[i], f"<img src=\"{savepath}\" alt=\"{imgurl}\">\n")
        except Exception as e:
            Fail_flag = False
            print(f"Error to download the image: {imgurl}, {e}")
            print("Continue to download the next image.")
            continue

    with open(mdfile, "w", encoding="utf-8") as file:
        file.write(content)

    if Fail_flag is False:
        print("Some images download failed.")
        return False

    return True
