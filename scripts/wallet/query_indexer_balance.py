#!/usr/bin/env python3
"""
Query balance directly from Midnight indexer using GraphQL
This bypasses the wallet sync and queries UTXOs directly
"""

import httpx
import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from midnight_sdk.wallet import WalletClient
from midnight_sdk.config import ConfigManager

def query_indexer_balance(address: str, indexer_url: str):
    """Query balance from indexer using GraphQL."""
    
    # Try multiple query formats
    queries = [
        # Query 1: Try to get DUST generation status
        {
            "query": """
                query GetDustStatus($address: String!) {
                    dustGenerationStatus(cardanoRewardAddresses: [$address]) {
                        nightBalance
                        currentCapacity
                        dustAddress
                    }
                }
            """,
            "variables": {"address": address}
        },
        # Query 2: Try to get unshielded transactions
        {
            "query": """
                query GetBalance {
                    transactions(offset: {identifier: "0x00"}) {
                        unshieldedCreatedOutputs {
                            owner
                            value
                            tokenType
                        }
                        unshieldedSpentOutputs {
                            owner
                            value
                            tokenType
                        }
                    }
                }
            """
        },
        # Query 3: Try block query
        {
            "query": """
                query GetLatestBlock {
                    block {
                        height
                        hash
                    }
                }
            """
        }
    ]
    
    client = httpx.Client(timeout=30.0)
    
    for i, query_data in enumerate(queries):
        try:
            print(f"Trying query {i+1}...", file=sys.stderr)
            response = client.post(
                indexer_url,
                json=query_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Query {i+1} response: {json.dumps(result, indent=2)}", file=sys.stderr)
                
                if "errors" not in result:
                    return result
            else:
                print(f"Query {i+1} failed with status {response.status_code}", file=sys.stderr)
                
        except Exception as e:
            print(f"Query {i+1} error: {e}", file=sys.stderr)
            continue
    
    return None

def main():
    config_mgr = ConfigManager()
    config_mgr.load()
    profile = config_mgr.get_profile("1AM_preprod")
    
    # Get wallet address
    wallet_name = config_mgr.config.default_wallet
    wallet_path = Path(config_mgr.config.wallets[wallet_name])
    mnemonic = wallet_path.read_text().strip()
    
    wallet_client = WalletClient(profile.node_url)
    addr_info = wallet_client.get_real_address(mnemonic, profile.network_id)
    address = addr_info['address']
    
    print(f"\nQuerying balance for: {address}", file=sys.stderr)
    print(f"Indexer: {profile.indexer_url}\n", file=sys.stderr)
    
    result = query_indexer_balance(address, profile.indexer_url)
    
    if result:
        print("\n=== Indexer Response ===", file=sys.stderr)
        print(json.dumps(result, indent=2))
    else:
        print("All queries failed", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
