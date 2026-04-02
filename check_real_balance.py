#!/usr/bin/env python3
"""
Check real balance on Midnight network.
This connects to the actual Midnight testnet to query your funded wallet.
"""

import httpx
import json
from pathlib import Path

# Your funded wallet address
WALLET_ADDRESS = "mn_addr_undeployed1x2w98jvk0wxppn3a3mlfw3ep736tdn7k2rhj7kjv292tcl6a0hyq3g5xa0"

# Midnight network endpoints
NETWORKS = {
    "testnet-02": {
        "indexer": "https://indexer.testnet-02.midnight.network/api/v4/graphql",
        "rpc": "https://rpc.testnet-02.midnight.network",
    },
    "undeployed": {
        "indexer": "http://127.0.0.1:8088/api/v4/graphql",
        "rpc": "http://127.0.0.1:9944",
    }
}


def check_balance(network="testnet-02"):
    """Check balance on specified network."""
    print(f"\n{'='*70}")
    print(f"Checking Balance on Midnight {network}")
    print(f"{'='*70}\n")
    
    print(f"Wallet: {WALLET_ADDRESS[:40]}...")
    print(f"Network: {network}")
    print(f"Indexer: {NETWORKS[network]['indexer']}\n")
    
    indexer_url = NETWORKS[network]['indexer']
    
    # Query 1: Check if indexer is alive
    print("Step 1: Checking indexer connectivity...")
    try:
        response = httpx.post(
            indexer_url,
            json={"query": "{ __typename }"},
            headers={"Content-Type": "application/json"},
            timeout=10.0,
        )
        if response.status_code == 200:
            print("  ✓ Indexer is online\n")
        else:
            print(f"  ✗ Indexer returned status {response.status_code}\n")
            return
    except Exception as e:
        print(f"  ✗ Cannot connect to indexer: {e}\n")
        print("  Tip: If using 'undeployed', make sure Docker services are running:")
        print("       docker-compose up -d\n")
        return
    
    # Query 2: Get latest block (proves chain is working)
    print("Step 2: Getting latest block...")
    block_query = """
    query {
        blocks(limit: 1) {
            height
            hash
            timestamp
        }
    }
    """
    try:
        response = httpx.post(
            indexer_url,
            json={"query": block_query},
            headers={"Content-Type": "application/json"},
            timeout=10.0,
        )
        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"].get("blocks"):
                blocks = data["data"]["blocks"]
                if blocks:
                    block = blocks[0]
                    print(f"  ✓ Latest block: {block.get('height', 'unknown')}")
                    print(f"    Hash: {block.get('hash', 'unknown')[:32]}...")
                    print(f"    Time: {block.get('timestamp', 'unknown')}\n")
                else:
                    print("  ⚠ No blocks found (chain might be empty)\n")
            else:
                print(f"  ⚠ Unexpected response: {data}\n")
        else:
            print(f"  ✗ Block query failed with status {response.status_code}\n")
    except Exception as e:
        print(f"  ✗ Block query error: {e}\n")
    
    # Query 3: Get DUST balance (unshielded)
    print("Step 3: Querying DUST balance (unshielded)...")
    dust_query = """
    query GetUnshieldedBalance($address: String!) {
        unshieldedCoins(address: $address) {
            value
        }
    }
    """
    try:
        response = httpx.post(
            indexer_url,
            json={"query": dust_query, "variables": {"address": WALLET_ADDRESS}},
            headers={"Content-Type": "application/json"},
            timeout=10.0,
        )
        if response.status_code == 200:
            data = response.json()
            if "errors" in data:
                print(f"  ⚠ GraphQL errors: {data['errors']}\n")
            elif "data" in data:
                coins = data["data"].get("unshieldedCoins")
                if coins:
                    if isinstance(coins, list):
                        dust = sum(int(c.get("value", 0)) for c in coins)
                    elif isinstance(coins, dict):
                        dust = int(coins.get("value", 0))
                    else:
                        dust = 0
                    print(f"  ✓ DUST balance: {dust:,}\n")
                else:
                    print(f"  ⚠ No unshielded coins found for this address\n")
                    print(f"  Raw response: {json.dumps(data, indent=2)}\n")
            else:
                print(f"  ⚠ Unexpected response format\n")
        else:
            print(f"  ✗ DUST query failed with status {response.status_code}\n")
    except Exception as e:
        print(f"  ✗ DUST query error: {e}\n")
    
    # Query 4: Explain NIGHT (shielded)
    print("Step 4: NIGHT balance (shielded)...")
    print("  ⚠ NIGHT tokens are shielded by design")
    print("  ⚠ The indexer CANNOT reveal shielded balances without a viewing key")
    print("  ⚠ This is privacy by design - not a bug!\n")
    
    print("To see your real NIGHT balance:")
    print("  1. Use the official Midnight wallet SDK")
    print("  2. Provide your viewing key to establish a session")
    print("  3. Query shieldedBalance with the session ID\n")
    
    print(f"{'='*70}\n")


def check_all_networks():
    """Check balance on all available networks."""
    for network in NETWORKS.keys():
        try:
            check_balance(network)
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            break
        except Exception as e:
            print(f"Error checking {network}: {e}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        network = sys.argv[1]
        if network in NETWORKS:
            check_balance(network)
        else:
            print(f"Unknown network: {network}")
            print(f"Available networks: {', '.join(NETWORKS.keys())}")
    else:
        # Default: check testnet-02 (real network)
        check_balance("testnet-02")
        
        print("\nTo check other networks:")
        print("  python check_real_balance.py testnet-02")
        print("  python check_real_balance.py undeployed")
