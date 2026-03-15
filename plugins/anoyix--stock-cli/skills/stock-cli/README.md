# stock-cli

[![CI](https://github.com/AnoyiX/stock-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/AnoyiX/stock-cli/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/stock-cli.svg)](https://pypi.org/project/stock-cli/)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](https://pypi.org/project/stock-cli/)

股市数据命令行工具，支持个股行情。

## 功能特性

- 🎯 **个股行情**：按股票代码查询实时价格、涨跌幅、成交额、K 线

## 安装

```bash
# 推荐：uv tool（快速、隔离环境）
uv tool install stock-cli

# 或者：pipx
pipx install stock-cli
```

升级到最新版本：

```bash
uv tool upgrade stock-cli
# 或：pipx upgrade stock-cli
```

## 快速开始

```bash
stock quote 000001
```

## 开发

```bash
# 安装依赖
uv sync

# 运行测试
uv run pytest tests/ -v

# Lint
uv run ruff check .

# 安装当前目录源码，并暴露 `stock` 命令
uv tool install --from . stock-cli

# 强制升级
uv tool install --from . stock-cli --force --reinstall --refresh --no-cache

# 卸载
uv tool uninstall stock-cli

# 调试
uv run python -m stock_cli quote 000001
```
```

## License

Apache-2.0
