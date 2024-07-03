import re
from typing import Tuple
import httpx


def get_imgcdnlink_list(text: str) -> Tuple[list, list]:
    """
    Extract the image links from the text.
    return the image links list and the image path list.
    """
    # <img src="image_path" alt="alt text">
    pattern = r'<img\s+src="([^"]+)"\s+alt="([^"]*)">'
    matches = re.findall(pattern, text)

    origin_text_list = []
    imgpath_list = []
    for match in matches:
        origin_text_list.append(f'<img src="{match[0]}" alt="{match[1]}">')
        imgpath_list.append(match[0])

    return origin_text_list, imgpath_list


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
) -> bool:
    """
    Replace the image links in the markdown file with the cdn links.
    Args:
        `mdfile`: `str`, the markdown file path.
        `replace`: `str`, only "local" accepted now, will add "R2", "S3", "OSS" in the future.
        `outputpath`: `str`, the output path to save the images.
    """
    with open(mdfile, "r", encoding="utf-8") as file:
        content = file.read()

    imglist, imgpath = get_imgcdnlink_list(content)
    if len(imglist) == 0:
        print("No image links found in the markdown file.")
        return True

    Fail_flag = True
    for i, imgurl in enumerate(imgpath):
        try:
            savepath = f"{outputpath}/img{i}.png"
            download_img_from_url(imgurl, savepath)
            content = content.replace(
                imglist[i], f'<img src="{savepath}" alt="img{i}">'
            )
        except Exception as e:
            Fail_flag = False
            print(f"Erorr to download the image: {imgurl}, {e}")
            print("Continue to download the next image.")
            continue

    with open(mdfile, "w", encoding="utf-8") as file:
        file.write(content)

    if Fail_flag:
        print("Some images download failed.")
        return False

    return True
