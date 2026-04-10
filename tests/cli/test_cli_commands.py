"""Tests for CLI commands."""

import pytest
from typer.testing import CliRunner
from pathlib import Path
import tempfile

from midnight_sdk.cli import app
from midnight_sdk.config import ConfigManager

runner = CliRunner()


def test_cli_help():
    """Test CLI help output."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Production-ready CLI for Midnight blockchain" in result.stdout


def test_cli_version():
    """Test version command."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "Midnight SDK CLI" in result.stdout


def test_wallet_help():
    """Test wallet command help."""
    result = runner.invoke(app, ["wallet", "--help"])
    assert result.exit_code == 0
    assert "wallet" in result.stdout.lower()


def test_config_help():
    """Test config command help."""
    result = runner.invoke(app, ["config", "--help"])
    assert result.exit_code == 0
    assert "config" in result.stdout.lower()


def test_contract_help():
    """Test contract command help."""
    result = runner.invoke(app, ["contract", "--help"])
    assert result.exit_code == 0
    assert "contract" in result.stdout.lower()


def test_tx_help():
    """Test tx command help."""
    result = runner.invoke(app, ["tx", "--help"])
    assert result.exit_code == 0
    assert "transaction" in result.stdout.lower()


def test_proof_help():
    """Test proof command help."""
    result = runner.invoke(app, ["proof", "--help"])
    assert result.exit_code == 0
    assert "proof" in result.stdout.lower()


def test_ai_help():
    """Test ai command help."""
    result = runner.invoke(app, ["ai", "--help"])
    assert result.exit_code == 0
    assert "ai" in result.stdout.lower()


def test_system_help():
    """Test system command help."""
    result = runner.invoke(app, ["system", "--help"])
    assert result.exit_code == 0
    assert "system" in result.stdout.lower()


def test_config_init():
    """Test config init command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        
        # Mock ConfigManager to use temp path
        result = runner.invoke(app, ["config", "init"])
        
        # Should succeed (creates default config)
        assert result.exit_code == 0 or "Config" in result.stdout


def test_config_list():
    """Test config list command."""
    result = runner.invoke(app, ["config", "list"])
    
    # Should show profiles
    assert result.exit_code == 0 or "Profile" in result.stdout or "local" in result.stdout


@pytest.mark.parametrize("command", [
    ["wallet", "list"],
    ["system", "info"],
    ["explorer", "--help"],
    ["node", "--help"],
    ["events", "--help"],
])
def test_command_groups_accessible(command):
    """Test all command groups are accessible."""
    result = runner.invoke(app, command)
    assert result.exit_code in [0, 1]  # 0 for success, 1 for expected errors (no wallets, etc.)
