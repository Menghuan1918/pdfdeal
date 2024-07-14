### 最近更新以及是否有接口变动

请参阅[更新](https://github.com/Menghuan1918/pdfdeal/releases)

## 安装

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

本项目支持 python 3.8-3.12 版本，并已使用GitHub Action在Windows/Linux/MacOS 系统中进行测试，使用`pip`进行安装：

```bash
pip install --upgrade pdfdeal
```

## 配置API密匙

对于个人使用，请登录[https://doc2x.noedgeai.com](https://doc2x.noedgeai.com/)，点击`个人信息`，复制其中的身份令牌作为你的API密匙。

### 使用环境变量(推荐)

运行以下代码以导入你的API密匙：

```python
from pdfdeal.doc2x import Doc2X
Client = Doc2X()
```

#### MacOS/Linux

请使用以下命令为当前终端设置环境变量：

```bash
export DOC2X_APIKEY = "Your API Key"
```

你也可以将以上命令添加到`~/.zshrc`或`~/.bashrc`以持久化环境变量。

#### Windows

请使用以下命令为当前终端设置环境变量：

```PowerShell
setx DOC2X_APIKEY "Your API Key"
```

你可以将其添加至`此电脑` -> `属性` -> `高级系统设置` -> `环境变量` -> `系统变量`中以持久化。

### 为项目单独设置API密匙

若你希望 API 密钥仅对单个项目可见，可创建一个包含你的API密钥的本地`.env`文件。以下是一个`.env`文件的示范：

```
DOC2X_APIKEY = "Your API Key"
```

导入的代码与使用环境变量的方法相同。

### 指定API密匙(不推荐)

如果你想指定你的API密匙，你可以通过以下代码导入：

```python
from pdfdeal.doc2x import Doc2X
Client = Doc2X(apikey="Your API key")
```

## 全局设置

你还可以配置密匙时同时配置请求的全局设置：

```python
from pdfdeal.doc2x import Doc2X
Client = Doc2X(apikey=api)
```

其中：
- `rpm`代表每分钟请求数，会自动进行设置

> [!NOTE]
> 除非你确信你需要修改请求频率，请不要修改`rpm`

## 发起请求

请首先通过上述方法配置好API密匙。

> [!NOTE]
> 关于`version`参数：
>
> 其值为`v2`时会返回三个值：`list1`:成功处理的文件列表、`list2`:处理失败的文件列表和`bool`:处理状态。
>
> 其中`list1`和`list2`的长度相同。
>
> 对于`list1`中的每个元素，如果处理成功，其值为处理后的文件路径，如果处理失败，其值为空字符串。
>
> 对于`list2`中的每个元素，其值为一个字典，包含`error`和`path`两个键，`error`为错误信息，`path`为处理失败的文件路径，当对应的文件处理成功时，两个键的值为空字符串。
>
> `bool`为`True`时代表至少有一个文件处理失败，为`False`时代表全部处理成功，详细信息请查看示例。


### 图片处理

`Client.pic2file`

接收一个或以多个(列表)的图片路径，返回处理后的输出文件路径。

输入参数：
- `image_file`：图片文件路径或图片文件路径列表
- `output_path`：`str`，可选，输出文件夹路径，默认为`"./Output"`
- `output_names` : `list`，可选，输出文件名列表，长度必须与`image_file`相同，用于指定输出文件的名称
- `output_format`：`str`，可选，输出格式，接受`texts`、`md`、`md_dollar`、`latex`，默认为`md_dollar`。其中选择`texts`时直接返回文本，并不会保存到文件
- `img_correction`：`bool`，可选，是否进行图片矫正，默认为`True`
- `equation`：`bool`，可选，使用纯公式输出模式，默认为`False`
- `convert`：`bool`，可选，是否将`[`转换为`$`，`[[`转换为`$$`，默认为`False`，仅在`output_format`为`texts`时有效
- `version`：`str`，可选，返回格式，接受`v1`、`v2`，当为`v2`时会返回更多信息，默认为`v1`

#### 示例：按照rpm限制处理多个图片，以`v2`格式返回

```python
from pdfdeal.doc2x import Doc2X
client = Doc2X()
file_list = ["tests/image/sample_bad.png", "tests/image/sample.png"]
# 如果你不需要使用重命名功能，可以使用 from pdfdeal.file_tools import gen_folder_list 函数从文件夹生成文件列表(因为其排序不是固定的)
# 例如：
# file_list = gen_folder_list("./tests/image","img")
success, failed, flag = client.pdf2file(
    pdf_file=file_list,
    output_path="./Output/test/multiple/pdf2file",
    output_names=["sample1.docx", "sample2.docx"],
    output_format="docx",
    version="v2",
)
print(success)
print(failed)
print(flag)
```

当第一个文件处理失败，第二个文件处理成功时，其示例输出：

```python
['', './Output/test/multiple/pdf2file/sample2.docx']
[{'error': 'Error Upload file error! 500:{"code":"service unavailable","msg":"read file error"}', 'path': 'tests/pdf/sample_bad.pdf'}, {'error': '', 'path': ''}]
True
```

#### 示例：处理单个图片，在纯公式模式下，获得公式格式为`$公式$`形式的内容

```python
from pdfdeal.doc2x import Doc2X
client = Doc2X()
text = client.pic2file(
    "tests/image/sample.png", output_format="texts", equation=True, convert=True
)
print(text)
```

示例输出：
```python
[['$$\\text{Test}$$']]
```

### PDF处理
`Client.pdf2file`

接收一个或以多个(列表)的pdf路径，返回处理后的输出文件路径。

输入参数：
- `pdf_file`：pdf文件路径或pdf文件路径列表
- `output_path`：`str`，可选，输出文件夹路径，默认为`"./Output"`
- `output_names` : `list`，可选，输出文件名列表，长度必须与`pdf_file`相同，用于指定输出文件的名称
- `output_format`：`str`，可选，输出格式，接受`texts`、`md`、`md_dollar`、`latex`、`docx`，默认为`md_dollar`。其中选择`texts`时直接返回文本，并不会保存到文件。
- `ocr`：`bool`，可选，是否使用OCR，默认为`True`
- `convert`：`bool`，可选，是否将`[`转换为`$`，`[[`转换为`$$`，默认为`False`，仅在`output_format`为`texts`时有效
- `version`：`str`，可选，返回格式，接受`v1`、`v2`，当为`v2`时会返回更多信息，默认为`v1`

#### 示例：将单个pdf转换为latex文件并指定输出文件名

```python
from pdfdeal.doc2x import Doc2X

client = Doc2X()
filepath = client.pdf2file(
    "tests/pdf/sample.pdf", output_names=["Test.zip"], output_format="latex"
)
print(filepath)
```

当成功时示例输出：

```python
['./Output/Test.zip']
```

当处理失败时示例输出：

```python
['']
```

#### 示例：将一个文件夹中的pdf转换为docx文件，并保持原有文件结构

```python
from pdfdeal.doc2x import Doc2X
from pdfdeal import get_files
client = Doc2X()
file_list, rename_list = get_files(
    path="./tests/pdf", mode="pdf", out="docx"
)
success, failed, flag = client.pdf2file(
    pdf_file=file_list,
    output_path="./Output/newfolder",
    output_names=rename_list,
    output_format="docx",
    version="v2",
)
print(success)
print(failed)
print(flag)
```

其中`./tests/pdf`的文件结构为：
```bash
pdf
├── sample_bad.pdf
├── sample.pdf
└── test
    └── sampleB.pdf
```

> 注意`sample_bad.pdf`是一个用于测试异常处理的损坏的文件，处理失败是正常的。

预期输出：

```python
PDF Progress: 2/3 files successfully processed.
-----
Failed deal with ./tests/pdf/sample_bad.pdf with error:
Error Upload file error! 400:{"code":"invalid request","msg":"bad params"}
-----
['./Output/newfolder/sample.docx', '', './Output/newfolder/test/sampleB.docx']
[{'error': '', 'path': ''}, {'error': 'Error Upload file error! 400:{"code":"invalid request","msg":"bad params"}', 'path': './tests/pdf/sample_bad.pdf'}, {'error': '', 'path': ''}]
True
```

以及处理后的文件结构：
```bash
Output
└── newfolder
    ├── sample.docx
    └── test
        └── sampleB.docx
```

### 获得剩余请求次数
`Client.get_limit`

返回API剩余请求次数。

```python
from pdfdeal.doc2x import Doc2X
Client = Doc2X()
print(f"Pages remaining: {Client.get_limit()}")
```

示例输出：

```python
Pages remaining: 123
```

### 用于RAG知识库预处理

`Client.pdfdeal`

接收一个或以多个(列表)的pdf路径，返回处理后的输出文件路径。

接受参数：
- `input`：pdf文件路径或pdf文件路径列表
- `output`：`str`，可选，输出格式，接受`pdf`、`md`，默认为`pdf`
- `path`：`str`，可选，输出文件夹路径，默认为`"./Output"`
- `convert`：`bool`，可选，是否将`[`转换为`$`，`[[`转换为`$$`，默认为`True`
- `version`：`str`，可选，返回格式，接受`v1`、`v2`，当为`v2`时会返回更多信息，默认为`v1`

```python
from pdfdeal.doc2x import Doc2X
from pdfdeal.file_tools import gen_folder_list

client = Doc2X()
file_list = gen_folder_list("tests/pdf", "pdf")
success, failed, flag = client.pdfdeal(
    input=file_list,
    path="./Output/test/multiple/pdfdeal",
    version="v2",
)
print(success)
print(failed)
print(flag)
```

当第一个文件处理**失败**，第二个文件处理**成功**时，其示例输出：

```python
['', './Output/test/multiple/pdfdeal/sample.pdf']
[{'error': Exception('Upload file error! 500:{"code":"service unavailable","msg":"read file error"}'), 'path': 'tests/pdf/sample_bad.pdf'}, {'error': '', 'path': ''}]
True
```

### 翻译pdf文档
获得翻译后的文本和位置信息。

```python
from pdfdeal.doc2x import Doc2X

Client = Doc2X()
translate = Client.pdf_translate("test.pdf")
for text in translate[0]:
    print(text["texts"])
    print(text["location"])
```

其中`text["texts"]`是翻译后的文本，为一个列表，空字符串代表当前文本块没有翻译(例如：是表格文本)，示例输出：

```
['翻译之后']
```


`text["location"]`是文本的位置信息，为一个列表，与`text["texts"]`对应，示例输出：

```
[{'raw_text': 'xxx', 'page_idx': 0, 'page_width': 1581, 'page_height': 2047, 'x': 178, 'y': 184}]
```