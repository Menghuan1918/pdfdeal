# This is an example of how to convert a single PDF file to a single DOCX file.
# 这是一个将单个 PDF 文件转换为单个 DOCX 文件的示例。

from pdfdeal import Doc2X

# gets API Key from environment variable DOC2X_APIKEY, or you can pass it as a string to the apikey parameter
# 从环境变量 DOC2X_APIKEY 获取 API Key, 或者您可以将其作为字符串传递给 apikey 参数

# client = Doc2X(apikey="Your API key",debug=True)
client = Doc2X(debug=True)

success, failed, flag = client.pdf2file(
    pdf_file="tests/pdf/sample.pdf",
    output_path="Output",
    output_format="docx",
)
print(success)
print(failed)
print(flag)
