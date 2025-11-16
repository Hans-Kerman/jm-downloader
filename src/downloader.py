import jmcomic


def download_by_id(num: int):
    option = jmcomic.create_option_by_file("./option.yml")
    jmcomic.download_album(num, option)

def main():
    num = input("请输入jm车牌号\n")
    download_by_id(int(num))


if __name__ == "__main__":
    main()
