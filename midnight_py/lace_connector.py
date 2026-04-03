"""
Lace Wallet Connector for Python CLI

This module provides integration with the Lace wallet browser extension,
allowing Python developers to connect their Lace wallet to the CLI.

Based on Midnight DApp Connector API v4.0.1
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from .models import Balance
from .exceptions import WalletError


class LaceConnector:
    """
    Connect to Lace wallet via Node.js bridge.
    
    Since Lace wallet is a browser extension, we use a Node.js script
    to access window.midnight.mnLace and bridge it to Python.
    """
    
    def __init__(self, network: str = "preprod"):
        self.network = network
        self._bridge_script = Path(__file__).parent.parent / "lace_bridge.mjs"
    
    def is_available(self) -> bool:
        """Check if Lace wallet is installed and accessible."""
        try:
            result = subprocess.run(
                ["node", str(self._bridge_script), "check"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0 and "available" in result.stdout.lower()
        except Exception:
            return False
    
    def get_wallet_info(self) -> Dict[str, str]:
        """Get Lace wallet name, icon, and API version."""
        try:
            result = subprocess.run(
                ["node", str(self._bridge_script), "info"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            raise WalletError(f"Failed to get wallet info: {result.stderr}")
        except json.JSONDecodeError as e:
            raise WalletError(f"Invalid response from Lace wallet: {e}")
        except subprocess.TimeoutExpired:
            raise WalletError("Lace wallet connection timed out")
    
    def connect(self) -> Dict[str, Any]:
        """
        Connect to Lace wallet and get connected API.
        
        This will prompt the user in their browser to approve the connection.
        
        Returns:
            Dict with connection status and API access
        """
        try:
            result = subprocess.run(
                ["node", str(self._bridge_script), "connect", self.network],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            raise WalletError(f"Failed to connect to Lace wallet: {result.stderr}")
        except json.JSONDecodeError as e:
            raise WalletError(f"Invalid response from Lace wallet: {e}")
        except subprocess.TimeoutExpired:
            raise WalletError("Lace wallet connection timed out. User may have rejected the connection.")
    
    def get_balance(self) -> Balance:
        """
        Get wallet balance from Lace wallet.
        
        Returns:
            Balance object with NIGHT and DUST amounts
        """
        try:
            result = subprocess.run(
                ["node", str(self._bridge_script), "balance", self.network],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return Balance(
                    dust=int(data.get("dust", 0)),
                    night=int(data.get("night", 0))
                )
            raise WalletError(f"Failed to get balance from Lace wallet: {result.stderr}")
        except json.JSONDecodeError as e:
            raise WalletError(f"Invalid response from Lace wallet: {e}")
        except subprocess.TimeoutExpired:
            raise WalletError("Lace wallet balance query timed out")
    
    def get_addresses(self) -> Dict[str, str]:
        """
        Get wallet addresses from Lace wallet.
        
        Returns:
            Dict with shielded, unshielded, and dust addresses
        """
        try:
            result = subprocess.run(
                ["node", str(self._bridge_script), "addresses", self.network],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            raise WalletError(f"Failed to get addresses from Lace wallet: {result.stderr}")
        except json.JSONDecodeError as e:
            raise WalletError(f"Invalid response from Lace wallet: {e}")
        except subprocess.TimeoutExpired:
            raise WalletError("Lace wallet address query timed out")
    
    def get_configuration(self) -> Dict[str, str]:
        """
        Get service configuration from Lace wallet.
        
        Returns:
            Dict with indexer, node, and proof server URLs
        """
        try:
            result = subprocess.run(
                ["node", str(self._bridge_script), "config", self.network],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            raise WalletError(f"Failed to get configuration from Lace wallet: {result.stderr}")
        except json.JSONDecodeError as e:
            raise WalletError(f"Invalid response from Lace wallet: {e}")
        except subprocess.TimeoutExpired:
            raise WalletError("Lace wallet configuration query timed out")


def check_lace_wallet() -> bool:
    """
    Quick check if Lace wallet is available.
    
    Returns:
        True if Lace wallet is installed and accessible
    """
    connector = LaceConnector()
    return connector.is_available()


def get_lace_balance(network: str = "preprod") -> Optional[Balance]:
    """
    Get balance from Lace wallet.
    
    Args:
        network: Network to query (preprod, testnet, mainnet)
    
    Returns:
        Balance object or None if Lace wallet is not available
    """
    connector = LaceConnector(network=network)
    if not connector.is_available():
        return None
    
    try:
        connector.connect()
        return connector.get_balance()
    except WalletError:
        return None
