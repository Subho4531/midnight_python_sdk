#!/usr/bin/env python3
"""
Verification script for CLI balance fixes.
Run this to confirm all changes are working correctly.
"""

import sys
from midnight_py.client import MidnightClient
from midnight_py.indexer import IndexerClient
from midnight_py.models import Balance

def test_indexer_url():
    """Verify indexer URL is v4."""
    print("Testing indexer URL configuration...")
    client = MidnightClient(network="local")
    
    expected_url = "http://127.0.0.1:8088/api/v4/graphql"
    actual_url = client.indexer.url
    
    if actual_url == expected_url:
        print(f"  ✓ Indexer URL correct: {actual_url}")
        return True
    else:
        print(f"  ✗ Indexer URL wrong: {actual_url}")
        print(f"    Expected: {expected_url}")
        return False

def test_balance_model():
    """Verify Balance model exists and works."""
    print("Testing Balance model...")
    try:
        bal = Balance(dust=1000, night=5000000)
        if bal.dust == 1000 and bal.night == 5000000:
            print(f"  ✓ Balance model works: {bal}")
            return True
        else:
            print(f"  ✗ Balance model values incorrect")
            return False
    except Exception as e:
        print(f"  ✗ Balance model failed: {e}")
        return False

def test_indexer_methods():
    """Verify IndexerClient has required methods."""
    print("Testing IndexerClient methods...")
    indexer = IndexerClient(
        url="http://127.0.0.1:8088/api/v4/graphql",
        network_id="undeployed"
    )
    
    required_methods = [
        'get_balance',
        'get_latest_block',
        'get_contract_state',
        'get_transaction',
        'is_alive'
    ]
    
    all_present = True
    for method in required_methods:
        if hasattr(indexer, method):
            print(f"  ✓ Method exists: {method}")
        else:
            print(f"  ✗ Method missing: {method}")
            all_present = False
    
    return all_present

def test_cli_import():
    """Verify CLI module imports without errors."""
    print("Testing CLI module import...")
    try:
        from midnight_py import cli
        print(f"  ✓ CLI module imported successfully")
        
        # Check for main commands
        if hasattr(cli, 'app'):
            print(f"  ✓ CLI app exists")
            return True
        else:
            print(f"  ✗ CLI app missing")
            return False
    except Exception as e:
        print(f"  ✗ CLI import failed: {e}")
        return False

def test_network_configs():
    """Verify all network configs use correct URLs."""
    print("Testing network configurations...")
    from midnight_py.client import NETWORKS
    
    all_correct = True
    for network_name, config in NETWORKS.items():
        if network_name in ["local", "undeployed"]:
            expected = "http://127.0.0.1:8088/api/v4/graphql"
        else:
            # Other networks should have v4 in their URLs
            expected = "/api/v4/graphql"
        
        if expected in config.indexer_url:
            print(f"  ✓ {network_name}: {config.indexer_url}")
        else:
            print(f"  ✗ {network_name}: {config.indexer_url}")
            all_correct = False
    
    return all_correct

def main():
    """Run all verification tests."""
    print("=" * 70)
    print("CLI Balance Fix Verification")
    print("=" * 70)
    print()
    
    tests = [
        ("Indexer URL", test_indexer_url),
        ("Balance Model", test_balance_model),
        ("IndexerClient Methods", test_indexer_methods),
        ("CLI Import", test_cli_import),
        ("Network Configs", test_network_configs),
    ]
    
    results = []
    for test_name, test_func in tests:
        print()
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ✗ Test crashed: {e}")
            results.append((test_name, False))
    
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    print()
    
    if passed == total:
        print("🎉 All fixes verified successfully!")
        print()
        print("Next steps:")
        print("  1. Start services: docker-compose up -d")
        print("  2. Test CLI: midnight-py status")
        print("  3. Check balance: midnight-py balance <your_address>")
        print("  4. View block: midnight-py block")
        return 0
    else:
        print("⚠️  Some tests failed. Review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
