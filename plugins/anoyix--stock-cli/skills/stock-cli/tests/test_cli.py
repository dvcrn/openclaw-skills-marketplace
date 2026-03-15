from click.testing import CliRunner

from stock_cli.cli import cli

runner = CliRunner()


def test_help_lists_planned_commands():
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "quote" in result.output
    assert "kline" in result.output
    assert "search" in result.output
    assert "market" in result.output
    assert "history" in result.output
    assert "config" in result.output


def test_quote_help_supports_symbol_argument():
    result = runner.invoke(cli, ["quote", "--help"])
    assert result.exit_code == 0
    assert "SYMBOL" in result.output


def test_history_help_supports_range_option():
    result = runner.invoke(cli, ["history", "--help"])
    assert result.exit_code == 0
    assert "--range" in result.output


def test_kline_help_supports_code_argument():
    result = runner.invoke(cli, ["kline", "--help"])
    assert result.exit_code == 0
    assert "CODE" in result.output


def test_version():
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "stock" in result.output.lower()


def test_short_version():
    result = runner.invoke(cli, ["-v"])
    assert result.exit_code == 0
    assert "stock" in result.output.lower()
