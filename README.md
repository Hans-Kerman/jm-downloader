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
