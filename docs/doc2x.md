# Installation

```bash
pip install pdfdeal
```

You can request a personal identity token at [https://doc2x.com/](https://doc2x.com/)

> Of course I definitely recommend signing up using my invite link: [https://doc2x.com/login?invite_code=4AREZ6](https://doc2x.com/login?invite_code=4AREZ6)

![图片](https://github.com/Menghuan1918/pdfdeal/assets/122662527/0b41b142-8210-4009-9ece-ce6f7bf2591a)


## Basic Use

## PDF to Text/MD/Latex

```python
from pdfdeal.doc2x import Doc2x

Client = Doc2x(api_key=your_api)

Client.pdf2file(pdf_file="./ppt/test.pdf", output_path="./output", output_format="md_dollar", ocr=True)
```

where `output_format` accepts 'text', “md”, “md_dollar”, “latex”, “docx”.” The difference between “md” and “md_dollar” is that the formula indicates whether or not to use the “$” sign, and “text” means to return the text directly without saving.

## Image to text/MD/Latex

```python
from pdfdeal.doc2x import Doc2x

Client = Doc2x(api_key=your_api)

Client.pic2file(image_file="image.png", output_path="./output", output_format="docx", equation=True)
```

where `output_format` accepts 'text', “md”, “md_dollar”, “latex”, “docx”.” The difference between “md” and “md_dollar” is that the formula indicates whether or not to use the “$” sign, and “text” means to return the text directly without saving.

## Conversion that preserves the original page count
This method preserves the original page count of the text as well as the text in the image. That is, the content of each page of the processed pdf is the source document corresponding to the number of pages.

```python
from pdfdeal.doc2x import Doc2x
Client = Doc2x(api_key=your_api)
file_path = "./test.pdf"
Client.pdfdeal(input=file_path, output="pdf", path="./Output", convert=True)
```

## As an OCR engine for pdfdeal
It is recommended to use the above method `Conversion that preserves the original page count` instead of using doc2x as the OCR engine.

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

## Getting the rest of the credit
```python
from pdfdeal.doc2x import Doc2x

Client = Doc2x(api_key=your_api)

print(Client.get_limit())
```

## The use of asynchrony
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