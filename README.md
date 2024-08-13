<div align=center>
<h1 aligh="center">
<img src="https://github.com/Menghuan1918/pdfdeal/assets/122662527/837cfd7f-4546-4b44-a199-d826d78784fc" width="45">  pdfdeal
</h1>

**Better RAG Effect!**

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

[![Downloads](https://static.pepy.tech/badge/pdfdeal)](https://pepy.tech/project/pdfdeal) ![GitHub License](https://img.shields.io/github/license/Menghuan1918/pdfdeal) ![PyPI - Version](https://img.shields.io/pypi/v/pdfdeal) ![GitHub Repo stars](https://img.shields.io/github/stars/Menghuan1918/pdfdeal)

<br>


🗺️ ENGLISH | [简体中文](README_CN.md)

</div>

Easily handle PDFs, extract readable text, recognize image text with OCR and clean up formatting to make it more suitable for building knowledge bases.

## Introduction
### What's NEW
Added documentation tutorial on how to [integrate with graphrag](https://menghuan1918.github.io/pdfdeal-docs/demo/graphrag.html)

### Doc2X Support
![doc2x](https://github.com/user-attachments/assets/3ebd3440-9b07-4be1-be2e-fc764d9d07f8)

[Doc2X](https://doc2x.com/) is a new universal document OCR tool that can convert images or PDF files into Markdown/LaTeX text with formulas and text formatting. It performs better than similar tools in most scenarios. `pdfdeal` provides abstract packaged classes to use Doc2X for requests.

### Processing PDFs
Use various OCR or PDF recognition tools to identify images and add them to the original text. You can set the output format to use PDF, which will ensure that the recognized text retains the same page numbers as the original in the new PDF. It also offers various practical file processing tools.

After processing PDFs, you can achieve better recognition rates when used with knowledge base applications such as [graphrag](https://github.com/microsoft/graphrag), [Dify](https://github.com/langgenius/dify), and [FastGPT](https://github.com/labring/FastGPT).

It is recommended to use Doc2X for the best results.

![main](https://github.com/Menghuan1918/pdfdeal/assets/122662527/b92335eb-bda0-4a61-b890-e864cebc5f67)

## Cases

For example, if [graphrag](https://github.com/microsoft/graphrag) does not support recognizing PDFs, you can use `doc2x` to convert it into txt documents for use.

![rag](https://github.com/user-attachments/assets/f9e8408b-9a4b-42b9-9aee-0d1229065a91)


Or for knowledge base applications, you can also use `pdfdeal` to enhance documents. Below are the effects of original PDF/OCR enhancement/Doc2X processing in Dify:

![222](https://github.com/Menghuan1918/pdfdeal/assets/122662527/457036e8-9d78-458a-8a48-763bd33e95f9)

## Documentation

You can view new features under development [here](https://github.com/users/Menghuan1918/projects/3)!

For details, please refer to the [documentation](https://menghuan1918.github.io/pdfdeal-docs/) 

Or check out the [documentation repository pdfdeal-docs](https://github.com/Menghuan1918/pdfdeal-docs).

## Quick Start

For details, please refer to the [documentation](https://menghuan1918.github.io/pdfdeal-docs/) 

### Installation
Install from PyPI:

```bash
pip install --upgrade pdfdeal

```

### Using pytesseract as an OCR engine

When using "pytesseract", make sure that [tesseract](https://github.com/tesseract-ocr/tesseract) is installed first:

```bash
pip install 'pdfdeal[pytesseract]'
```

```python
from pdfdeal import deal_pdf, get_files

files, rename = get_files("tests/pdf", "pdf", "md")
output_path, failed, flag = deal_pdf(
    pdf_file=files,
    output_format="md",
    ocr="pytesseract",
    language=["eng"],
    output_path="Output",
    output_names=rename,
)
for f in output_path:
    print(f"Save processed file to {f}")
```

### Using Doc2X as PDF deal tool

```python
from pdfdeal import Doc2X
from pdfdeal import get_files

client = Doc2X()
file_list, rename = get_files(path="tests/pdf", mode="pdf", out="pdf")
success, failed, flag = client.pdfdeal(
    pdf_file=file_list,
    output_path="./Output/test/multiple/pdfdeal",
    output_names=rename,
)
print(success)
print(failed)
print(flag)
```
