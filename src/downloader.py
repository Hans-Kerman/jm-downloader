import jmcomic
import sys
from pathlib import Path

from .config import ROOT_DIR


def download_by_id(num: int):
    option = jmcomic.create_option_by_file(str(ROOT_DIR / "option.yml"))
    jmcomic.download_album(num, option)


def main():
    if sys.argv[0] == "python":
        if len(sys.argv) == 2:
            num = input("请输入jm车牌号\n")
        elif len(sys.argv) == 3:
            num = sys.argv[-1]
        else:
            print("参数数量不正确")
            exit()
    else: 
        if len(sys.argv) == 1:
            num = input("请输入jm车牌号\n")
        elif len(sys.argv) == 2:
            num = sys.argv[-1]
        else:
            print("参数数量不正确")
            exit()
    download_by_id(int(num))


if __name__ == "__main__":
    main()
