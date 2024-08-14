LANGUAGES = ["简体中文", "Enlish"]
WORDS_CN = [
    "🔎 请选择文件预处理工具,其中Tool类代表其会直接处理PDF文件，OCR类代表其会仅会使用OCR处理图片文件：",
    "🔎 请选择备用文件预处理工具,其中Tool类代表其会直接处理PDF文件，OCR类代表其会仅会使用OCR处理图片文件：",
    "📇 请输入 Doc2X 的身份令牌，个人用户请访问 https://doc2x.noedgeai.com/ 获取：",
    "⚠️ 验证 Doc2X 的身份令牌失败，请检查网络连接或者身份令牌是否正确",
    "📌 请选择 Doc2X 的速率限制，含意为同时请求数量，建议输入 A 以自动选择速率限制：",
]
WORDS_EN = [
    "🔎 Please select the file pre-processing tool, where the Tool class represents that it will directly process PDF files, and the OCR class represents that it will only use OCR to process image files:",
    "🔎 Please select the fallback file pre-processing tool, where the Tool class represents that it will directly process PDF files, and the OCR class represents that it will only use OCR to process image files:",
    "📇 Please enter the API key of the Doc2X, for personal use, visit https://doc2x.com/ to get the key:",
    "⚠️ Failed to verify the API key of Doc2X, please check the network connection or the API key",
    "📌 Please select the rate limit of Doc2X, means number of simultaneous requests, it is recommended to enter A to automatically select the rate limit:",
]
WORDS = [WORDS_CN, WORDS_EN]


WORDS_LOCAL_CN = [
    "📂 请输入项目文件夹的名称：",
    "⚠️ 文件夹已存在，请重新输入：",
    "🔗 正在尝试在以下路径初始化项目文件夹配置：",
    "💾 找到全局配置，是否使用全局配置？",
    "🌐 请选择预处理完成后的文件输出方式：",
]
WORDS_LOCAL_EN = [
    "📂 Please enter the name of the project folder:",
    "⚠️ The folder already exists, please re-enter:",
    "🔗 Trying to initialize the project folder configuration at the following path:",
    "💾 Found global configuration, do you want to use it?",
    "🌐 Please select the file output method after preprocessing:",
]

WORDS_LOCAL = [WORDS_LOCAL_CN, WORDS_LOCAL_EN]
