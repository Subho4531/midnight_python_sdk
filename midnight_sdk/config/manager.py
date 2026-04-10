"""Configuration manager for Midnight SDK profiles and settings."""

import os
from pathlib import Path
from typing import Any
import yaml
from pydantic import BaseModel


class NetworkProfile(BaseModel):
    """Network profile configuration."""
    name: str
    node_url: str
    indexer_url: str
    indexer_ws_url: str
    proof_server_url: str
    network_id: str
    explorer_url: str = ""


class Config(BaseModel):
    """Main configuration structure."""
    active_profile: str = "local"
    profiles: dict[str, NetworkProfile] = {}
    wallets: dict[str, str] = {}  # name -> mnemonic path
    default_wallet: str = ""


class ConfigManager:
    """Manages SDK configuration and profiles."""
    
    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or Path.home() / ".midnight" / "config.yaml"
        self.config: Config | None = None
        
    def load(self) -> Config:
        """Load configuration from file."""
        if not self.config_path.exists():
            self.config = self._create_default_config()
            self.save()
        else:
            with open(self.config_path) as f:
                data = yaml.safe_load(f) or {}
                self.config = Config(**data)
        return self.config
    
    def save(self) -> None:
        """Save configuration to file."""
        if self.config is None:
            raise ValueError("No configuration loaded")
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            yaml.dump(self.config.model_dump(), f, default_flow_style=False)
    
    def get_profile(self, name: str | None = None) -> NetworkProfile:
        """Get a network profile by name or active profile."""
        if self.config is None:
            self.load()
        
        profile_name = name or self.config.active_profile
        if profile_name not in self.config.profiles:
            raise ValueError(f"Profile '{profile_name}' not found")
        
        return self.config.profiles[profile_name]
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value using dot notation."""
        if self.config is None:
            self.load()
        
        parts = key.split(".")
        if len(parts) == 1:
            setattr(self.config, key, value)
        elif parts[0] == "profiles" and len(parts) >= 2:
            profile_name = parts[1]
            if profile_name not in self.config.profiles:
                raise ValueError(f"Profile '{profile_name}' not found")
            if len(parts) == 2:
                # Setting entire profile
                self.config.profiles[profile_name] = value
            else:
                # Setting profile attribute
                attr = parts[2]
                setattr(self.config.profiles[profile_name], attr, value)
        else:
            raise ValueError(f"Invalid config key: {key}")
        
        self.save()
    
    def get(self, key: str) -> Any:
        """Get a configuration value using dot notation."""
        if self.config is None:
            self.load()
        
        parts = key.split(".")
        obj = self.config
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            elif isinstance(obj, dict) and part in obj:
                obj = obj[part]
            else:
                raise ValueError(f"Config key not found: {key}")
        return obj
    
    def add_profile(self, profile: NetworkProfile) -> None:
        """Add a new network profile."""
        if self.config is None:
            self.load()
        
        self.config.profiles[profile.name] = profile
        self.save()
    
    def _create_default_config(self) -> Config:
        """Create default configuration with standard profiles."""
        return Config(
            active_profile="local",
            profiles={
                "local": NetworkProfile(
                    name="local",
                    node_url="http://127.0.0.1:9944",
                    indexer_url="http://127.0.0.1:8088/api/v4/graphql",
                    indexer_ws_url="ws://127.0.0.1:8088/api/v4/graphql/ws",
                    proof_server_url="http://127.0.0.1:6300",
                    network_id="undeployed",
                    explorer_url="http://localhost:3000",
                ),
                "preprod": NetworkProfile(
                    name="preprod",
                    node_url="https://rpc.preprod.midnight.network",
                    indexer_url="https://indexer.preprod.midnight.network/api/v4/graphql",
                    indexer_ws_url="wss://indexer.preprod.midnight.network/api/v4/graphql/ws",
                    proof_server_url="https://proof-server.preprod.midnight.network",
                    network_id="preprod",
                    explorer_url="https://explorer.preprod.midnight.network",
                ),
                "testnet": NetworkProfile(
                    name="testnet",
                    node_url="https://rpc.testnet-02.midnight.network",
                    indexer_url="https://indexer.testnet-02.midnight.network/api/v4/graphql",
                    indexer_ws_url="wss://indexer.testnet-02.midnight.network/api/v4/graphql/ws",
                    proof_server_url="https://proof-server.testnet-02.midnight.network",
                    network_id="testnet-02",
                    explorer_url="https://explorer.testnet-02.midnight.network",
                ),
                "mainnet": NetworkProfile(
                    name="mainnet",
                    node_url="https://rpc.midnight.network",
                    indexer_url="https://indexer.midnight.network/api/v4/graphql",
                    indexer_ws_url="wss://indexer.midnight.network/api/v4/graphql/ws",
                    proof_server_url="https://proof-server.midnight.network",
                    network_id="mainnet",
                    explorer_url="https://explorer.midnight.network",
                ),
            },
        )
