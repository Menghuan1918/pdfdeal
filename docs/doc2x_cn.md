# 安装

```bash
pip install pdfdeal
```

你可以在[https://doc2x.noedgeai.com/](https://doc2x.noedgeai.com/)申请个人身份令牌

> 当然我肯定推荐你使用我的邀请链接进行注册：[https://doc2x.noedgeai.com/login?invite_code=4AREZ6](https://doc2x.noedgeai.com/login?invite_code=4AREZ6)

![图片](https://github.com/Menghuan1918/pdfdeal/assets/122662527/0b41b142-8210-4009-9ece-ce6f7bf2591a)

# 基本使用

## PDF转文本/MD/Latex

```python
from pdfdeal.doc2x import Doc2x

Client = Doc2x(api_key=your_api)

Client.pdf2file(pdf_file="./ppt/test.pdf", output_path="./output", output_format="md_dollar", ocr=True)
```

其中`output_format`接受'text'，"md", "md_dollar", "latex", "docx"。"md"和"md_dollar"的区别在于公式表示是否使用“$”号，"text"代表直接返回文本而不保存。

## 图片转文本/MD/Latex

```python
from pdfdeal.doc2x import Doc2x

Client = Doc2x(api_key=your_api)

Client.pic2file(image_file="image.png", output_path="./output", output_format="docx", equation=True)
```

其中`output_format`接受'text'，"md", "md_dollar", "latex", "docx"。"md"和"md_dollar"的区别在于公式表示是否使用“$”号，"text"代表直接返回文本而不保存。

## 保留原有页数的转换
这种方法会保留文本以及图片中文本的原有页数。即处理后的pdf每一页的内容就是源文件对应页数的内容。

```python
from pdfdeal.doc2x import Doc2x
Client = Doc2x(api_key=your_api)
file_path = "./test.pdf"
Client.pdfdeal(input=file_path, output="pdf", path="./Output", convert=True)
```

## 作为pdfdeal的OCR引擎
推荐使用上面的方法`保留原有页数的转换`而不是将doc2x作为OCR引擎。

```python
import os
from pdfdeal import deal_pdf
from pdfdeal.doc2x import Doc2x

Client = Doc2x(api_key=your_api)

for root, dirs, files in os.walk("./ppt"):
    for file in files:
        file_path = os.path.join(root, file)
        deal_pdf(input=file_path, output="pdf", ocr=Client.OCR, path="./output")
        print(f"Deal with {file_path} successfully!")
```

## 获得Doc2X的翻译内容
在翻译模式下，`async_uuid2file`会返回三个list，其分别是：
`Translated_texts`：翻译后的文本块
`texts`：原始文本块
`Text_location`：其内容为`{page_idx","page_width","page_height","x","y"}`，每个文本块的具体位置信息

随后你可以调用`text2file`方法将文本块保存为md文档或txt文件

```python
from pdfdeal.doc2x import Doc2x
Client = Doc2x(api_key=api)
uuid = Client.async_pdf2file(pdf_file="test.pdf", Translate=True)
texts, Rawtexts, location = Client.async_uuid2file(uuid=uuid, Translate=True)
file = Client.text2file(texts=texts, filepath=".", output_format="md")
print(f"Translated file is saved at {file}")
```

## 获得剩余的额度
```python
from pdfdeal.doc2x import Doc2x

Client = Doc2x(api_key=your_api)

print(Client.get_limit())
```

## 异步的使用
```python
from pdfdeal.doc2x import Doc2x
Client = Doc2x(api_key=your_api)
uuid = Client.async_pic2file(image_file="test.png")
# uuid = Client.async_pdf2file(pdf_file="test.pdf")
# If the input file is PDF
texts = Client.async_uuid2file(uuid)
for text in texts:
    print(text)
```