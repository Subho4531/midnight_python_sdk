"""Tests for configuration manager."""

import pytest
from pathlib import Path
import tempfile
import yaml

from midnight_sdk.config import ConfigManager, NetworkProfile


@pytest.fixture
def temp_config_path():
    """Create temporary config path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "config.yaml"


def test_config_manager_init(temp_config_path):
    """Test ConfigManager initialization."""
    mgr = ConfigManager(temp_config_path)
    assert mgr.config_path == temp_config_path
    assert mgr.config is None


def test_config_manager_load_creates_default(temp_config_path):
    """Test loading creates default config."""
    mgr = ConfigManager(temp_config_path)
    config = mgr.load()
    
    assert config.active_profile == "local"
    assert "local" in config.profiles
    assert "preprod" in config.profiles
    assert temp_config_path.exists()


def test_config_manager_save(temp_config_path):
    """Test saving configuration."""
    mgr = ConfigManager(temp_config_path)
    mgr.load()
    mgr.config.active_profile = "preprod"
    mgr.save()
    
    # Load again and verify
    mgr2 = ConfigManager(temp_config_path)
    config2 = mgr2.load()
    assert config2.active_profile == "preprod"


def test_config_manager_get_profile(temp_config_path):
    """Test getting profile."""
    mgr = ConfigManager(temp_config_path)
    mgr.load()
    
    profile = mgr.get_profile("local")
    assert profile.name == "local"
    assert profile.network_id == "undeployed"


def test_config_manager_get_active_profile(temp_config_path):
    """Test getting active profile."""
    mgr = ConfigManager(temp_config_path)
    mgr.load()
    mgr.config.active_profile = "preprod"
    
    profile = mgr.get_profile()
    assert profile.name == "preprod"


def test_config_manager_set_simple(temp_config_path):
    """Test setting simple value."""
    mgr = ConfigManager(temp_config_path)
    mgr.load()
    
    mgr.set("active_profile", "testnet")
    assert mgr.config.active_profile == "testnet"


def test_config_manager_get_simple(temp_config_path):
    """Test getting simple value."""
    mgr = ConfigManager(temp_config_path)
    mgr.load()
    
    value = mgr.get("active_profile")
    assert value == "local"


def test_config_manager_add_profile(temp_config_path):
    """Test adding new profile."""
    mgr = ConfigManager(temp_config_path)
    mgr.load()
    
    custom_profile = NetworkProfile(
        name="custom",
        node_url="http://custom.node",
        indexer_url="http://custom.indexer",
        indexer_ws_url="ws://custom.indexer",
        proof_server_url="http://custom.proof",
        network_id="custom",
    )
    
    mgr.add_profile(custom_profile)
    
    # Verify it was added
    profile = mgr.get_profile("custom")
    assert profile.name == "custom"
    assert profile.node_url == "http://custom.node"


def test_config_manager_invalid_profile(temp_config_path):
    """Test getting invalid profile raises error."""
    mgr = ConfigManager(temp_config_path)
    mgr.load()
    
    with pytest.raises(ValueError, match="Profile 'invalid' not found"):
        mgr.get_profile("invalid")


def test_config_manager_yaml_format(temp_config_path):
    """Test config is saved in valid YAML format."""
    mgr = ConfigManager(temp_config_path)
    mgr.load()
    mgr.save()
    
    # Read and parse YAML
    with open(temp_config_path) as f:
        data = yaml.safe_load(f)
    
    assert "active_profile" in data
    assert "profiles" in data
    assert isinstance(data["profiles"], dict)
