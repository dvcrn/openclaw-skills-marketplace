# GITCODE_TOKEN（跨平台）

| 用法 | 说明 |
|------|------|
| `python scripts/setup_gitcode_token.py` | 检查是否已配置；已配置则输出来源并 exit 0，否则提示并 exit 1。 |
| `python scripts/setup_gitcode_token.py --set` | 未配置时提示输入；Windows 写入用户环境变量，Linux/macOS 输出 `export GITCODE_TOKEN=...` 可追加到 ~/.bashrc。 |
| `python scripts/setup_gitcode_token.py -q` | 静默：仅用退出码表示是否已配置（0=已配置，1=未配置），适合 Agent/CI。 |

Windows / Linux / macOS 均可运行，依赖 Python 3.6+ 标准库。
