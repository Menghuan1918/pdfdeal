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

[📄Documentation](https://menghuan1918.github.io/pdfdeal-docs/)

🗺️ ENGLISH | [简体中文](README_CN.md)

</div>

Handle PDF more easily and simply, utilizing Doc2X's powerful document conversion capabilities for retained format file conversion/RAG enhancement.

<div align=center>
<img src="https://github.com/user-attachments/assets/f008bed2-9314-4e45-a5cb-08b667b4b204" width="500px">
</div>

## Introduction

### Doc2X Support

[Doc2X](https://doc2x.com/) is a new universal document OCR tool that can convert images or PDF files into Markdown/LaTeX text with formulas and text formatting. It performs better than similar tools in most scenarios. `pdfdeal` provides abstract packaged classes to use Doc2X for requests.

### Processing PDFs

Use various OCR or PDF recognition tools to identify images and add them to the original text. You can set the output format to use PDF, which will ensure that the recognized text retains the same page numbers as the original in the new PDF. It also offers various practical file processing tools.

After conversion and pre-processing of PDF using Doc2X, you can achieve better recognition rates when used with knowledge base applications such as [graphrag](https://github.com/microsoft/graphrag), [Dify](https://github.com/langgenius/dify), and [FastGPT](https://github.com/labring/FastGPT).

## Cases

### graphrag

See [how to use it with graphrag](https://menghuan1918.github.io/pdfdeal-docs/demo/graphrag.html), [its not supported to recognize pdf](https://github.com/microsoft/graphrag), but you can use the CLI tool `doc2x` to convert it to a txt document for use.

<div align=center>
<img src="https://github.com/user-attachments/assets/f9e8408b-9a4b-42b9-9aee-0d1229065a91" width="600px">
</div>

### Fastgpt/Dify or other RAG system

Or for knowledge base applications, you can use `pdfdeal`'s built-in variety of enhancements to documents, such as uploading images to remote storage services, adding breaks by paragraph, etc. See [Integration with RAG applications](https://menghuan1918.github.io/pdfdeal-docs/demo/RAG_pre.html).

<img src="https://github.com/user-attachments/assets/034d3eb0-d77e-4f7d-a707-9be08a092a9a" width="450px">
<img src="https://github.com/user-attachments/assets/6078e585-7c06-485f-bcd3-9fac84eb7301" width="450px">

### RAG system plug-in integration

- You can find Doc2X plugin in [FastGPT 4.8.9 and later](https://github.com/labring/FastGPT/releases/tag/v4.8.9) which supports PDF/image conversion.

## Documentation

For details, please refer to the [documentation](https://menghuan1918.github.io/pdfdeal-docs/)

Or check out the [documentation repository pdfdeal-docs](https://github.com/Menghuan1918/pdfdeal-docs).

## Quick Start

For details, please refer to the [documentation](https://menghuan1918.github.io/pdfdeal-docs/)

### Installation

Install from PyPI:

```bash
pip install --upgrade pdfdeal

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

See the online documentation for details.
