import re
from typing import Tuple, Callable
import httpx
import os
from ..Doc2X.Exception import nomal_retry
import concurrent.futures
import logging


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
        (r"!\[[^\]]*\]\(<([^>]+)>\)", lambda m: (m.group(0), m.group(1))),
        (r"!\[[^\]]*\]\(([^)]+)\)", lambda m: (m.group(0), m.group(1))),
    ]

    origin_text_list = []
    imgpath_list = []

    for pattern, extract in patterns:
        for match in re.finditer(pattern, text):
            origin_text, src = extract(match)
            if origin_text not in origin_text_list:  # 检查是否已存在于列表中
                origin_text_list.append(origin_text)
                imgpath_list.append(src)

    return origin_text_list, imgpath_list


@nomal_retry()
def download_img_from_url(url: str, savepath: str) -> None:
    """
    Download the image from the url to the savepath, changing the extension based on the content type.
    """
    with httpx.stream("GET", url) as response:
        content_type = response.headers.get("Content-Type")
        if content_type:
            extension = content_type.split("/")[-1]
            savepath = f"{savepath}.{extension}"
        with open(savepath, "wb") as file:
            for chunk in response.iter_bytes():
                file.write(chunk)
        return extension


def md_replace_imgs(
    mdfile: str,
    replace,
    skip: str = None,
    outputpath: str = "",
    relative: bool = False,
    threads: int = 5,
) -> bool:
    """Replace the image links in the markdown file (cdn links -> local file).

    Args:
        mdfile (str): The markdown file path.
        replace: Str or function to replace the image links. For str only "local" accepted. Defaults to "local".
        skip (str, optional): The URL start with this string will be skipped. Defaults to None. For example, "https://menghuan1918.github.io/pdfdeal-docs".
        outputpath (str, optional): The output path to save the images, if not set, will create a folder named as same as the markdown file name and add `_img`. **⚠️Only works when `replace` is "local".**
        relative (bool, optional): The output path to save the images with relative path. Defaults to False. **⚠️Only works when `replace` is "local".**
        threads (int, optional): The number of threads to download the images. Defaults to 5.

    Returns:
        bool: If all images are downloaded successfully, return True, else return False.
    """
    if isinstance(replace, str) and replace == "local":
        pass
    elif isinstance(replace, Callable):
        pass
    else:
        raise ValueError("The replace must be 'local' or a function.")

    with open(mdfile, "r", encoding="utf-8") as file:
        content = file.read()

    imglist, imgpath = get_imgcdnlink_list(content)
    if len(imglist) == 0:
        logging.warning("No image links found in the markdown file.")
        return True

    no_outputppath_flag = False
    if outputpath == "":
        no_outputppath_flag = True
        outputpath = os.path.splitext(mdfile)[0] + "_img"
    os.makedirs(outputpath, exist_ok=True)

    logging.info(f"Start to download images from file {mdfile}")

    def download_image(i, imgurl, outputpath, relative, mdfile):
        if not imgurl.startswith("http"):
            logging.info(f"Not a valid url: {imgurl}, Skip it.")
            return None
        elif skip and imgurl.startswith(skip):
            logging.info(f"Skip the image: {imgurl}, because it starts with {skip}.")
            return None
        try:
            savepath = f"{outputpath}/img{i}"
            extension = download_img_from_url(imgurl, savepath)
            savepath = f"{savepath}.{extension}"
            if relative:
                savepath = os.path.relpath(savepath, os.path.dirname(mdfile))
                return (imglist[i], f"![{imgurl}](<{savepath}>)\n")
            else:
                savepath = os.path.abspath(savepath)
                return (imglist[i], f"![{imgurl}](<{savepath}>)\n")
        except Exception as e:
            logging.warning(
                f"Error to download the image: {imgurl}, continue to download the next image:\n {e}"
            )
            return None

    replacements = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(
                download_image,
                i,
                imgurl,
                outputpath,
                relative,
                mdfile,
            )
            for i, imgurl in enumerate(imgpath)
        ]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                replacements.append(result)

    flag = True
    for old, new in replacements:
        content = content.replace(old, new)

    if len(replacements) < len(imglist):
        logging.info(
            "Some images may not be downloaded successfully. Please check the log."
        )
        flag = False

    if isinstance(replace, Callable):
        imglist, imgpath = get_imgcdnlink_list(content)

        @nomal_retry()
        def upload_task(i, img_path, replace):
            if img_path.startswith("http://") or img_path.startswith("https://"):
                logging.info(f"Skip the image: {img_path}, because it is a url.")
                return None, None, None
            if os.path.isabs(img_path) is False:
                img_path = os.path.join(os.path.dirname(mdfile), img_path)
            try:
                remote_file_name = f"{os.path.splitext(os.path.basename(mdfile))[0]}_{os.path.basename(img_path)}"
                new_url, flag = replace(img_path, remote_file_name)
                if flag:
                    img_url = f"![{os.path.splitext(os.path.basename(mdfile))[0]}](<{new_url}>)\n"
                    return img_url, True, i
                else:
                    logging.error(
                        f"Error to upload the image: {img_path}, {new_url}, continue to upload the next image."
                    )
                    return new_url, False, i
            except Exception:
                logging.exception(
                    f"=====\nError to upload the image: {img_path}, Continue to upload the next image:"
                )
                return new_url, False, i

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [
                executor.submit(upload_task, i, img_path, replace)
                for i, img_path in enumerate(imgpath)
            ]
            for future in concurrent.futures.as_completed(futures):
                new_url, flag, i = future.result()
                if flag:
                    content = content.replace(imglist[i], new_url)
                elif flag is None:
                    pass
                else:
                    logging.warning(
                        f"=====\nError to upload the image: {imgpath[i]}, {new_url}, continue to upload the next image."
                    )
                    flag = False

        if no_outputppath_flag:
            for img in imgpath:
                try:
                    os.remove(img)
                except Exception:
                    pass
            try:
                os.rmdir(outputpath)
            except Exception as e:
                logging.error(f"\nError to remove the folder: {outputpath}, {e}")

    with open(mdfile, "w", encoding="utf-8") as file:
        file.write(content)

    logging.info(f"Finish to process images in file {mdfile}.")
    return flag


def mds_replace_imgs(
    path: str,
    replace,
    outputpath: str = "",
    relative: bool = False,
    skip: str = None,
    threads: int = 2,
    down_load_threads: int = 3,
) -> Tuple[list, list, bool]:
    """Replace the image links in the markdown file (cdn links -> local file).

    Args:
        path (str): The markdown file path.
        replace: Str or function to replace the image links. For str only "local" accepted. Defaults to "local".
        outputpath (str, optional): The output path to save the images, if not set, will create a folder named as same as the markdown file name and add `_img`.  **⚠️Only works when `replace` is "local".**
        relative (bool, optional): Whether to save the images with relative path. Defaults to False, **⚠️Only works when `replace` is "local".**
        skip (str, optional): The URL start with this string will be skipped. Defaults to None. For example, "https://menghuan1918.github.io/pdfdeal-docs".
        threads (int, optional): The number of threads to download the images. Defaults to 2.
        down_load_threads (int, optional): The number of threads to download the images in one md file. Defaults to 3.

    Returns:
        Tuple[list, list, bool]:
                `list1`: list of successfilly processed md file path, if the file failed, its path will be empty string
                `list2`: list of failed files's error message and its original file path, if some files are successful, its error message will be empty string
                `bool`: If all files are processed successfully, return True, else return False.
    """
    if isinstance(replace, str) and replace == "local":
        pass
    elif isinstance(replace, Callable):
        pass
    else:
        raise ValueError("The replace must be 'local' or a function.")

    from pdfdeal.FileTools.file_tools import gen_folder_list

    mdfiles = gen_folder_list(path=path, mode="md", recursive=True)
    if len(mdfiles) == 0:
        logging.warning("No markdown file found in the path.")
        return [], [], True

    import concurrent.futures

    def process_mdfile(mdfile, replace, outputpath, relative):
        try:
            md_replace_imgs(
                mdfile=mdfile,
                replace=replace,
                outputpath=outputpath,
                relative=relative,
                skip=skip,
                threads=down_load_threads,
            )
            return mdfile, None
        except Exception as e:
            return mdfile, e

    success_files = []
    fail_files = []
    Fail_flag = True

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(process_mdfile, mdfile, replace, outputpath, relative)
            for mdfile in mdfiles
        ]
        for future in concurrent.futures.as_completed(futures):
            mdfile, error = future.result()
            if error:
                Fail_flag = False
                fail_files.append({"error": str(error), "path": mdfile})
                logging.warning(
                    f"Error to process the markdown file: {mdfile}, {error}, continue to process the next markdown file."
                )
            else:
                success_files.append(mdfile)

    logging.info(
        f"\n[MARKDOWN REPLACE] Successfully processed {len(success_files)}/{len(mdfiles)} markdown files."
    )

    if Fail_flag is False:
        logging.info("Some markdown files process failed.")
        return success_files, fail_files, True

    return success_files, fail_files, False
