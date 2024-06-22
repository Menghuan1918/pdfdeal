## Update for V0.1.0

> [!IMPORTANT]
> The `0.0.X` version of the method is deprecated and will be removed in the future, please migrate to the new implementation as soon as possible. You can find it [here](./doc2x_old.md) to see the documentation for older versions.
>
> Most of its interfaces haven't changed, you can try changing `from pdfdeal.doc2x import Doc2x` to `from pdfdeal.doc2x import Doc2X` directly.

## Update for V0.1.1

> [!IMPORTANT]
> The return format has changed, please pay attention to modify your code to adapt to the new return format.
>
> Now you can choose the return format by the `version` parameter, when it is `v2`, it will return: `list: successful processing files` `list: processing failed files` `bool`.
>
> The default `v1` return parameter will only return `list: successful processing files`.

### ✨ New Features

- All functions now support the new return format, through the **optional parameter** `version` to choose, when it is `v2`, it will return: `list: successful processing files` `list: processing failed files` `bool`, and the default `v1` return parameter will only return `list: successful processing files`.
- `pdf2file` and `file2pdf` now support the **optional parameter** `output_names` to specify the output file name.
- Added request retry mechanism, now it will automatically retry when the network request fails.
- Added error handling mechanism, now it will automatically handle errors when processing files, and will not cause the entire program to interrupt due to a file error.

### 🐛 Bug Fixes

- Fixed the font exception problem in the `pdfdeal` function.
- Fixed some abnormal use of keys.
- Fixed the problem that the rpm limit may not take effect.

## Installation

[![Python package test](https://github.com/Menghuan1918/pdfdeal/actions/workflows/python-test.yml/badge.svg)](https://github.com/Menghuan1918/pdfdeal/actions/workflows/python-test.yml)

This project supports python 3.9-3.12 and has been tested on Windows/Linux/MacOS systems. Use `pip` to install:

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
Client = Doc2X(apikey=api, rpm=20, maxretry=10)
```

And:
- `rpm` represents the number of requests per minute, default is 3.
- `maxretry` represents the maximum number of retries, default is 5.

> [!NOTE]
> For personal use, sugguest not change the default settings.

## Usage

Please set the API key first.

> [!NOTE]
> About the `version` parameter:
>
> - `v1`: Only return the list of successful processing files.
>
> When the `version` parameter is `v2`, it will return: `list: successful processing files` `list: processing failed files` `bool`.
>
> The lengths of `list1` and `list2` are the same.
> 
> For each element in `list1`, if the processing is successful, its value is the processed file path, and if the processing fails, its value is an empty string.
>
> For each element in `list2`, its value is a dictionary containing `error` and `path`, `error` is the error message, and `path` is the file path that failed to be processed. When the corresponding file is processed successfully, the values of the two keys are empty strings.
>
> `bool` is `True` means that at least one file processing failed, and `False` means that all processing was successful. For more information, please refer to the example.

### Deal with Pictures

`Client.pic2file`

Accepts a single or multiple (list) of image paths and returns the processed output file path.

Input parameters:
- `image_file`: image file path or image file path list
- `output_path`: `str`, optional, output folder path, default is `"./Output"`
- `output_names` : `list`, optional, output file name list, the length must be the same as `image_file`, used to specify the output file name.
- `output_format`: `str`, optional, output format, accepts `texts`, `md`, `md_dollar`, `latex`, default is `md_dollar`. Selecting `texts` will return text directly and will not be saved to a file.
- `img_correction`: `bool`, optional, whether to perform image correction, default is `True`
- `equation`: `bool`, optional, use pure formula output mode, default is `False`
- `convert`: `bool`, optional, whether to convert `[` to `$`, `[[` to `$$`, default is `False`, only valid when `output_format` is `texts`
- `version`: `str`, optional, return format, accepts `v1`, `v2`, when it is `v2`, it will return more information, default is `v1`

#### Example: Process multiple images according to the rpm limit, return in `v2` format

```python
from pdfdeal.doc2x import Doc2X
client = Doc2X()
file_list = ["tests/image/sample_bad.png", "tests/image/sample.png"]
# If you don't need to use the renaming function, you can use the function gen_folder_list from pdfdeal.file_tools to generate a file list from the folder (because its sorting is not fixed)
# For example:
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

When the first file fails to process and the second file is processed successfully, the example output is:

```python
['', './Output/test/multiple/pdf2file/sample2.docx']
[{'error': 'Error Upload file error! 500:{"code":"service unavailable","msg":"read file error"}', 'path': 'tests/pdf/sample_bad.pdf'}, {'error': '', 'path': ''}]
True
```

#### Example: Process a single image and get the content in the form of `$formula$`, in pure formula mode

```python
from pdfdeal.doc2x import Doc2X
client = Doc2X()
text = client.pic2file(
    "tests/image/sample.png", output_format="texts", equation=True, convert=True
)
print(text)
```

The example output is:

```python
[['$$\\text{Test}$$']]
```

### PDF Processing

`Client.pdf2file`

Accepts a single or multiple (list) of pdf paths and returns the processed output file path.

Input parameters:
- `pdf_file`: pdf file path or pdf file path list
- `output_path`: `str`, optional, output folder path, default is `"./Output"`
- `output_names` : `list`, optional, output file name list, the length must be the same as `pdf_file`, used to specify the output file name.
- `output_format`: `str`, optional, output format, accepts `texts`, `md`, `md_dollar`, `latex`, `docx`, default is `md_dollar`. Selecting `texts` will return text directly and will not be saved to a file.
- `ocr`: `bool`, optional, whether to use OCR, default is `True`
- `convert`: `bool`, optional, whether to convert `[` to `$`, `[[` to `$$`, default is `False`, only valid when `output_format` is `texts`
- `version`: `str`, optional, return format, accepts `v1`, `v2`, when it is `v2`, it will return more information, default is `v1`

#### Example: Convert a single pdf to a latex file and specify the output file name

```python
from pdfdeal.doc2x import Doc2X

client = Doc2X()
filepath = client.pdf2file(
    "tests/pdf/sample.pdf", output_names=["Test.zip"], output_format="latex"
)
print(filepath)
```

When successful, the example output is:

```python
['./Output/Test.zip']
```

When processing fails, the example output is:

```python
['']
```

#### Example: Convert multiple pdfs to docx files, return in `v2` format

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

When the first file fails to process and the second file is processed successfully, the example output is:

```python
['', './Output/test/multiple/pdfdeal/sample.pdf']
[{'error': Exception('Upload file error! 500:{"code":"service unavailable","msg":"read file error"}'), 'path': 'tests/pdf/sample_bad.pdf'}, {'error': '', 'path': ''}]
True
```

### Get Remaining Request Times

`Client.get_limit`

Returns the remaining number of API requests.

```python
from pdfdeal.doc2x import Doc2X
Client = Doc2X()
print(f"Pages remaining: {Client.get_limit()}")
```

Example output:

```python
Pages remaining: 2229
```

### Used for RAG Knowledge Base Preprocessing

`Client.pdfdeal`

Accepts a single or multiple (list) of pdf paths and returns the processed output file path.

Input parameters:
- `input`: pdf file path or pdf file path list
- `output`: `str`, optional, output format, accepts `pdf`, `md`, default is `pdf`
- `path`: `str`, optional, output folder path, default is `"./Output"`
- `convert`: `bool`, optional, whether to convert `[` to `$`, `[[` to `$$`, default is `True`
- `version`: `str`, optional, return format, accepts `v1`, `v2`, when it is `v2`, it will return more information, default is `v1`

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

When the first file fails to process and the second file is processed successfully, the example output is:

```python
['', './Output/test/multiple/pdfdeal/sample.pdf']
[{'error': Exception('Upload file error! 500:{"code":"service unavailable","msg":"read file error"}'), 'path': 'tests/pdf/sample_bad.pdf'}, {'error': '', 'path': ''}]
True
```

### Translate PDF Documents

Get the translated text and location information (EN -> CN only).

```python
from pdfdeal.doc2x import Doc2X

Client = Doc2X()
translate = Client.pdf_translate("test.pdf")
for text in translate[0]:
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