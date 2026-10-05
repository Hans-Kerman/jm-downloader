个人自用的jm-api downloader

## 环境与运行

Nix flake 只负责提供 `uv`，Python 3.12 与全部依赖由 uv 管理（uv 自管 CPython + `.venv`）。

进入项目目录（direnv 自动激活 flake 环境并挂载 uv 的 `.venv`）或手动进入：

```bash
nix develop
```

安装依赖并运行：

```bash
uv sync
uv run python main.py
```

`.venv` 建好后，direnv 进目录即自动挂载，`python`/`pip` 直接指向 `.venv`，可省略 `uv run`。依赖变更后手动 `uv sync`（direnv 不自动 sync）。

## JM 账号与收藏下载

复制 `.env.example` 为 `.env`，填写账号字段：

```dotenv
JM_USERNAME=""
JM_PASSWORD=""
```

两项均空时可匿名下载单本；只填一项会提示配置不完整。填写完整账号后，下载入口自动使用上游 `login` 插件登录，无需重新生成 `option.yml`，也不会把账号密码写入该文件。已有 `option.yml` 登录插件优先使用其配置，不重复登录。`.env` 固定从项目根目录加载，已有进程环境变量优先。

JM 登录无需 API key 或 PAT；`.env` 中的 `API_KEY`、`BASE_URL` 仅用于 OCR，进入图片识别选项时才检查和初始化客户端。未找到上游登录后提高下载速度或并发的显式开关，因此保持已有 `download.threading` 配置。

首次运行先用菜单选项 3 生成 `option.yml`。选择 **4 - 下载账号全部收藏** 后，程序先读取全部收藏分页并按 album ID 去重，再逐本下载，每本内部保留已有章节、图片并发。登录或收藏列表读取失败时返回菜单，不启动下载。

单本异常或部分图片、章节下载失败时继续其他漫画，结束显示成功数、失败数、未处理数及失败 ID。再次运行会重新读取收藏，按现有 `download.cache` 设置跳过已有图片，不额外增加整本重试。按 `Ctrl+C` 停止启动后续漫画，等待当前本下载完成或失败后汇总并返回菜单；再次按键仍等待当前本收尾。

## 下载进度条

项目下载入口默认启用上游 `download_progress` 插件，依赖 `rich`。已有 `option.yml` 无需修改；若已在 `plugins.after_init` 中配置该插件，则沿用其参数，不重复启用。

在支持动态刷新的终端（包括 SSH 终端）中，显示最近日志及 album、章节两级进度条；非 TTY 输出使用上游的静态汇总模式。完整日志默认追加到运行目录的 `jmcomic-download.log`。

`jmcomic` 不设版本范围，使用 PyPI 发布版。`uv.lock` 仍记录具体版本；`uv sync` 不会自动检查新版。跟进最新发布版并更新依赖快照：

```bash
uv lock --upgrade-package jmcomic
uv sync
uv pip compile pyproject.toml --upgrade-package jmcomic -o requirements.txt
```

进度条能力需要 jmcomic 2.7.4 或更新版本，详见[上游文档](https://github.com/hect0x7/JMComic-Crawler-Python/blob/master/assets/docs/sources/tutorial/15_download_progress.md)。

## 使用 tmux 保持后台下载

本项目不提供应用内后台任务切换。需要离开终端或断开 SSH 时，在项目根目录运行：

```bash
tmux new -s jm-download
uv run python main.py
```

按 `Ctrl+b` 后按 `d` 脱离会话，下载继续运行。重新查看进度：

```bash
tmux attach -t jm-download
```

需要本机已安装 tmux；不要用 `Ctrl+Z` 代替脱离会话，它会暂停进程。
