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

[📄在线文档](https://menghuan1918.github.io/pdfdeal-docs/zh/)

[ENGLISH]((README.md)) | 🗺️简体中文

</div>

更轻松简单地处理 PDF，利用Doc2X强大的文档转换能力，进行保留格式文件转换/RAG增强。

<div align=center>
<img src="https://github.com/user-attachments/assets/f008bed2-9314-4e45-a5cb-08b667b4b204" width="500px">
</div>

## 简介

### Doc2X 支持
[Doc2X](https://doc2x.com/)是一款新型的通用的文档OCR工具，可将图像或pdf文件转换为带有公式和文本格式的Markdown/LaTeX文本，并且效果在大部分场景下优于同类型工具。`pdfdeal`提供了抽象包装好的类以使用Doc2X发起请求。

### 对PDF进行处理

使用多种OCR或者PDF识别工具来识别图像并将其添加到原始文本中。可以设置输出格式使用 pdf 格式，这将确保识别后的文本在新 PDF 中的页数与原始文本相同。同时提供了多种实用的文件处理工具。

对 PDF 使用Doc2X转换并预处理后，与知识库应用程序（例如[graphrag](https://github.com/microsoft/graphrag)，[Dify](https://github.com/langgenius/dify)，[FastGPT](https://github.com/labring/FastGPT)），可以显著提升召回率。


## 案例

### graphrag

参见[如何与graphrag结合使用](https://menghuan1918.github.io/pdfdeal-docs/zh/demo/graphrag.html)，[其不支持识别pdf](https://github.com/microsoft/graphrag)，但你可以使用CLI工具`doc2x`将其转换为txt文档进行使用。

<div align=center>
<img src="https://github.com/user-attachments/assets/f9e8408b-9a4b-42b9-9aee-0d1229065a91" width="600px">
</div>

### FastGPT/Dify 或其他RAG应用

或者对于知识库应用，你也可以使用`pdfdeal`内置的多种对文档进行增强，例如图片上传到远端储存服务，按段落添加分割符等。请参见[与RAG应用集成](https://menghuan1918.github.io/pdfdeal-docs/zh/demo/RAG_pre.html)

<img src="https://github.com/user-attachments/assets/034d3eb0-d77e-4f7d-a707-9be08a092a9a" width="450px">
<img src="https://github.com/user-attachments/assets/6078e585-7c06-485f-bcd3-9fac84eb7301" width="450px">

### RAG系统插件集成

- 你可以在[FastGPT 4.8.9以及更高版本](https://github.com/labring/FastGPT/releases/tag/v4.8.9)的插件中找到Doc2X插件，其支持PDF/图片转换。

- 你可以在[此处](https://www.coze.cn/store/plugin/7398010704374153253)找到扣子的Doc2X插件，其支持PDF转换。

## 文档

详细请查看[在线文档](https://menghuan1918.github.io/pdfdeal-docs/zh/)。

你可以找到在线文档的开源[储存库 pdfdeal-docs](https://github.com/Menghuan1918/pdfdeal-docs)。

## 快速开始

### 安装
从 PyPI 安装：

```bash
pip install --upgrade pdfdeal
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

详细请参见在线文档。
