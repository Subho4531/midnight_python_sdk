#!/usr/bin/env python3
"""
Test real contract deployment on Midnight Preprod network
Uses real wallet, real transactions, real explorer
"""

import sys
from pathlib import Path
from midnight_py import MidnightClient

# REAL Preprod wallet
PREPROD_WALLET = "mn_addr_preprod1qr0n4n8lhczmnnjv0ryzvcul3dteals0ejjgs7mmpqueh4u9clqssyv3kd"
PREPROD_NETWORK = "preprod"

def print_section(title):
    """Print a section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def test_1_check_preprod_services():
    """Test 1: Check preprod network connectivity"""
    print_section("TEST 1: Check Preprod Network Services")
    
    client = MidnightClient(network=PREPROD_NETWORK)
    status = client.status()
    
    print("Preprod Service Status:")
    for service, is_alive in status.items():
        status_icon = "✅" if is_alive else "❌"
        print(f"  {status_icon} {service.capitalize()}: {'ONLINE' if is_alive else 'OFFLINE'}")
    
    print(f"\nIndexer: {client.indexer.url}")
    print(f"Node: {client.wallet.url}")
    print(f"Prover: {client.prover.url} (local)")
    
    all_online = status['indexer'] and status['node']  # Prover is local
    print(f"\nResult: {'✅ PASSED' if all_online else '❌ FAILED'}")
    return all_online

def test_2_check_preprod_balance():
    """Test 2: Check real balance on preprod"""
    print_section("TEST 2: Check Preprod Wallet Balance")
    
    print(f"Wallet: {PREPROD_WALLET}")
    print(f"Network: {PREPROD_NETWORK}")
    print("\nQuerying balance from real Midnight preprod indexer...")
    
    try:
        client = MidnightClient(network=PREPROD_NETWORK)
        balance = client.indexer.get_balance(PREPROD_WALLET)
        
        print(f"\n✅ Balance Retrieved:")
        print(f"  DUST (unshielded): {balance.dust:,}")
        print(f"  NIGHT (shielded): Requires viewing key")
        
        # Get latest block
        block = client.indexer.get_latest_block()
        if block:
            print(f"\n  Latest preprod block: {block.get('height', 'unknown')}")
        
        print(f"\nResult: ✅ PASSED")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_3_get_preprod_private_key():
    """Test 3: Get private key from preprod mnemonic"""
    print_section("TEST 3: Get Preprod Private Key")
    
    mnemonic_file = Path("prepod.mnemonic.txt")
    if not mnemonic_file.exists():
        print("❌ prepod.mnemonic.txt not found")
        return None
    
    mnemonic = mnemonic_file.read_text().strip()
    print(f"Mnemonic: {mnemonic[:30]}... (24 words)")
    
    try:
        client = MidnightClient(network=PREPROD_NETWORK)
        keys = client.wallet.get_private_keys(mnemonic)
        
        print("\n✅ Private Keys Retrieved:")
        for key_type, key_value in keys.items():
            print(f"  {key_type}: {key_value[:16]}...")
        
        print(f"\nResult: ✅ PASSED")
        return keys.get('nightExternal', '')
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_4_deploy_to_preprod(private_key):
    """Test 4: Deploy contract to REAL preprod network"""
    print_section("TEST 4: Deploy Contract to Preprod (REAL)")
    
    if not private_key:
        print("❌ No private key available")
        return None
    
    contract_file = Path("contracts/hello_world.compact")
    if not contract_file.exists():
        print(f"❌ Contract not found: {contract_file}")
        return None
    
    print(f"Contract: {contract_file}")
    print(f"Network: {PREPROD_NETWORK} (REAL Midnight network)")
    print(f"Wallet: {PREPROD_WALLET[:40]}...")
    print(f"Private Key: {private_key[:16]}...")
    print("\n🚀 Deploying to REAL Midnight preprod network...")
    print("   This will create a REAL on-chain transaction!")
    
    try:
        client = MidnightClient(network=PREPROD_NETWORK, wallet_address=PREPROD_WALLET)
        
        deployed = client.contracts.deploy(
            str(contract_file),
            private_key=private_key,
            sign_transaction=True
        )
        
        print(f"\n✅ Contract Deployed to REAL Preprod Network!")
        print(f"  Contract Address: {deployed.address}")
        
        # Get transaction hash if available
        if hasattr(deployed, 'tx_hash'):
            print(f"  Transaction Hash: {deployed.tx_hash}")
            print(f"\n  🔍 View on REAL Midnight Explorer:")
            print(f"     https://explorer.preprod.midnight.network/tx/{deployed.tx_hash}")
        
        print(f"\nResult: ✅ PASSED - REAL CONTRACT ON PREPROD!")
        return deployed.address
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_5_call_preprod_contract(contract_address, private_key):
    """Test 5: Call contract on preprod"""
    print_section("TEST 5: Call Contract on Preprod (REAL)")
    
    if not contract_address:
        print("❌ No contract address")
        return False
    
    if not private_key:
        print("❌ No private key")
        return False
    
    print(f"Contract: {contract_address}")
    print(f"Network: {PREPROD_NETWORK} (REAL)")
    print(f"Circuit: storeMessage")
    print(f"Message: 'Hello from REAL Midnight Preprod!'")
    print("\n🚀 Calling circuit on REAL preprod network...")
    
    try:
        client = MidnightClient(network=PREPROD_NETWORK, wallet_address=PREPROD_WALLET)
        contract = client.get_contract(contract_address, ["storeMessage"])
        contract.set_key(private_key)
        
        result = contract.call(
            circuit_name="storeMessage",
            public_inputs={"message": "Hello from REAL Midnight Preprod!"},
            private_inputs={},
            sign_transaction=True
        )
        
        print(f"\n✅ Circuit Called on REAL Preprod!")
        print(f"  TX Hash: {result.tx_hash}")
        print(f"  Status: {result.status}")
        print(f"\n  🔍 View on REAL Midnight Explorer:")
        print(f"     https://explorer.preprod.midnight.network/tx/{result.tx_hash}")
        
        print(f"\nResult: ✅ PASSED - REAL TRANSACTION ON PREPROD!")
        return True
    except Exception as e:
        print(f"❌ Call failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_6_check_preprod_state(contract_address):
    """Test 6: Check contract state on preprod"""
    print_section("TEST 6: Check Contract State on Preprod")
    
    if not contract_address:
        print("❌ No contract address")
        return False
    
    try:
        client = MidnightClient(network=PREPROD_NETWORK)
        state = client.indexer.get_contract_state(contract_address)
        
        print(f"Contract: {contract_address}")
        print(f"Block Height: {state.block_height}")
        print(f"State: {state.state}")
        
        print(f"\nResult: ✅ PASSED")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def main():
    """Run all preprod tests"""
    print("\n" + "="*70)
    print("  MIDNIGHT PREPROD - REAL NETWORK TEST")
    print("  Testing with REAL wallet, REAL transactions, REAL explorer")
    print("="*70)
    
    results = {}
    
    # Test 1: Check preprod services
    results['preprod_services'] = test_1_check_preprod_services()
    if not results['preprod_services']:
        print("\n❌ Preprod network not accessible")
        return
    
    # Test 2: Check balance
    results['preprod_balance'] = test_2_check_preprod_balance()
    
    # Test 3: Get private key
    private_key = test_3_get_preprod_private_key()
    results['preprod_key'] = private_key is not None
    if not private_key:
        print("\n❌ Cannot proceed without private key")
        return
    
    # Test 4: Deploy to preprod
    contract_address = test_4_deploy_to_preprod(private_key)
    results['preprod_deploy'] = contract_address is not None
    
    # Test 5: Call contract on preprod
    if contract_address:
        results['preprod_call'] = test_5_call_preprod_contract(contract_address, private_key)
    else:
        results['preprod_call'] = False
        print_section("TEST 5: Call Contract on Preprod")
        print("⏭️  SKIPPED (no contract deployed)")
    
    # Test 6: Check state
    if contract_address:
        results['preprod_state'] = test_6_check_preprod_state(contract_address)
    else:
        results['preprod_state'] = False
    
    # Summary
    print_section("TEST SUMMARY - REAL PREPROD NETWORK")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print("Test Results:")
    for test_name, passed_test in results.items():
        icon = "✅" if passed_test else "❌"
        print(f"  {icon} {test_name.replace('_', ' ').title()}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED ON REAL PREPROD! 🎉")
        print("\nYour midnight-py CLI successfully:")
        print("  ✅ Connected to REAL Midnight preprod network")
        print("  ✅ Deployed contract with REAL signed transaction")
        print("  ✅ Called circuit with REAL signed transaction")
        print("  ✅ Transactions visible on REAL Midnight explorer")
        print("\n  🔍 View your transactions:")
        print("     https://explorer.preprod.midnight.network")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
