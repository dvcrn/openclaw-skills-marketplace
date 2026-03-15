#!/usr/bin/env python3
"""Tests for team.py"""

import json
import sys
from io import StringIO
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import team


@pytest.fixture
def temp_data_file(tmp_path: Path):
    """Create a temporary data file for testing."""
    data_file = tmp_path / "team.json"
    team.set_data_file(str(data_file))
    yield data_file
    # Reset after test
    team.set_data_file(None)


@pytest.fixture
def sample_member_data():
    """Sample member data for testing."""
    return {
        "agent_id": "agent-001",
        "name": "Alice",
        "role": "Developer",
        "enabled": True,
        "tags": ["backend", "api"],
        "expertise": ["python", "go"],
        "not_good_at": ["frontend"],
    }


class TestListCommand:
    """Tests for the list command."""

    def test_list_empty_data(self, temp_data_file, capsys):
        """Test listing when no data exists."""
        team.list_members()
        captured = capsys.readouterr()
        assert "No team members found" in captured.out

    def test_list_with_members(self, temp_data_file, sample_member_data, capsys):
        """Test listing with existing members."""
        # Save sample data
        team.save_data({"team": {"agent-001": sample_member_data}})

        team.list_members()
        captured = capsys.readouterr()

        assert "Alice" in captured.out
        assert "Developer" in captured.out
        assert "backend" in captured.out
        assert "Total: 1 member(s)" in captured.out


class TestUpdateCommand:
    """Tests for the update command."""

    def test_add_new_member(self, temp_data_file, capsys):
        """Test adding a new member."""
        team.update_member(
            agent_id="agent-001",
            name="Alice",
            role="Developer",
            enabled=True,
            tags="backend, api",
            expertise="python, go",
            not_good_at="frontend",
        )
        captured = capsys.readouterr()
        assert "Added member: Alice (agent-001)" in captured.out

        # Verify data was saved
        data = team.load_data()
        assert "agent-001" in data["team"]
        assert data["team"]["agent-001"]["name"] == "Alice"

    def test_update_existing_member(self, temp_data_file, sample_member_data, capsys):
        """Test updating an existing member."""
        # Save initial data
        team.save_data({"team": {"agent-001": sample_member_data}})

        # Update the member
        team.update_member(
            agent_id="agent-001",
            name="Alice Updated",
            role="Senior Developer",
            enabled=False,
            tags="backend, api, database",
            expertise="python, go, postgresql",
            not_good_at="frontend, design",
        )
        captured = capsys.readouterr()
        assert "Updated member: Alice Updated (agent-001)" in captured.out

        # Verify data was updated
        data = team.load_data()
        assert data["team"]["agent-001"]["name"] == "Alice Updated"
        assert data["team"]["agent-001"]["role"] == "Senior Developer"
        assert data["team"]["agent-001"]["enabled"] is False

    def test_tags_parsing(self, temp_data_file):
        """Test that tags are correctly parsed from comma-separated string."""
        team.update_member(
            agent_id="agent-001",
            name="Test",
            role="Test",
            enabled=True,
            tags=" tag1 , tag2 , tag3 ",
            expertise="skill1",
            not_good_at="weakness1",
        )

        data = team.load_data()
        assert data["team"]["agent-001"]["tags"] == ["tag1", "tag2", "tag3"]


class TestResetCommand:
    """Tests for the reset command."""

    def test_reset_clears_data(self, temp_data_file, sample_member_data, capsys):
        """Test that reset clears all data."""
        # Save some data first
        team.save_data({"team": {"agent-001": sample_member_data}})

        # Reset
        team.reset_data()
        captured = capsys.readouterr()
        assert "reset to empty" in captured.out

        # Verify data is empty
        data = team.load_data()
        assert data["team"] == {}


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_load_data_file_not_exists(self, tmp_path):
        """Test loading when file doesn't exist."""
        non_existent = tmp_path / "nonexistent.json"
        team.set_data_file(str(non_existent))
        data = team.load_data()
        assert data == {"team": {}}
        team.set_data_file(None)

    def test_load_data_invalid_json(self, tmp_path):
        """Test loading when JSON is invalid."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("not valid json {")
        team.set_data_file(str(invalid_file))
        data = team.load_data()
        assert data == {"team": {}}
        team.set_data_file(None)

    def test_load_data_missing_team_key(self, tmp_path):
        """Test loading when JSON is missing 'team' key."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text('{"other": "data"}')
        team.set_data_file(str(bad_file))
        data = team.load_data()
        assert data == {"team": {}}
        team.set_data_file(None)

    def test_custom_data_file_path(self, tmp_path):
        """Test using a custom data file path."""
        custom_file = tmp_path / "custom_team.json"
        team.set_data_file(str(custom_file))

        team.update_member(
            agent_id="test-001",
            name="Test User",
            role="Tester",
            enabled=True,
            tags="test",
            expertise="testing",
            not_good_at="coding",
        )

        assert custom_file.exists()
        team.set_data_file(None)


class TestCLI:
    """Tests for command-line interface."""

    def test_list_cli(self, temp_data_file, monkeypatch, capsys):
        """Test list command via CLI."""
        monkeypatch.setattr(sys, "argv", ["team.py", "--data-file", str(temp_data_file), "list"])
        team.main()
        captured = capsys.readouterr()
        assert "No team members found" in captured.out

    def test_update_cli(self, temp_data_file, monkeypatch, capsys):
        """Test update command via CLI."""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "team.py",
                "--data-file",
                str(temp_data_file),
                "update",
                "--agent-id",
                "cli-001",
                "--name",
                "CLI User",
                "--role",
                "CLI Role",
                "--enabled",
                "true",
                "--tags",
                "cli",
                "--expertise",
                "testing",
                "--not-good-at",
                "nothing",
            ],
        )
        team.main()
        captured = capsys.readouterr()
        assert "Added member: CLI User (cli-001)" in captured.out

    def test_reset_cli(self, temp_data_file, sample_member_data, monkeypatch, capsys):
        """Test reset command via CLI."""
        team.save_data({"team": {"agent-001": sample_member_data}})

        monkeypatch.setattr(
            sys, "argv", ["team.py", "--data-file", str(temp_data_file), "reset"]
        )
        team.main()
        captured = capsys.readouterr()
        assert "reset to empty" in captured.out

    def test_no_command_shows_help(self, monkeypatch, capsys):
        """Test that running without command shows help."""
        monkeypatch.setattr(sys, "argv", ["team.py"])

        with pytest.raises(SystemExit) as exc_info:
            team.main()

        assert exc_info.value.code == 1