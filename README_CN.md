<div align=center>
<h1 aligh="center">
<img src="https://github.com/Menghuan1918/pdfdeal/assets/122662527/837cfd7f-4546-4b44-a199-d826d78784fc" width="45">  pdfdeal
</h1>
<a href="https://github.com/Menghuan1918/pdfdeal/actions/workflows/python-test.yml">
  <img src="https://github.com/Menghuan1918/pdfdeal/actions/workflows/python-test.yml/badge.svg" 
  alt="Package Testing on Python 3.8-3.13 on Win/Linux/macOS">
</a>
<br>

<br>

[![Downloads](https://static.pepy.tech/badge/pdfdeal)](https://pepy.tech/project/pdfdeal) ![GitHub License](https://img.shields.io/github/license/Menghuan1918/pdfdeal) ![PyPI - Version](https://img.shields.io/pypi/v/pdfdeal) ![GitHub Repo stars](https://img.shields.io/github/stars/Menghuan1918/pdfdeal)

<br>

[📄 在线文档](https://menghuan1918.github.io/pdfdeal-docs/zh/guide/)

<br>

[ENGLISH](README.md) | 🗺️ 简体中文

</div>

更轻松简单地处理 PDF，利用 Doc2X 强大的文档转换能力，进行保留格式文件转换/RAG 增强。

<div align=center>
<img src="https://github.com/user-attachments/assets/3db3c682-84f1-4712-bd70-47422616f393" width="500px">
</div>

## 简介

### Doc2X 支持

[Doc2X](https://doc2x.com/)是一款新型的通用的文档 OCR 工具，可将图像或 pdf 文件转换为带有公式和文本格式的 Markdown/LaTeX 文本，并且效果在大部分场景下优于同类型工具。`pdfdeal`提供了抽象包装好的类以使用 Doc2X 发起请求。

### 对 PDF 进行处理

使用多种 OCR 或者 PDF 识别工具来识别图像并将其添加到原始文本中。可以设置输出格式使用 pdf 格式，这将确保识别后的文本在新 PDF 中的页数与原始文本相同。同时提供了多种实用的文件处理工具。

对 PDF 使用 Doc2X 转换并预处理后，与知识库应用程序（例如[graphrag](https://github.com/microsoft/graphrag)，[Dify](https://github.com/langgenius/dify)，[FastGPT](https://github.com/labring/FastGPT)），可以显著提升召回率。

## 案例

### graphrag

参见[如何与 graphrag 结合使用](https://menghuan1918.github.io/pdfdeal-docs/zh/demo/graphrag.html)，[其不支持识别 pdf](https://github.com/microsoft/graphrag)，但你可以使用 CLI 工具`doc2x`将其转换为 txt 文档进行使用。

<div align=center>
<img src="https://github.com/user-attachments/assets/f9e8408b-9a4b-42b9-9aee-0d1229065a91" width="600px">
</div>

### FastGPT/Dify 或其他 RAG 应用

或者对于知识库应用，你也可以使用`pdfdeal`内置的多种对文档进行增强，例如图片上传到远端储存服务，按段落添加分割符等。请参见[与 RAG 应用集成](https://menghuan1918.github.io/pdfdeal-docs/zh/demo/RAG_pre.html)

<div align=center>
<img src="https://github.com/user-attachments/assets/034d3eb0-d77e-4f7d-a707-9be08a092a9a" width="450px">
<img src="https://github.com/user-attachments/assets/6078e585-7c06-485f-bcd3-9fac84eb7301" width="450px">
</div>

## 文档

详细请查看[在线文档](https://menghuan1918.github.io/pdfdeal-docs/zh/)。

你可以找到在线文档的开源[储存库 pdfdeal-docs](https://github.com/Menghuan1918/pdfdeal-docs)。

## 快速开始

### 安装

使用 pip 安装：

```bash
pip install --upgrade pdfdeal
```

如你还需要使用[文本预处理功能](https://menghuan1918.github.io/pdfdeal-docs/zh/guide/Tools/)：

```bash
pip install --upgrade "pdfdeal[rag]"
```

### 使用 Doc2X PDF API 处理指定文件夹中所有 PDF 文件

```python
from pdfdeal import Doc2X

client = Doc2X(apikey="Your API key",debug=True)
success, failed, flag = client.pdf2file(
    pdf_file="tests/pdf",
    output_path="./Output",
    output_format="docx",
)
print(success)
print(failed)
print(flag)
```

### 使用 Doc2X PDF API 处理指定的 PDF 文件并指定导出的文件名

```python
from pdfdeal import Doc2X

client = Doc2X(apikey="Your API key",debug=True)
success, failed, flag = client.pdf2file(
    pdf_file="tests/pdf/sample.pdf",
    output_path="./Output/test/single/pdf2file",
    output_names=["NAME.zip"],
    output_format="md_dollar",
)
print(success)
print(failed)
print(flag)
```

更多详细请参见在线文档。
