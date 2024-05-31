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

Client.pic2file(image_file="image.png", output_path="./output", output_format="docx")
```

其中`output_format`接受'text'，"md", "md_dollar", "latex", "docx"。"md"和"md_dollar"的区别在于公式表示是否使用“$”号，"text"代表直接返回文本而不保存。

## 作为pdfdeal的OCR引擎

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
