> [!IMPORTANT]
> `0.0.X`版本的方法已经弃用，其将会在未来删除，请尽快迁移至新的实现。你可以在[此处](./doc2x_old_cn.md)查看旧版本的文档。
>
> 其大部分接口并没变动，你可以尝试直接将`from pdfdeal.doc2x import Doc2x`改为`from pdfdeal.doc2x import Doc2X`。

## 安装

`pdfdeal`支持python3.9以及更高版本，使用`pip`进行安装：

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
Client = Doc2X(apikey=api,rpm=25,thread=5,maxretry=10)
```

其中：
- `rpm`代表每分钟请求数，默认为3。
- `thread`代表最大同时请求数，默认为1。
- `maxretry`代表遇到rpm限制时的最大重试次数，默认为5。

> [!NOTE]
> 对于个人使用，不建议修改`rpm`和`thread`，以免触发频率限制。

## 发起请求

请首先通过上述方法配置好API密匙。

### 图片处理

`Client.pic2file`

接收一个或以多个(列表)的图片路径，返回处理后的输出文件路径。

输入参数：
- `image_file`：图片文件路径或图片文件路径列表
- `output_path`：`str`，可选，输出文件夹路径，默认为`"./Output"`
- `output_format`：`str`，可选，输出格式，接受`texts`、`md`、`md_dollar`、`latex`，默认为`md_dollar`。其中选择`texts`时直接返回文本，并不会保存到文件。
- `img_correction`：`bool`，可选，是否进行图片矫正，默认为`True`
- `equation`：`bool`，可选，使用纯公式输出模式，默认为`False`
- `convert`：`bool`，可选，是否将`[`转换为`$`，`[[`转换为`$$`，默认为`False`，仅在`output_format`为`texts`时有效

示例：按照rpm限制处理多个图片

```python
from pdfdeal.doc2x import Doc2X
from pdfdeal.file_tools import gen_folder_list
Client = Doc2X()
filelist = gen_folder_list("./test","img")
# 这是内置的一个函数，用于生成文件夹下所有图片的路径，你可以给定任意list形式的图片路径
finished_list =  Client.pic2file(filelist,output_format="docx")
print(*finished_list, sep='\n')
```

示例：处理单个图片，获得公式格式为`$公式$`形式的内容

```python
from pdfdeal.doc2x import Doc2X
Client = Doc2X()
text = Client.pic2file("./test.png", output_format="texts", convert=True)
print(*text, sep='\n')
```

### PDF处理
`Client.pdf2file`

接收一个或以多个(列表)的pdf路径，返回处理后的输出文件路径。

输入参数：
- `pdf_file`：pdf文件路径或pdf文件路径列表
- `output_path`：`str`，可选，输出文件夹路径，默认为`"./Output"`
- `output_format`：`str`，可选，输出格式，接受`texts`、`md`、`md_dollar`、`latex`、`docx`，默认为`md_dollar`。其中选择`texts`时直接返回文本，并不会保存到文件。
- `ocr`：`bool`，可选，是否使用OCR，默认为`True`
- `convert`：`bool`，可选，是否将`[`转换为`$`，`[[`转换为`$$`，默认为`False`，仅在`output_format`为`texts`时有效

示例：将单个pdf转换为latex文件

```python
from pdfdeal.doc2x import Doc2X
Client = Doc2X()
filepath = Client.pdf2file("test.pdf",output_format ="latex")
print(filepath)
# 返回值为输出文件路径
```

示例：将多个pdf转换为docx文件

```python
from pdfdeal.doc2x import Doc2X
from pdfdeal.file_tools import gen_folder_list
Client = Doc2X()
filelist = gen_folder_list("./test","pdf")
# 这是内置的一个函数，用于生成文件夹下所有pdf的路径，你可以给定任意list形式的pdf路径
finished_list =  Client.pdf2file(filelist,output_format="docx")
print(*finished_list, sep='\n')
```

### 获得剩余请求次数
`Client.get_limit`

返回API剩余请求次数。

```python
from pdfdeal.doc2x import Doc2X
Client = Doc2X()
print(f"Pages remaining: {Client.get_limit()}")
```

### 用于RAG知识库预处理

`Client.pdfdeal`

接收一个或以多个(列表)的pdf路径，返回处理后的输出文件路径。

接受参数：
- `input`：pdf文件路径或pdf文件路径列表
- `output`：`str`，可选，输出格式，接受`pdf`、`md`，默认为`pdf`
- `path`：`str`，可选，输出文件夹路径，默认为`"./Output"`
- `convert`：`bool`，可选，是否将`[`转换为`$`，`[[`转换为`$$`，默认为`True`

```python
from pdfdeal.doc2x import Doc2X

Client = Doc2X()
filelist = gen_folder_list("./test","pdf")
# 这是内置的一个函数，用于生成文件夹下所有pdf的路径，你可以给定任意list形式的pdf路径
Client.pdfdeal(filelist)
```

### 翻译pdf文档
获得翻译后的文本和位置信息。

```python
from pdfdeal.doc2x import Doc2X

Client = Doc2X()
translate = Client.pdf_translate("test.pdf")
for text in translate:
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