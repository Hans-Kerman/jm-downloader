import base64
import os
import json
from openai import OpenAI
from src import config
from src import downloader
from dotenv import load_dotenv

if config.CUSTOM_ENV.exists():
    load_dotenv() 

    # 获取API配置 (推荐为必须项提供默认错误提示)
    API_KEY = os.getenv("API_KEY")
    BASE_URL = os.getenv("BASE_URL")
    if not API_KEY or not BASE_URL:
        raise ValueError("API_KEY and BASE_URL must be set in your .env file")

    # 获取模型名称 (可以提供一个默认值)
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    # 获取路径配置
    DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH", "downloads") # 提供一个默认值 "downloads"
    INPUT_PNG_DIR = os.getenv("INPUT_PNG_DIR", "input_images")
else:
    print("请先设置.env文件")
    exit()

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)

def encode_image_to_base64(image_path) -> str:
    """将图片文件编码为Base64字符串"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
def llm_ocr(image_path: str):
    try:
        base64_image = encode_image_to_base64(image_path=image_path)
    except FileNotFoundError:
        print("错误：请确保图片文件在当前目录下，或提供正确路径。")
        exit()

    prompt_text = """
You are an OCR agent that extracts numbers from an image.

Return ONLY a valid JSON object:
{"sequence": [num1, num2, ...]}

Rules:
- Detect all natural numbers (each usually 6–7 digits).
- Output JSON only — no explanations, no Markdown, no code fences.
- If nothing is detected, output {"sequence": []}.
"""

    number_array: list[int] = []
    try:
        print("正在发起API请求...")
        response = client.chat.completions.create(
            # 你的模型供应商让你使用的模型名称
            model=MODEL_NAME, 
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1000,
        )
        try:
            # 6. 解析结果
            response_text = response.choices[0].message.content
            print(f"模型返回的原始文本:\n{response_text}")
            if response_text:
                try:
                    # 尝试将返回的文本解析为JSON
                    result_json = json.loads(response_text)
                    # 从JSON中提取你想要的数组
                    number_array = result_json.get("sequence")
                    if isinstance(number_array, list):
                        print(f"\n成功提取到Python列表 (数组): {number_array}")
                        print(f"列表的类型是: {type(number_array)}")
                    else:
                        print("\n错误：模型返回的数据中'sequence'字段不是一个列表。")

                except json.JSONDecodeError:
                    # 处理模型返回了非JSON格式字符串的情况
                    print("\n[错误] 模型返回的不是一个有效的JSON字符串。")
                    # 在这里你可以选择重试、记录日志或返回一个错误状态
        except IndexError:
            # 这个异常处理也很重要，如果API返回的 choices 列表是空的
            print("\n[错误] API返回的响应中不包含任何 'choices'。")
    except Exception as e:
        print(f"\n调用API或解析数据时发生错误: {e}")    
    
    return (number_array, response.usage)


if __name__ == '__main__':
    while(1):
        a = input(
'''
请选择工作模式:
    1 - 下载单独的album
    2 - 输入图片下载所有合集    
    3 - 使用.env更新配置
    0 - 退出程序
'''
        )
        match a:
            case '1':
                downloader.main()
            case '2':
                image_path = input("请输入要解析的图片的路径\n")
                albums, tokens = llm_ocr(image_path=image_path)
                for num in albums:
                    downloader.download_by_id(num)
                print(f"任务结束，共消耗tokens如下：\n{str(tokens)}")
            case '3':
                config.generate_option_yml()
            case '0':
                print("退出程序")
                exit()  
            case _:
                print("非法输入，退出程序")
                exit()
