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


def split_of_md(mdfile: str, mode: str = "auto") -> list:
    """Find the header of the markdown file and add a split line before it.
    Args:
        mdfile (str): The markdown file path.
        mode (str): The way to split. Supports `auto`, `H1`, `H2`, `H3`.
    Returns:
        list: A list of strings where each string is a segment of the markdown file between headers.
    """
    with open(mdfile, "r", encoding="utf-8") as file:
        content = file.read()

    # Define patterns for different header levels
    patterns = {"H1": r"^#\s.*$", "H2": r"^##\s.*$", "H3": r"^###\s.*$"}

    # Determine the pattern based on the mode
    if mode == "auto":
        # Try H3 first, if not found, use H2
        if re.search(patterns["H3"], content, re.MULTILINE):
            pattern = patterns["H3"]
        else:
            pattern = patterns["H2"]
    else:
        pattern = patterns[mode.upper()]

    matches = re.finditer(pattern, content, re.MULTILINE)
    headers = [match.group() for match in matches]
    segments = []
    start = 0
    for header in headers:
        end = content.find(header, start)
        segments.append(content[start:end].strip())
        start = end
    segments.append(content[start:].strip())

    # Process segments to include H1 and H2 titles and split into chunks
    final_segments = []
    h1_title = ""
    h2_title = ""
    for segment in segments:
        # Check if this segment is an H1 or H2 header
        if re.match(patterns["H1"], segment):
            h1_title = segment.lstrip("#").strip()
            h2_title = ""
        elif re.match(patterns["H2"], segment):
            h2_title = segment.lstrip("#").strip()
        else:
            # It's a content segment
            if h2_title:
                prefix = f"H1: {h1_title}, H2: {h2_title}\n"
            elif h1_title:
                prefix = f"H1: {h1_title}\n"
            else:
                prefix = ""

            # Split the content into chunks of ~640 characters, ending at punctuation
            chunk = prefix + segment
            while len(chunk) > 640:
                # Try to find the last punctuation within the first 640 characters
                end = 640
                while end > 0 and chunk[end] not in "。；？！.?;!>":
                    end -= 1

                # If no punctuation found, force split at 640
                if end == 0:
                    end = 640

                final_segments.append(chunk[:end].strip())
                chunk = chunk[end:].lstrip()
            if chunk:
                final_segments.append(chunk.strip())

    return final_segments
