#!/usr/bin/env python3
"""
Fund a wallet address with DUST and NIGHT tokens.
This sets the balance on the local blockchain.
"""

import httpx
import sys

# Your wallet address
WALLET_ADDRESS = "mn_addr_undeployed1x2w98jvk0wxppn3a3mlfw3ep736tdn7k2rhj7kjv292tcl6a0hyq3g5xa0"

# Node URL
NODE_URL = "http://127.0.0.1:9944"

# Funding amounts (in smallest units)
DUST_AMOUNT = 1000000000000  # 1 trillion DUST
NIGHT_AMOUNT = 5000000000    # 5 billion NIGHT (5,000,000 NIGHT with 6 decimals)


def fund_wallet(address: str, dust: int, night: int):
    """Fund a wallet with specified amounts."""
    print(f"\n{'='*70}")
    print("Funding Wallet on Local Blockchain")
    print(f"{'='*70}\n")
    
    print(f"Address: {address[:40]}...")
    print(f"DUST:    {dust:,}")
    print(f"NIGHT:   {night:,}\n")
    
    try:
        response = httpx.post(
            f"{NODE_URL}/balance",
            json={
                "address": address,
                "dust": dust,
                "night": night
            },
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Wallet funded successfully!\n")
            print(f"  Address: {data['address'][:40]}...")
            print(f"  DUST:    {data['dust']:,}")
            print(f"  NIGHT:   {data['night']:,}\n")
            
            print("Verify balance with:")
            print(f"  midnight-py balance {address}\n")
            print(f"  python check_real_balance.py undeployed\n")
            
            return True
        else:
            print(f"✗ Failed to fund wallet: HTTP {response.status_code}")
            print(f"  Response: {response.text}\n")
            return False
            
    except httpx.ConnectError:
        print("✗ Cannot connect to node")
        print("  Make sure Docker services are running:")
        print("    docker-compose up -d\n")
        return False
    except Exception as e:
        print(f"✗ Error: {e}\n")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Custom address provided
        address = sys.argv[1]
        dust = int(sys.argv[2]) if len(sys.argv) > 2 else DUST_AMOUNT
        night = int(sys.argv[3]) if len(sys.argv) > 3 else NIGHT_AMOUNT
        fund_wallet(address, dust, night)
    else:
        # Fund default address
        fund_wallet(WALLET_ADDRESS, DUST_AMOUNT, NIGHT_AMOUNT)
