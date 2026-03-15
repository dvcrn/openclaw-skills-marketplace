from click.testing import CliRunner

from stock_cli.cli import cli
from stock_cli.commands import kline as kline_command
from stock_cli.commands import quote as quote_command

runner = CliRunner()


def test_quote_output(monkeypatch):
    monkeypatch.setattr(
        quote_command,
        "get_stock_by_code",
        lambda _symbol: {
            "name": "顺灏股份",
            "code": "002565",
            "price": "13.19",
            "change_rate": "-4.28%",
            "previous_close": "13.78",
            "open": "13.64",
            "high": "13.76",
            "low": "13.15",
            "market_value": "139.81亿",
            "circulating_value": "139.81亿",
            "pe": "246.61",
            "pb": "7.50",
            "volume": "58.46万手",
            "vr": "0.76",
            "turnover_rate": "5.52%",
        },
    )
    result = runner.invoke(cli, ["quote", "600519"])
    assert result.exit_code == 0
    assert "# 个股信息" in result.output
    assert "股票: 顺灏股份，代码: 002565" in result.output
    assert "- 当前价格: 13.19" in result.output
    assert "- 换手率: 5.52%" in result.output


def test_search_table():
    result = runner.invoke(cli, ["search", "Apple"])
    assert result.exit_code == 0
    assert "暂无数据" in result.output


def test_market_output():
    result = runner.invoke(cli, ["market"])
    assert result.exit_code == 0
    assert "暂无数据" in result.output


def test_history_default_range_output():
    result = runner.invoke(cli, ["history", "AAPL"])
    assert result.exit_code == 0
    assert "暂无数据" in result.output


def test_history_custom_range():
    result = runner.invoke(cli, ["history", "AAPL", "--range", "5d"])
    assert result.exit_code == 0
    assert "暂无数据" in result.output


def test_kline_output(monkeypatch):
    monkeypatch.setattr(
        kline_command,
        "get_kline_data",
        lambda _symbol, count=45: {
            "lines": [
                {
                    "时间": 20260310,
                    "开盘价": 10.2,
                    "收盘价": 10.8,
                    "最高价": 10.9,
                    "最低价": 10.1,
                    "成交量": "1000手",
                    "成交额": "5000万",
                }
            ],
            "factors": {
                "ema_5": 10.55,
                "ema_10": 10.32,
                "ema_20": 10.11,
                "boll_up": 11.2,
                "boll_mid": 10.5,
                "boll_low": 9.8,
                "kdj_k": 61.2,
                "kdj_d": 58.9,
                "kdj_j": 65.8,
                "rsi_6": 54.12,
                "rsi_12": 51.88,
            },
        },
    )
    result = runner.invoke(cli, ["kline", "600519"])
    assert result.exit_code == 0
    assert "## 日K线" in result.output
    assert "时间,开盘价,收盘价,最高价,最低价,成交量,成交额" in result.output
    assert "20260310,10.2,10.8,10.9,10.1,1000手,5000万" in result.output
    assert "- EMA5: 10.55" in result.output
