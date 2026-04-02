"""
Network Detector - Automatically find which network has your wallet funded
"""

import httpx
from typing import Optional, Dict, List
from .models import Balance


class NetworkDetector:
    """Detect which Midnight network has a wallet funded."""
    
    # Networks to try in order of preference
    NETWORKS_TO_TRY = [
        "undeployed",
        "testnet",
        "testnet-02", 
        "preprod",
        "devnet",
        "mainnet"
    ]
    
    def __init__(self, indexer_urls: Dict[str, str]):
        """
        Initialize detector with indexer URLs for each network.
        
        Args:
            indexer_urls: Dict mapping network name to indexer URL
        """
        self.indexer_urls = indexer_urls
        self._http = httpx.Client(timeout=10.0)
    
    def detect_network(self, address: str) -> Optional[str]:
        """
        Detect which network has this wallet address funded.
        
        Args:
            address: Wallet address to check
            
        Returns:
            Network name if found, None otherwise
        """
        print(f"🔍 Detecting network for wallet: {address[:40]}...")
        print()
        
        for network in self.NETWORKS_TO_TRY:
            if network not in self.indexer_urls:
                continue
                
            indexer_url = self.indexer_urls[network]
            print(f"  Trying {network}... ", end="", flush=True)
            
            try:
                # Check if indexer is alive
                if not self._check_indexer_alive(indexer_url):
                    print("❌ Offline")
                    continue
                
                # Check balance
                balance = self._get_balance(indexer_url, address)
                
                if balance and (balance.dust > 0 or balance.night > 0):
                    print(f"✅ Found! (DUST: {balance.dust:,}, NIGHT: {balance.night:,})")
                    return network
                else:
                    print("⚪ Empty")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}")
                continue
        
        print()
        print("⚠️  Wallet not found on any network")
        return None
    
    def get_balance_from_any_network(self, address: str) -> tuple[Optional[str], Optional[Balance]]:
        """
        Get balance from whichever network has the wallet.
        
        Args:
            address: Wallet address
            
        Returns:
            Tuple of (network_name, balance) or (None, None)
        """
        network = self.detect_network(address)
        if not network:
            return None, None
        
        indexer_url = self.indexer_urls[network]
        balance = self._get_balance(indexer_url, address)
        
        return network, balance
    
    def _check_indexer_alive(self, indexer_url: str) -> bool:
        """Check if indexer is reachable."""
        try:
            response = self._http.post(
                indexer_url,
                json={"query": "{ __typename }"},
                headers={"Content-Type": "application/json"},
                timeout=5.0,
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def _get_balance(self, indexer_url: str, address: str) -> Optional[Balance]:
        """Get balance from a specific indexer."""
        # Query for DUST (unshielded)
        dust_query = """
        query GetUnshieldedBalance($address: String!) {
            unshieldedCoins(address: $address) {
                value
            }
        }
        """
        
        try:
            response = self._http.post(
                indexer_url,
                json={"query": dust_query, "variables": {"address": address}},
                headers={"Content-Type": "application/json"},
                timeout=5.0,
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "data" in data and data["data"]:
                    coins = data["data"].get("unshieldedCoins")
                    
                    dust = 0
                    if coins:
                        if isinstance(coins, list):
                            dust = sum(int(c.get("value", 0)) for c in coins)
                        elif isinstance(coins, dict):
                            dust = int(coins.get("value", 0))
                    
                    # NIGHT is shielded, so we return 0 (requires viewing key)
                    return Balance(dust=dust, night=0)
            
            return None
            
        except Exception:
            return None
    
    def get_network_info(self, network: str) -> Dict[str, str]:
        """Get information about a specific network."""
        info = {
            "undeployed": {
                "name": "Local Undeployed",
                "description": "Local development network",
                "explorer": "http://localhost:8088"
            },
            "testnet": {
                "name": "Testnet-02",
                "description": "Midnight public testnet",
                "explorer": "https://explorer.testnet-02.midnight.network"
            },
            "testnet-02": {
                "name": "Testnet-02",
                "description": "Midnight public testnet",
                "explorer": "https://explorer.testnet-02.midnight.network"
            },
            "preprod": {
                "name": "Preprod",
                "description": "Pre-production network",
                "explorer": "https://explorer.preprod.midnight.network"
            },
            "devnet": {
                "name": "Devnet",
                "description": "Development network",
                "explorer": "https://explorer.devnet.midnight.network"
            },
            "mainnet": {
                "name": "Mainnet",
                "description": "Midnight mainnet",
                "explorer": "https://explorer.midnight.network"
            }
        }
        
        return info.get(network, {
            "name": network,
            "description": "Unknown network",
            "explorer": ""
        })
