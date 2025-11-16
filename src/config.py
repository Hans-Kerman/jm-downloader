#解决和路径、初始化相关的问题
import jmcomic
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
OPTION_FILE = ROOT_DIR / "option.yml"
CUSTOM_ENV = ROOT_DIR / ".env"

API_KEY = ""
BASE_URL = ""
MODEL_NAME = ""
DOWNLOAD_PATH = ""
INPUT_PNG_DIR = ""

def generate_option_yml_by_env():
    DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH", "downloads")
    if not Path(DOWNLOAD_PATH).is_absolute():#是相对路径
        DOWNLOAD_PATH = str(Path(ROOT_DIR / DOWNLOAD_PATH))
    custom_option = jmcomic.JmOption.default()
    custom_option.dir_rule.base_dir = DOWNLOAD_PATH
    custom_option.to_file("./option.yml")

def generate_option_yml_Interactively():
    print("请输入使用的下载输出地址，直接回车则使用默认的./downloads")
    DOWNLOAD_PATH = input()
    if DOWNLOAD_PATH == "":
        DOWNLOAD_PATH = "downloads"
    custom_option = jmcomic.JmOption.default()
    custom_option.dir_rule.base_dir = DOWNLOAD_PATH
    custom_option.to_file("./option.yml")    

def generate_option_yml():
    if (OPTION_FILE.exists()):
        print("option.yml已存在，跳过生成重构")
    else:
        print("option.yml不存在，进行生成")
        if (CUSTOM_ENV.exists()):
            print("检测到.env文件，将直接使用文件内容生成配置文件")
            generate_option_yml_by_env()
        else:
            print("未检测到.env文件，交互式输入下载目录")
            generate_option_yml_Interactively()



def generate_env_Interactively():
    if not CUSTOM_ENV.exists():
        print("请复制.env.example为.env并且填充相关配置")


