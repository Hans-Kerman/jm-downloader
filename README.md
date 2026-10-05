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
