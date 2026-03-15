import json

from click.testing import CliRunner

from stock_cli.cli import cli

runner = CliRunner()


def test_config_show_default(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    monkeypatch.setenv("STOCK_CLI_CONFIG_PATH", str(config_path))
    result = runner.invoke(cli, ["config", "show"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["market"] == "US"


def test_config_set_market(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    monkeypatch.setenv("STOCK_CLI_CONFIG_PATH", str(config_path))
    set_result = runner.invoke(cli, ["config", "set", "market", "HK"])
    assert set_result.exit_code == 0
    show_result = runner.invoke(cli, ["config", "show"])
    payload = json.loads(show_result.output)
    assert payload["market"] == "HK"
