import re
from typing import Tuple


def gen_imglist_from_md(mdfile: str) -> Tuple[list, list]:
    """
    Find the images used in the markdown file.
    Args:
        `mdfile`: `str`, the markdown file path.
    Returns:
        `imglist`: `list`, the image texts list used in the markdown file.
        `imgpath`: `list`, the image path list used in the markdown file.
    """
    imglist = []
    imgpath = []

    with open(mdfile, "r", encoding="utf-8") as file:
        content = file.read()

    # Get ![alt text](image_path) or <img src="image_path" alt="alt text">
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)|<img\s+src="([^"]+)"\s+alt="([^"]*)">'
    matches = re.findall(pattern, content)

    for match in matches:
        if match[0] and match[1]:  # The type ![alt text](image_path)
            imglist.append(f"![{match[0]}]({match[1]})")
            imgpath.append(match[1])
        elif match[2] and match[3]:  # The type <img src="image_path" alt="alt text">
            imglist.append(f'<img src="{match[2]}" alt="{match[3]}">')
            imgpath.append(match[2])

    return imglist, imgpath


def split_of_md(mdfile: str, mode: str) -> list:
    """Find the header of the markdown file and add a split line before it.

    Args:
        mdfile (str): The markdown file path.
        mode (str): The way to split. Only support `title`(split by every title) now.

    Returns:
        list: A list of strings where each string is a segment of the markdown file between headers.
    """
    with open(mdfile, "r", encoding="utf-8") as file:
        content = file.read()

    pattern = r"(^#{1,6}\s.*$)"
    matches = re.finditer(pattern, content, re.MULTILINE)
    headers = [match.group() for match in matches]

    segments = []
    start = 0
    for header in headers:
        end = content.find(header, start)
        segments.append(content[start:end].strip())
        start = end

    segments.append(content[start:].strip())
    return segments
