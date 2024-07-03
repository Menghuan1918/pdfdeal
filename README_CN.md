<div align=center>
<h1 aligh="center">
pdfdeal
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

</div>


更轻松简单地处理 PDF，提取可读文本，用 OCR 识别图像文本并清理格式,使其更适合构建知识库。

## 最近更新

你可以[在此处](https://github.com/users/Menghuan1918/projects/3)查看正在开发的新功能！如果直接使用Doc2X进行转换请参阅[Doc2x支持](./docs/doc2x_cn.md)。

### V0.1.3

#### ✨ 新特性

- 新增功能：将 Markdown 文件中的所有远程图片替换为本地图片
- 重构的`pdfdeal`函数，现在支持批量输入文件了

#### 🐛 Bug 修复

- 重整本地OCR文件处理函数的输出格式
- `pdfdeal`某些情况下无法输出md文件的问题
- 删除版本0.0.x中使用的`Doc2x`

#### 🚀 其他

- 文档将会在下个版本重制

### V0.1.x版本

请参阅[0.1.2更新](https://github.com/Menghuan1918/pdfdeal/releases/tag/v0.1.2)，[0.1.1更新](https://github.com/Menghuan1918/pdfdeal/releases/tag/v0.1.1)以及[0.1.0更新](https://github.com/Menghuan1918/pdfdeal/releases/tag/v0.1.0)。

## 简介

使用 [easyocr](https://github.com/JaidedAI/EasyOCR) 或 [Doc2x](./docs/doc2x_cn.md)来识别图像并将其添加到原始文本中。可以设置输出格式使用 pdf 格式，这将确保文本在新 PDF 中的页数与原始文本相同。对 PDF 进行处理后与知识库应用程序（如[Dify](https://github.com/langgenius/dify)、[FastGPT](https://github.com/labring/FastGPT)），理论上可以达到更好的识别率。

![111](https://github.com/Menghuan1918/pdfdeal/assets/122662527/58155389-f846-41fd-9314-1cd86282e66a)

![222](https://github.com/Menghuan1918/pdfdeal/assets/122662527/457036e8-9d78-458a-8a48-763bd33e95f9)

## 对Doc2x的支持

新增对Doc2x的支持，目前其每日有500页的**免费**使用额度，其对表格/公式的识别效果卓越。

你也可以**单独使用**Doc2x的支持模块直接将pdf转换为markdown/latex/docx等格式，就像下面这样。详细请参阅[Doc2x支持](./docs/doc2x_cn.md)。


```python
from pdfdeal.doc2x import Doc2X

Client = Doc2X()
filelist = gen_folder_list("./test","pdf")
# This is a built-in function for generating the folder under the path of all the pdf, you can give any list of the form of the path of the pdf
Client.pdfdeal(filelist)
```

## 使用方法
[示范代码](https://github.com/Menghuan1918/pdfdeal/blob/main/README_CN.md#%E5%B0%86%E6%96%87%E4%BB%B6%E5%A4%B9%E4%B8%AD%E7%9A%84%E6%89%80%E6%9C%89%E6%96%87%E4%BB%B6%E8%BF%9B%E8%A1%8C%E5%A4%84%E7%90%86%E5%B9%B6%E6%94%BE%E7%BD%AE%E5%9C%A8output%E6%96%87%E4%BB%B6%E5%A4%B9%E4%B8%AD)

### 安装
从 PyPI 安装：

```bash
pip install 'pdfdeal[easyocr]'
```

使用 “pytesseract ”时，请确保首先安装了 [tesseract](https://github.com/tesseract-ocr/tesseract)：

```bash
pip install 'pdfdeal[pytesseract]'
```

使用自己的自定义OCR功能,Doc2x或跳过OCR：

```bash
pip install pdfdeal
```

从源码安装：

```bash
pip install 'pdfdeal[all] @ git+https://github.com/Menghuan1918/pdfdeal.git'
```

### 参数
通过 `from pdfdeal import deal_pdf` 导入函数。以下是该函数接受的参数说明：

- **input**: `str`或`list`
  - 描述：要处理的 PDF 文件的本地路径。
  - 示例： `["1.pdf","2.pdf"]`

- **output**: `str`, 可选，默认值：`"texts"`
  - 描述：指定所需的输出类型。选项包括：
    - `"texts"`：提取的文本作为字符串列表，每页一个字符串。
    - `"md"`：Markdown 格式的文本。
    - `"pdf"`：包含提取文本的新 PDF 文件。
  - 示例：`"md"`

- **ocr**: `function`, 可选，默认值：`None`
  - 描述：自定义 OCR（光学字符识别）函数。如果未提供，将使用默认的 OCR 函数。使用字符串 "pytesseract" 以使用 pytesseract，使用字符串 "pass" 以跳过 OCR。
  - 示例自定义 OCR 函数：`custom_ocr_function`，输入为：`(path, language=["ch_sim", "en"], GPU=False)`，返回一个 `string`,`bool`

- **language**: `list`, 可选，默认值：`["ch_sim", "en"]`
  - 描述：OCR 使用的语言列表。默认语言是简体中文（`"ch_sim"`）和英语（`"en"`）。pytesseract 使用 `["eng"]`。
  - 示例：`["en", "fr"]`

- **GPU**: `bool`, 可选，默认值：`False`
  - 描述：一个布尔标志，指示是否使用 GPU 进行 OCR 处理。如果设置为 `True`，将使用 GPU。
  - 示例：`True`

- **path**: `str`, 可选，默认值：`None`
  - 描述：输出文件保存的目录路径。仅在 `output` 类型为 `"md"` 或 `"pdf"` 时使用此参数。
  - 示例：`"/path/to/save/output"`

### 将文件夹中的所有文件进行处理并放置在`Output`文件夹中

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

### 获得处理后PDF文件按页分割的文本列表

```python
from pdfdeal import deal_pdf
Text = deal_pdf(input="test.pdf", output="texts", language=["en"], GPU=True)
for text in Text:
  print(text)
```

### 使用pytesseract进行OCR识别

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

### 跳过OCR环节

```python
print(deal_pdf(input="test.pdf",ocr="pass"))
```

### 使用Doc2x


```python
from pdfdeal.doc2x import Doc2X

Client = Doc2X()
filelist = gen_folder_list("./test","pdf")
# This is a built-in function for generating the folder under the path of all the pdf, you can give any list of the form of the path of the pdf
Client.pdfdeal(filelist)
```

请参阅[Doc2x支持](./docs/doc2x_cn.md)。
