import jmcomic
import os
import signal
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dotenv import load_dotenv

from .config import CUSTOM_ENV, OPTION_FILE


class DownloadSetupError(Exception):
    """可直接向用户展示、不包含凭据的下载初始化错误。"""


def prepare_download_option(require_login=False):
    load_dotenv(CUSTOM_ENV)
    if not OPTION_FILE.exists():
        raise DownloadSetupError("option.yml 不存在，请先使用菜单选项 3 生成配置")

    # 上游 after_init 会吞掉登录异常，因此先取出登录插件，单独严格执行。
    try:
        data = jmcomic.PackerUtil.unpack(str(OPTION_FILE))[0]
        plugins = data.get("plugins") or {}
        after_init = plugins.get("after_init") or []
        login_entries = [p for p in after_init if p.get("plugin") == "login"]
        if len(login_entries) > 1:
            raise DownloadSetupError("请在 option.yml 中只保留一个 login 插件")
        if login_entries:
            login_info = login_entries[0]
            # 延后到 option 构建后解析上游支持的环境变量引用。
            login_kwargs = None
        else:
            login_info = {}
            login_kwargs = {
                "username": os.getenv("JM_USERNAME", ""),
                "password": os.getenv("JM_PASSWORD", ""),
            }
            if bool(login_kwargs["username"]) != bool(login_kwargs["password"]):
                raise DownloadSetupError("请同时填写 JM_USERNAME 和 JM_PASSWORD")
            if require_login and not login_kwargs["username"]:
                raise DownloadSetupError("下载收藏需要先填写 .env 中的 JM_USERNAME 和 JM_PASSWORD")

        plugins["after_init"] = [p for p in after_init if p.get("plugin") != "login"]
        data["plugins"] = plugins
        data.setdefault("filepath", str(OPTION_FILE))
        option = jmcomic.JmOption.construct(data)
    except DownloadSetupError:
        raise
    except Exception:
        raise DownloadSetupError("无法加载 option.yml，请检查配置格式及插件依赖") from None

    try:
        if login_kwargs is None:
            login_kwargs = option.fix_kwargs(login_info.get("kwargs"))
        username = login_kwargs.get("username", "")
        password = login_kwargs.get("password", "")
        if login_entries and (not username or not password):
            raise DownloadSetupError("option.yml 的 login 插件需要完整用户名和密码")
        if username and password:
            plugin = jmcomic.JmLoginPlugin.build(option)
            plugin.log_enable = login_info.get("log", True)
            plugin.invoke(**login_kwargs)
    except DownloadSetupError:
        raise
    except Exception:
        raise DownloadSetupError("JM 登录失败，请检查账号、密码和网络后重试") from None

    # 配置中的 after_init 插件已在加载时执行，只补充缺失的进度展示。
    if not any(plugin.get("plugin") == "download_progress" for plugin in after_init):
        try:
            option.invoke_plugin(
                jmcomic.JmModuleConfig.REGISTRY_PLUGIN["download_progress"],
                kwargs={},
                extra={},
                pinfo={"plugin": "download_progress", "valid": "raise"},
            )
        except Exception:
            raise DownloadSetupError("下载进度插件初始化失败，请检查 rich 依赖和日志路径") from None
    return option, username


def download_by_id(num: int, option=None):
    if option is None:
        option, _ = prepare_download_option()
    return jmcomic.download_album(num, option)


def download_favorites():
    try:
        option, username = prepare_download_option(require_login=True)
        client = option.build_jm_client()
        print("正在读取全部收藏…")
        album_ids = list(dict.fromkeys(
            str(album_id)
            for page in client.favorite_folder_gen(folder_id="0", username=username)
            for album_id, _ in page
        ))
    except DownloadSetupError as e:
        print(e)
        return
    except KeyboardInterrupt:
        print("已取消读取收藏，未启动下载")
        return
    except Exception:
        print("收藏读取失败，请检查登录状态及网络；未启动下载")
        return

    if not album_ids:
        print("收藏为空，没有需要下载的漫画")
        return

    print(f"共 {len(album_ids)} 本收藏，开始逐本下载")
    succeeded = []
    failed = []
    interrupted = False
    stop_notice_shown = False

    def request_stop(signum, frame):
        nonlocal interrupted
        interrupted = True

    # 主线程接收 Ctrl+C；工作线程不受信号中断，能够完整收尾当前本。
    previous_handler = signal.signal(signal.SIGINT, request_stop)
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            for index, album_id in enumerate(album_ids, 1):
                if interrupted:
                    break
                print(f"正在下载 {index}/{len(album_ids)}：JM{album_id}")
                future = executor.submit(download_by_id, album_id, option)
                try:
                    while True:
                        if interrupted and not stop_notice_shown:
                            print("已停止启动后续漫画，等待当前本下载收尾…")
                            stop_notice_shown = True
                        try:
                            future.result(timeout=0.2)
                            break
                        except TimeoutError:
                            if future.done():
                                # 区分等待超时与下载函数自身抛出的 TimeoutError。
                                future.result()
                except Exception:
                    failed.append(album_id)
                    print(f"JM{album_id} 下载失败或部分内容未完成，继续下一本")
                else:
                    succeeded.append(album_id)
    finally:
        signal.signal(signal.SIGINT, previous_handler)

    print(f"{'任务已中断' if interrupted else '任务结束'}：总数 {len(album_ids)}，"
          f"成功 {len(succeeded)}，失败 {len(failed)}，"
          f"未处理 {len(album_ids) - len(succeeded) - len(failed)}")
    if failed:
        print("失败 ID：" + ", ".join(failed))


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
