from __future__ import annotations

from pathlib import Path

from twitter_cli.config import load_config


def test_filter_normalization_for_invalid_values(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "\n".join(
            [
                "fetch:",
                "  count: -5",
                "filter:",
                "  mode: unknown",
                "  topN: -1",
                "  minScore: abc",
                "  lang: zh",
                "  weights:",
                "    likes: bad",
                "    retweets: 4",
            ]
        ),
        encoding="utf-8",
    )

    config = load_config(str(config_file))
    assert config["fetch"]["count"] == 1
    assert config["filter"]["mode"] == "topN"
    assert config["filter"]["topN"] == 1
    assert config["filter"]["minScore"] == 50.0
    assert config["filter"]["lang"] == []
    assert config["filter"]["weights"]["likes"] == 1.0
    assert config["filter"]["weights"]["retweets"] == 4.0
