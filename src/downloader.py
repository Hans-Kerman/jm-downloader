import jmcomic
import sys
from pathlib import Path

from .config import ROOT_DIR


def download_by_id(num: int):
    option = jmcomic.create_option_by_file(str(ROOT_DIR / "option.yml"))
    # 配置中的 after_init 插件已在加载时执行，只补充缺失的进度展示。
    after_init = option.plugins.get("after_init", []) or []
    if not any(plugin.get("plugin") == "download_progress" for plugin in after_init):
        option.invoke_plugin(
            jmcomic.JmModuleConfig.REGISTRY_PLUGIN["download_progress"],
            kwargs={},
            extra={},
            pinfo={"plugin": "download_progress"},
        )
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
