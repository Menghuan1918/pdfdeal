# This is an example of how to convert all PDF files in a folder to multiple types of files.
# 这是一个将文件夹中的所有 PDF 文件转换为多种类型文件的示例。

from pdfdeal import Doc2X

# gets API Key from environment variable DOC2X_APIKEY, or you can pass it as a string to the apikey parameter
# 从环境变量 DOC2X_APIKEY 获取 API Key, 或者您可以将其作为字符串传递给 apikey 参数

# client = Doc2X(apikey="Your API key",debug=True)
client = Doc2X(debug=True)

success, failed, flag = client.pdf2file(
    pdf_file="/home/menghuan/文档/Test/pdf",
    output_path="./Output",
    output_format="docx,md",
)
print(success)
print(failed)
print(flag)
