#!/usr/bin/env python3
"""
Test All Contracts - Comprehensive Testing Suite
Tests deployment and execution of all contracts with transaction signing
"""

import time
from pathlib import Path
from midnight_py import MidnightClient


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def get_private_key(client):
    """Get private key from mnemonic"""
    mnemonic_file = Path("mnemonic.txt")
    if not mnemonic_file.exists():
        print("[ERROR] mnemonic.txt not found!")
        return None
    
    mnemonic = mnemonic_file.read_text().strip()
    keys = client.wallet.get_private_keys(mnemonic)
    return keys['nightExternal']


def test_hello_world(client, private_key):
    """Test Hello World contract"""
    print_section("Test 1: Hello World Contract")
    
    print("[Step 1] Deploy hello_world contract...")
    contract = client.contracts.deploy(
        "contracts/hello_world.compact",
        private_key=private_key,
        sign_transaction=True
    )
    
    print(f"\n[Step 2] Call storeMessage circuit...")
    result = contract.call(
        circuit_name="storeMessage",
        private_key=private_key,
        sign_transaction=True
    )
    
    print(f"[OK] Transaction: {result.tx_hash}")
    print(f"[OK] Status: {result.status}")
    print(f"[OK] Explorer: http://localhost:8088/tx/{result.tx_hash}")
    
    # Wait for confirmation
    print("\n[Step 3] Waiting for confirmation...")
    time.sleep(4)
    
    return contract


def test_counter(client, private_key):
    """Test Counter contract"""
    print_section("Test 2: Counter Contract")
    
    print("[Step 1] Deploy counter contract...")
    contract = client.contracts.deploy(
        "contracts/counter.compact",
        private_key=private_key,
        sign_transaction=True
    )
    
    print(f"\n[Step 2] Call increment circuit (3 times)...")
    for i in range(3):
        result = contract.call(
            circuit_name="increment",
            private_key=private_key,
            sign_transaction=True
        )
        print(f"  Increment {i+1}: {result.tx_hash[:32]}...")
        time.sleep(1)
    
    print(f"\n[OK] Counter incremented 3 times")
    print(f"[OK] Last transaction: {result.tx_hash}")
    
    # Wait for confirmation
    print("\n[Step 3] Waiting for confirmation...")
    time.sleep(4)
    
    return contract


def test_bulletin_board(client, private_key):
    """Test Bulletin Board contract"""
    print_section("Test 3: Bulletin Board Contract")
    
    print("[Step 1] Deploy bulletin_board contract...")
    contract = client.contracts.deploy(
        "contracts/bulletin_board.compact",
        private_key=private_key,
        sign_transaction=True
    )
    
    print(f"\n[Step 2] Post messages (3 times)...")
    messages = ["Hello Midnight!", "ZK Proofs are cool", "Blockchain privacy"]
    
    for i, msg in enumerate(messages):
        result = contract.call(
            circuit_name="post",
            private_key=private_key,
            sign_transaction=True
        )
        print(f"  Post {i+1} '{msg}': {result.tx_hash[:32]}...")
        time.sleep(1)
    
    print(f"\n[OK] Posted 3 messages")
    print(f"[OK] Last transaction: {result.tx_hash}")
    
    # Wait for confirmation
    print("\n[Step 3] Waiting for confirmation...")
    time.sleep(4)
    
    return contract


def test_private_vote(client, private_key):
    """Test Private Vote contract"""
    print_section("Test 4: Private Vote Contract")
    
    print("[Step 1] Deploy private_vote contract...")
    contract = client.contracts.deploy(
        "contracts/private_vote.compact",
        private_key=private_key,
        sign_transaction=True
    )
    
    print(f"\n[Step 2] Cast votes...")
    
    # Vote Yes (3 times)
    print("  Casting YES votes...")
    for i in range(3):
        result = contract.call(
            circuit_name="voteYes",
            private_key=private_key,
            sign_transaction=True
        )
        print(f"    Vote YES {i+1}: {result.tx_hash[:32]}...")
        time.sleep(1)
    
    # Vote No (2 times)
    print("  Casting NO votes...")
    for i in range(2):
        result = contract.call(
            circuit_name="voteNo",
            private_key=private_key,
            sign_transaction=True
        )
        print(f"    Vote NO {i+1}: {result.tx_hash[:32]}...")
        time.sleep(1)
    
    print(f"\n[OK] Cast 5 votes (3 YES, 2 NO)")
    print(f"[OK] Last transaction: {result.tx_hash}")
    
    # Wait for confirmation
    print("\n[Step 3] Waiting for confirmation...")
    time.sleep(4)
    
    return contract


def main():
    print("=" * 70)
    print("  Midnight Contract Testing Suite")
    print("  Testing All Contracts with Transaction Signing")
    print("=" * 70)
    
    # Initialize client
    print("\n[SETUP] Initialize Midnight Client...")
    client = MidnightClient(
        network="undeployed",
        wallet_address="mn_addr_undeployed1zaa268rc7sjz0ctscrsy7mp2ne7khfz8wu2uqsu4msfvxnlt6qfsmfrhr0",
        proof_server_url="http://localhost:6300",
    )
    print("[OK] Client initialized")
    
    # Get private key
    print("\n[SETUP] Derive private key from mnemonic...")
    private_key = get_private_key(client)
    if not private_key:
        return
    print(f"[OK] Private key: {private_key[:16]}...")
    
    # Test all contracts
    contracts = {}
    
    try:
        contracts['hello_world'] = test_hello_world(client, private_key)
    except Exception as e:
        print(f"[ERROR] Hello World test failed: {e}")
    
    try:
        contracts['counter'] = test_counter(client, private_key)
    except Exception as e:
        print(f"[ERROR] Counter test failed: {e}")
    
    try:
        contracts['bulletin_board'] = test_bulletin_board(client, private_key)
    except Exception as e:
        print(f"[ERROR] Bulletin Board test failed: {e}")
    
    try:
        contracts['private_vote'] = test_private_vote(client, private_key)
    except Exception as e:
        print(f"[ERROR] Private Vote test failed: {e}")
    
    # Summary
    print_section("Test Summary")
    
    print("Deployed Contracts:")
    for name, contract in contracts.items():
        print(f"  {name:20} -> {contract.address}")
        print(f"  {'':20}    Circuits: {', '.join(contract.circuit_ids)}")
    
    print(f"\nTotal Contracts Tested: {len(contracts)}/4")
    print("\nAll transactions can be viewed at: http://localhost:8088/")
    print("\nTo check transaction status:")
    print("  midnight-py tx list")
    print("  midnight-py tx status <tx_hash>")
    
    print("\n" + "=" * 70)
    print("  Testing Complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
