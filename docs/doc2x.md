> [!IMPORTANT]
> The `0.0.X` version of the method is deprecated and will be removed in the future, please migrate to the new implementation as soon as possible. You can find it [here](./doc2x_old.md) to see the documentation for older versions.
>
> Most of its interfaces haven't changed, you can try changing `from pdfdeal.doc2x import Doc2x` to `from pdfdeal.doc2x import Doc2X` directly.

## Installation

`pdfdeal` supports python3.9 and higher, install using `pip`:

```bash
pip install --upgrade pdfdeal
```

## Configure API Key

For personal use, please log in to [https://doc2x.com/](https://doc2x.com/), click on `Personal Information`, and copy the identity token as your API key.

### Use Environment Variables (Recommended)

Run the following code to import your API key:

```python
from pdfdeal.doc2x import Doc2X
Client = Doc2X()
```

#### MacOS/Linux

Use the following command to set the environment variable for the current terminal:

```bash
export DOC2X_APIKEY = "Your API Key
```

You can also add the above command to `~/.zshrc` or `~/.bashrc` to persist the environment variable.

#### Windows

Use the following command to set the environment variable for the current terminal:

```PowerShell
setx DOC2X_APIKEY "Your API Key"
```

You can add it to `This PC` -> `Properties` -> `Advanced system settings` -> `Environment Variables` -> `System Variables` to persist.

### Set API Key for the Project Separately

If you want the API key to be visible only to a single project, you can create a local `.env` file containing your API key. Here is an example of a `.env` file:

```
DOC2X_APIKEY = "Your API Key"
```

The code for importing is the same as the method of using environment variables.

### Specify API Key (Not Recommended)

If you want to specify your API key, you can import it with the following code:

```python
from pdfdeal.doc2x import Doc2X
Client = Doc2X(apikey="Your API key")
```

## Config

You can also configure global settings when configuring the key:

```python
from pdfdeal.doc2x import Doc2X
Client = Doc2X(apikey=api,rpm=25,thread=5,maxretry=10)
```

And:
- `rpm` represents the number of requests per minute, default is 3.
- `thread` represents the number of threads, default is 1.
- `maxretry` represents the maximum number of retries, default is 5.

> [!NOTE]
> For personal use, sugguest not change the default settings.

## Usage

Please set the API key first.

### Deal with Pictures

`Client.pic2file`

Accepts a single or multiple (list) of image paths and returns the processed output file path.

Input parameters:
- `image_file`: image file path or image file path list
- `output_path`: `str`, optional, output folder path, default is `"./Output"`
- `output_format`: `str`, optional, output format, accepts `texts`, `md`, `md_dollar`, `latex`, default is `md_dollar`. Selecting `texts` will return text directly and will not be saved to a file.
- `img_correction`: `bool`, optional, whether to perform image correction, default is `True`
- `equation`: `bool`, optional, use pure formula output mode, default is `False`
- `convert`: `bool`, optional, whether to convert `[` to `$`, `[[` to `$$`, default is `False`, only valid when `output_format` is `texts`

Example: Process multiple images according to the rpm limit

```python
from pdfdeal.doc2x import Doc2X
from pdfdeal.file_tools import gen_folder_list
Client = Doc2X()
filelist = gen_folder_list("./test","img")
# This is a built-in function that generates the paths of all images in the folder, you can give any list form of image paths
finished_list =  Client.pic2file(filelist,output_format="docx")
print(*finished_list, sep='\n')
```

Example: Process a single image and get the content in the form of `$formula$`

```python
from pdfdeal.doc2x import Doc2X
Client = Doc2X()
text = Client.pic2file("./test.png", output_format="texts", convert=True)
print(*text, sep='\n')
```

### PDF Processing

`Client.pdf2file`

Accepts a single or multiple (list) of pdf paths and returns the processed output file path.

Input parameters:
- `pdf_file`: pdf file path or pdf file path list
- `output_path`: `str`, optional, output folder path, default is `"./Output"`
- `output_format`: `str`, optional, output format, accepts `texts`, `md`, `md_dollar`, `latex`, `docx`, default is `md_dollar`. Selecting `texts` will return text directly and will not be saved to a file.
- `ocr`: `bool`, optional, whether to use OCR, default is `True`
- `convert`: `bool`, optional, whether to convert `[` to `$`, `[[` to `$$`, default is `False`, only valid when `output_format` is `texts`

Example: Convert a single pdf to a latex file

```python
from pdfdeal.doc2x import Doc2X
Client = Doc2X()
filepath = Client.pdf2file("test.pdf",output_format ="latex")
print(filepath)
# Returns the output file path
```

Example: Convert multiple pdfs to docx files

```python
from pdfdeal.doc2x import Doc2X
from pdfdeal.file_tools import gen_folder_list
Client = Doc2X()
filelist = gen_folder_list("./test","pdf")
# This is a built-in function that generates the paths of all pdfs in the folder, you can give any list form of pdf paths
finished_list =  Client.pdf2file(filelist,output_format="docx")
print(*finished_list, sep='\n')
```

### Get Remaining Request Times

`Client.get_limit`

Returns the remaining number of API requests.

```python
from pdfdeal.doc2x import Doc2X
Client = Doc2X()
print(f"Pages remaining: {Client.get_limit()}")
```

### Used for RAG Knowledge Base Preprocessing

`Client.pdfdeal`

Accepts a single or multiple (list) of pdf paths and returns the processed output file path.

Input parameters:
- `input`: pdf file path or pdf file path list
- `output`: `str`, optional, output format, accepts `pdf`, `md`, default is `pdf`
- `path`: `str`, optional, output folder path, default is `"./Output"`
- `convert`: `bool`, optional, whether to convert `[` to `$`, `[[` to `$$`, default is `True`

```python
from pdfdeal.doc2x import Doc2X

Client = Doc2X()
filelist = gen_folder_list("./test","pdf")
# This is a built-in function that generates the paths of all pdfs in the folder, you can give any list form of pdf paths
Client.pdfdeal(filelist)
```

### Translate PDF Documents

Get the translated text and location information (EN -> CN only).

```python
from pdfdeal.doc2x import Doc2X

Client = Doc2X()
translate = Client.pdf_translate("test.pdf")
for text in translate:
    print(text["texts"])
    print(text["location"])
```

Among them, `text["texts"]` is the translated text, which is a list, an empty string means that the current text block is not translated (for example: it is table text), example output:

```
['翻译之后']
```

`text["location"]` is the location information of the text, which is a list corresponding to `text["texts"]`, example output:

```
[{'raw_text': 'xxx', 'page_idx': 0, 'page_width': 1581, 'page_height': 2047, 'x': 178, 'y': 184}]
```