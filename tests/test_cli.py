"""Test the CLI functionality."""

import sys
from unittest.mock import patch

import pytest

from migration_analyser import cli


def test_cli_with_safe_sql(tmp_path, capsys):
    """Test CLI with safe SQL statements."""
    # Create a test SQL file with safe statements
    sql_file = tmp_path / "safe.sql"
    sql_file.write_text("SELECT * FROM users WHERE id = 1;")

    # Mock sys.argv
    with patch.object(sys, "argv", ["cli", str(sql_file)]):
        with pytest.raises(SystemExit) as exc_info:
            cli.main()

    # Should exit with code 0 (success)
    assert exc_info.value.code == 0

    # Check output
    captured = capsys.readouterr()
    assert "All statements are SAFE" in captured.out


def test_cli_with_dangerous_sql(tmp_path, capsys):
    """Test CLI with dangerous SQL statements."""
    # Create a test SQL file with dangerous statement
    sql_file = tmp_path / "dangerous.sql"
    sql_file.write_text("DELETE FROM users;")

    # Mock sys.argv
    with patch.object(sys, "argv", ["cli", str(sql_file)]):
        with pytest.raises(SystemExit) as exc_info:
            cli.main()

    # Should exit with code 1 (failure)
    assert exc_info.value.code == 1

    # Check output
    captured = capsys.readouterr()
    assert "WARNING: Dangerous statements found" in captured.out
    assert "ANALYSIS FAILED" in captured.out


def test_cli_with_nonexistent_file(capsys):
    """Test CLI with a file that doesn't exist."""
    # Mock sys.argv with non-existent file
    with patch.object(sys, "argv", ["cli", "nonexistent.sql"]):
        with pytest.raises(SystemExit) as exc_info:
            cli.main()

    # Should exit with code 2 (error)
    assert exc_info.value.code == 2

    # Check error output
    captured = capsys.readouterr()
    assert "File not found" in captured.err


def test_cli_with_multiple_files(tmp_path, capsys):
    """Test CLI with multiple SQL files."""
    # Create test SQL files
    safe_file = tmp_path / "safe.sql"
    safe_file.write_text("SELECT * FROM users WHERE id = 1;")

    dangerous_file = tmp_path / "dangerous.sql"
    dangerous_file.write_text("UPDATE users SET active = false;")

    # Mock sys.argv
    with patch.object(sys, "argv", ["cli", str(safe_file), str(dangerous_file)]):
        with pytest.raises(SystemExit) as exc_info:
            cli.main()

    # Should exit with code 1 (failure due to dangerous file)
    assert exc_info.value.code == 1

    # Check output
    captured = capsys.readouterr()
    assert "Total files analysed: 2" in captured.out
    assert "Files with dangerous statements: 1" in captured.out


def test_cli_no_fail_on_danger(tmp_path, capsys):
    """Test CLI with --no-fail-on-danger flag."""
    # Create a test SQL file with dangerous statement
    sql_file = tmp_path / "dangerous.sql"
    sql_file.write_text("DELETE FROM users;")

    # Mock sys.argv with --no-fail-on-danger
    with patch.object(sys, "argv", ["cli", "--no-fail-on-danger", str(sql_file)]):
        with pytest.raises(SystemExit) as exc_info:
            cli.main()

    # Should exit with code 0 even though dangerous statements exist
    assert exc_info.value.code == 0

    # Check output still shows warning
    captured = capsys.readouterr()
    assert "WARNING: Dangerous statements found" in captured.out
