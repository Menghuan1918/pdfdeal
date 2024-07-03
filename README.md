<div align=center>
<h1 aligh="center">
pdfdeal
</h1>
  
**For better RAG!**

<br>

<a href="https://github.com/Menghuan1918/pdfdeal/actions/workflows/python-test-linux.yml">
  <img src="https://github.com/Menghuan1918/pdfdeal/actions/workflows/python-test-linux.yml/badge.svg?branch=main" alt="Package tests on Ubuntu">
</a>
<a href="https://github.com/Menghuan1918/pdfdeal/actions/workflows/python-test-win.yml">
  <img src="https://github.com/Menghuan1918/pdfdeal/actions/workflows/python-test-win.yml/badge.svg?branch=main" alt="Package tests on Windows">
</a>
<a href="https://github.com/Menghuan1918/pdfdeal/actions/workflows/python-test-mac.yml">
  <img src="https://github.com/Menghuan1918/pdfdeal/actions/workflows/python-test-mac.yml/badge.svg?branch=main" alt="Package tests on MacOS">
</a>

<br>

🗺️ ENGLISH | [简体中文](README_CN.md)

</div>


## What's new

Check out the [task list](https://github.com/users/Menghuan1918/projects/3) to see what new features are in the works!

### V0.1.3

#### ✨ New Features

- New feature: replace all remote images in Markdown files with local ones.
- Refactored `pdfdeal` function, now supports batch input of files.

#### 🐛 Bug Fixes

- Reformatting the output of native OCR file processing functions.
- `pdfdeal` can't output md files under some circumstances.
- Remove `Doc2x` used in version 0.0.x.

#### 🚀Other

- Documentation will be refactored for the next release

### V0.1.x

Please see  [0.1.2 release](https://github.com/Menghuan1918/pdfdeal/releases/tag/v0.1.2), [0.1.1 release](https://github.com/Menghuan1918/pdfdeal/releases/tag/v0.1.1) and [0.1.0 release](https://github.com/Menghuan1918/pdfdeal/releases/tag/v0.1.0)。


## Summary

Easier to deal with PDF, extract readable text and OCR to recognise image text and clean the format. Make it more suitable for knowledge base construction.

Its going to use [easyocr](https://github.com/JaidedAI/EasyOCR) or [Doc2x](./docs/doc2x.md) to recognise the image and add it to the original text. If the output format uses pdf format, this ensures that the text is on the same number of pages in the new PDF as the original. You can use knowledge base applications (such as [Dify](https://github.com/langgenius/dify),[FastGPT](https://github.com/labring/FastGPT)) after the PDF processing, so that theoretically can reach a better recognition rate.

![111](https://github.com/Menghuan1918/pdfdeal/assets/122662527/58155389-f846-41fd-9314-1cd86282e66a)

![222](https://github.com/Menghuan1918/pdfdeal/assets/122662527/457036e8-9d78-458a-8a48-763bd33e95f9)

## Support for Doc2x

Added support for Doc2x, which currently has a daily 500-page **free** usage quota, and its recognition of tables/formulas is excellent. 

You can also use Doc2x support module **alone** to convert pdf to markdown/latex/docx directly like below. See [Doc2x Support](./docs/doc2x.md) for more.

```python
from pdfdeal.doc2x import Doc2X

Client = Doc2X()
filelist = gen_folder_list("./test","pdf")
# This is a built-in function for generating the folder under the path of all the pdf, you can give any list of the form of the path of the pdf
Client.pdfdeal(filelist)
```

## Usage
See the [example codes](https://github.com/Menghuan1918/pdfdeal?tab=readme-ov-file#processes-all-the-files-in-a-file-and-saves-them-in-the-output-folder).

### Install
Install from PyPI:

```bash
pip install 'pdfdeal[easyocr]'
```

Using `pytesseract`, make sure you have install [tesseract](https://github.com/tesseract-ocr/tesseract) first:

```bash
pip install 'pdfdeal[pytesseract]'
```

Using own custom OCR function or Doc2x or skip OCR:

```bash
pip install pdfdeal
```

Install from source:

```bash
pip install 'pdfdeal[all] @ git+https://github.com/Menghuan1918/pdfdeal.git'
```

### Parameters
Import the function by`from pdfdeal import deal_pdf`. Explanation of the parameters accepted by the function:

- **input**: `str` or `list`
  - Description: The local path to the PDF file that you want to process.
  - Example:  `["1.pdf","2.pdf"]`

- **output**: `str`, optional, default: `"texts"`
  - Description: Specifies the type of output you want. The options are:
    - `"texts"`: Extracted text from the PDF as a list of strings, one per page.
    - `"md"`: Markdown formatted text.
    - `"pdf"`: A new PDF file with the extracted text.
  - Example: `"md"`

- **ocr**: `function`, optional, default: `None`
  - Description: A custom OCR (Optical Character Recognition) function. If not provided, the default OCR function will be used. Use string "pytesseract" to use pytesseract, string "pass" to skip OCR
  - Example custom OCR function: `custom_ocr_function`, input is :`(path, language=["ch_sim", "en"], GPU=False)`, return a `string`,`bool`


- **language**: `list`, optional, default: `["ch_sim", "en"]`
  - Description: A list of languages to be used in OCR. The default languages are Simplified Chinese (`"ch_sim"`) and English (`"en"`). ["eng"] for pytesseract.
  - Example: `["en", "fr"]`

- **GPU**: `bool`, optional, default: `False`
  - Description: A boolean flag indicating whether to use GPU for OCR processing. If set to `True`, GPU will be used.
  - Example: `True`

- **path**: `str`, optional, default: `None`
  - Description: The directory path where the output file will be saved. This parameter is only used when the `output` type is `"md"` or `"pdf"`.
  - Example: `"/path/to/save/output"`

### Processes all the files in a file and saves them in the Output folder

```python
import os
from pdfdeal import deal_pdf
for root, dirs, files in os.walk("./PPT"):
    for file in files:
        file_path = os.path.join(root, file)
        deal_pdf(
            input=file_path, output="pdf", language=["en"], path="./Output", GPU=True
        )
        print(f"Deal with {file_path} successfully!")
```

### Get the the list of text in the pdf

```python
from pdfdeal import deal_pdf
Text = deal_pdf(input="test.pdf", output="texts", language=["en"], GPU=True)
for text in Text:
  print(text)
```

### Using pytesseract to do OCR

```python
from pdfdeal import deal_pdf, gen_folder_list
files = gen_folder_list("tests/pdf", "pdf")
output_path = deal_pdf(
    input=files,
    output="md",
    ocr="pytesseract",
    language=["eng"],
    path="Output",
)
for f in output_path:
    print(f"Save processed file to {f}")
```

### Skip OCR

```python
print(deal_pdf(input="test.pdf",ocr="pass"))
```

### Doc2x support

```python
from pdfdeal.doc2x import Doc2X

Client = Doc2X()
filelist = gen_folder_list("./test","pdf")
# This is a built-in function for generating the folder under the path of all the pdf, you can give any list of the form of the path of the pdf
Client.pdfdeal(filelist)
```

See [Doc2x Support](./docs/doc2x.md).
