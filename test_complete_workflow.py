#!/usr/bin/env python3
"""
Complete End-to-End Test of Midnight Python SDK

Tests:
1. Network status check
2. Balance query
3. Contract compilation
4. Contract deployment with signing
5. Circuit call with signing
6. Transaction verification
7. Explorer verification
"""

import sys
import time
from pathlib import Path
from midnight_py import MidnightClient
from midnight_py.exceptions import MidnightSDKError

def print_section(title):
    """Print a section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def test_1_network_status():
    """Test 1: Check network status"""
    print_section("TEST 1: Network Status Check")
    
    try:
        client = MidnightClient(network="undeployed")
        status = client.status()
        
        print("Service Status:")
        for service, is_alive in status.items():
            status_icon = "✅" if is_alive else "❌"
            print(f"  {status_icon} {service.capitalize()}: {'ONLINE' if is_alive else 'OFFLINE'}")
        
        all_online = all(status.values())
        print(f"\nResult: {'✅ PASSED' if all_online else '❌ FAILED'}")
        return all_online
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_2_balance_check():
    """Test 2: Check wallet balance"""
    print_section("TEST 2: Balance Check")
    
    # Your undeployed wallet address
    address = "mn_addr_undeployed1x2w98jvk0wxppn3a3mlfw3ep736tdn7k2rhj7kjv292tcl6a0hyq3g5xa0"
    
    try:
        client = MidnightClient(network="undeployed")
        balance = client.indexer.get_balance(address)
        
        print(f"Wallet: {address[:40]}...")
        print(f"DUST:  {balance.dust:,}")
        print(f"NIGHT: {balance.night:,}")
        
        has_funds = balance.dust > 0 or balance.night > 0
        print(f"\nResult: {'✅ PASSED' if has_funds else '⚠️  No funds (run fund_wallet.py)'}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_3_contract_compilation():
    """Test 3: Check if contract is compiled"""
    print_section("TEST 3: Contract Compilation Check")
    
    contract_path = Path("contracts/hello_world.compact")
    compiled_path = Path("contracts/managed/hello_world/contract/index.js")
    
    print(f"Contract: {contract_path}")
    print(f"Compiled: {compiled_path}")
    
    if not contract_path.exists():
        print(f"\n❌ Contract not found: {contract_path}")
        return False
    
    if not compiled_path.exists():
        print(f"\n⚠️  Contract not compiled")
        print(f"   Run: npx compact compile {contract_path} contracts/managed/hello_world")
        return False
    
    print(f"\n✅ Contract is compiled and ready")
    return True

def test_4_deploy_contract():
    """Test 4: Deploy contract with signing"""
    print_section("TEST 4: Deploy Contract with Signing")
    
    contract_path = "contracts/hello_world.compact"
    wallet_address = "mn_addr_undeployed1x2w98jvk0wxppn3a3mlfw3ep736tdn7k2rhj7kjv292tcl6a0hyq3g5xa0"
    
    # For testing, we'll use a test private key
    # In production, this would come from secure storage
    private_key = "test_key_for_signing"
    
    print(f"Contract: {contract_path}")
    print(f"Wallet: {wallet_address[:40]}...")
    print(f"Network: undeployed")
    print(f"\n🚀 Deploying contract with signed transaction...")
    
    try:
        client = MidnightClient(network="undeployed", wallet_address=wallet_address)
        
        deployed = client.contracts.deploy(
            contract_path,
            private_key=private_key,
            sign_transaction=True
        )
        
        print(f"\n✅ Contract Deployed!")
        print(f"  Contract Address: {deployed.address}")
        
        if hasattr(deployed, 'tx_hash'):
            print(f"  Transaction Hash: {deployed.tx_hash}")
            print(f"\n  🔍 View on Explorer:")
            print(f"     http://localhost:8088/tx/{deployed.tx_hash}")
        
        print(f"\nResult: ✅ PASSED")
        return deployed.address
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_5_call_circuit(contract_address):
    """Test 5: Call circuit with signing"""
    print_section("TEST 5: Call Circuit with Signing")
    
    if not contract_address:
        print("⏭️  SKIPPED (no contract deployed)")
        return False
    
    wallet_address = "mn_addr_undeployed1x2w98jvk0wxppn3a3mlfw3ep736tdn7k2rhj7kjv292tcl6a0hyq3g5xa0"
    private_key = "test_key_for_signing"
    
    print(f"Contract: {contract_address}")
    print(f"Circuit: storeMessage")
    print(f"Message: 'Hello from Python SDK!'")
    print(f"\n🚀 Calling circuit with signed transaction...")
    
    try:
        client = MidnightClient(network="undeployed", wallet_address=wallet_address)
        contract = client.get_contract(contract_address, ["storeMessage"])
        contract.set_key(private_key)
        
        result = contract.call(
            circuit_name="storeMessage",
            public_inputs={"message": "Hello from Python SDK!"},
            private_inputs={},
            sign_transaction=True
        )
        
        print(f"\n✅ Circuit Called!")
        print(f"  TX Hash: {result.tx_hash}")
        print(f"  Status: {result.status}")
        print(f"\n  🔍 View on Explorer:")
        print(f"     http://localhost:8088/tx/{result.tx_hash}")
        
        print(f"\nResult: ✅ PASSED")
        return result.tx_hash
    except Exception as e:
        print(f"\n❌ Call failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_6_verify_transaction(tx_hash):
    """Test 6: Verify transaction on chain"""
    print_section("TEST 6: Verify Transaction")
    
    if not tx_hash:
        print("⏭️  SKIPPED (no transaction)")
        return False
    
    print(f"Transaction: {tx_hash}")
    print(f"\n🔍 Querying indexer...")
    
    try:
        client = MidnightClient(network="undeployed")
        tx = client.indexer.get_transaction(tx_hash)
        
        if tx:
            print(f"\n✅ Transaction Found!")
            print(f"  Block Height: {tx.get('blockHeight', 'pending')}")
            print(f"  Status: {tx.get('status', 'unknown')}")
            print(f"  Timestamp: {tx.get('timestamp', 'N/A')}")
            print(f"\nResult: ✅ PASSED")
            return True
        else:
            print(f"\n⚠️  Transaction not found (may still be pending)")
            print(f"   Wait a few seconds and check explorer")
            return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def test_7_check_explorer():
    """Test 7: Verify explorer is accessible"""
    print_section("TEST 7: Explorer Verification")
    
    explorer_url = "http://localhost:8088"
    
    print(f"Explorer URL: {explorer_url}")
    print(f"\n🔍 Checking accessibility...")
    
    try:
        import httpx
        response = httpx.get(explorer_url, timeout=5.0)
        
        if response.status_code == 200:
            print(f"\n✅ Explorer is accessible!")
            print(f"  Status Code: {response.status_code}")
            print(f"\n  🌐 Open in browser:")
            print(f"     {explorer_url}")
            print(f"\nResult: ✅ PASSED")
            return True
        else:
            print(f"\n⚠️  Explorer returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"\n❌ Explorer not accessible: {e}")
        print(f"   Make sure Docker services are running:")
        print(f"   docker-compose up -d")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  MIDNIGHT PYTHON SDK - COMPLETE WORKFLOW TEST")
    print("  Testing: Status → Balance → Deploy → Call → Verify → Explorer")
    print("="*70)
    
    results = {}
    
    # Test 1: Network Status
    results['network_status'] = test_1_network_status()
    if not results['network_status']:
        print("\n❌ Network services are offline. Start them with:")
        print("   docker-compose up -d")
        return
    
    # Test 2: Balance Check
    results['balance_check'] = test_2_balance_check()
    
    # Test 3: Contract Compilation
    results['contract_compiled'] = test_3_contract_compilation()
    if not results['contract_compiled']:
        print("\n⚠️  Compile the contract first, then run this test again")
        return
    
    # Test 4: Deploy Contract
    contract_address = test_4_deploy_contract()
    results['contract_deploy'] = contract_address is not None
    
    # Test 5: Call Circuit
    tx_hash = None
    if contract_address:
        tx_hash = test_5_call_circuit(contract_address)
        results['circuit_call'] = tx_hash is not None
    else:
        results['circuit_call'] = False
        print_section("TEST 5: Call Circuit with Signing")
        print("⏭️  SKIPPED (no contract deployed)")
    
    # Test 6: Verify Transaction
    if tx_hash:
        results['tx_verify'] = test_6_verify_transaction(tx_hash)
    else:
        results['tx_verify'] = False
        print_section("TEST 6: Verify Transaction")
        print("⏭️  SKIPPED (no transaction)")
    
    # Test 7: Check Explorer
    results['explorer'] = test_7_check_explorer()
    
    # Summary
    print_section("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print("Test Results:")
    for test_name, passed_test in results.items():
        icon = "✅" if passed_test else "❌"
        print(f"  {icon} {test_name.replace('_', ' ').title()}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\nYour Midnight Python SDK is working perfectly!")
        print("\n✅ Network services online")
        print("✅ Contract deployment with signing")
        print("✅ Circuit calls with signing")
        print("✅ Transactions stored on-chain")
        print("✅ Explorer accessible")
        print("\n🌐 View your transactions:")
        print("   http://localhost:8088")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("\nCheck the errors above and:")
        print("  1. Make sure Docker services are running: docker-compose up -d")
        print("  2. Compile contracts: npx compact compile contracts/hello_world.compact contracts/managed/hello_world")
        print("  3. Fund wallet if needed: python fund_wallet.py")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
