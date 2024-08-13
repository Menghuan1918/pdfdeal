<div align=center>
<h1 aligh="center">
<img src="https://github.com/Menghuan1918/pdfdeal/assets/122662527/837cfd7f-4546-4b44-a199-d826d78784fc" width="45">  pdfdeal
</h1>

**更好的RAG效果！**

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

</div>

更轻松简单地处理 PDF，提取可读文本，用 OCR 识别图像文本并清理格式,使其更适合构建知识库。


## 简介
### 最近更新
文档更新:[如何与graphrag结合使用](https://menghuan1918.github.io/pdfdeal-docs/zh/demo/graphrag.html)

### Doc2X 支持
![doc2x](https://github.com/user-attachments/assets/3ebd3440-9b07-4be1-be2e-fc764d9d07f8)

[Doc2X](https://doc2x.com/)是一款新型的通用的文档OCR工具，可将图像或pdf文件转换为带有公式和文本格式的Markdown/LaTeX文本，并且效果在大部分场景下优于同类型工具。`pdfdeal`提供了抽象包装好的类以使用Doc2X发起请求。

### 对PDF进行处理
使用多种OCR或者PDF识别工具来识别图像并将其添加到原始文本中。可以设置输出格式使用 pdf 格式，这将确保识别后的文本在新 PDF 中的页数与原始文本相同。同时提供了多种实用的文件处理工具。

对 PDF 进行处理后与知识库应用程序（例如[graphrag](https://github.com/microsoft/graphrag)，[Dify](https://github.com/langgenius/dify)，[FastGPT](https://github.com/labring/FastGPT)），可以达到更好的识别率。

建议使用Doc2X以达到最佳效果。

![main](https://github.com/Menghuan1918/pdfdeal/assets/122662527/b92335eb-bda0-4a61-b890-e864cebc5f67)

## 案例

例如[graphrag](https://github.com/microsoft/graphrag)不支持识别pdf，你可以使用`doc2x`将其转换为txt文档进行使用。

![rag](https://github.com/user-attachments/assets/f9e8408b-9a4b-42b9-9aee-0d1229065a91)

或者对于知识库应用，你也可以使用`pdfdeal`对文档进行增强，以下是在Dify中原始PDF/OCR增强/Doc2X处理后的效果：

![222](https://github.com/Menghuan1918/pdfdeal/assets/122662527/457036e8-9d78-458a-8a48-763bd33e95f9)

## 文档

你可以[在此处](https://github.com/users/Menghuan1918/projects/3)查看正在开发的新功能！

详细请查看[在线文档](https://menghuan1918.github.io/pdfdeal-docs/zh/)。

或者你也可以查看文档的开源[储存库 pdfdeal-docs](https://github.com/Menghuan1918/pdfdeal-docs)。

## 快速开始

### 安装
从 PyPI 安装：

```bash
pip install --upgrade pdfdeal
```

### 使用pytesseract作为OCR引擎

使用 “pytesseract ”时，请确保首先安装了 [tesseract](https://github.com/tesseract-ocr/tesseract)：

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

### 使用Doc2X作为PDF处理工具

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
