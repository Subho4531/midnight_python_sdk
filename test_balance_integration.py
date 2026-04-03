#!/usr/bin/env python3
"""
Test balance integration in CLI

This test verifies that the CLI correctly shows:
1. Indexer balance (0 for privacy)
2. Real balance from faucet (1,000 tNIGHT + 19.4 tDUST)
3. Explanation of Midnight's privacy features
"""

import subprocess
import sys

def test_balance_command():
    """Test the balance command shows real balance"""
    
    print("\n" + "="*70)
    print("TESTING BALANCE INTEGRATION")
    print("="*70 + "\n")
    
    address = "mn_addr_preprod1qr0n4n8lhczmnnjv0ryzvcul3dteals0ejjgs7mmpqueh4u9clqssyv3kd"
    
    print("Running: midnight-py balance <address> --network preprod --no-auto\n")
    
    result = subprocess.run(
        ["midnight-py", "balance", address, "--network", "preprod", "--no-auto"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    
    output = result.stdout
    
    print(output)
    
    # Verify key elements are present
    checks = {
        "Shows indexer balance": "Indexer Balance:" in output,
        "Shows DUST as 0": "DUST:  0" in output,
        "Shows NIGHT requires key": "Requires viewing key" in output,
        "Shows real balance": "Your Real Balance" in output,
        "Shows 1,000 tNIGHT": "1,000" in output,
        "Shows 19.4 tDUST": "19,410,900,000" in output or "19.4" in output,
        "Explains privacy": "PRIVACY blockchain" in output,
        "Mentions Lace wallet": "Lace Wallet" in output,
        "Shows explorer link": "explorer.preprod.midnight.network" in output,
    }
    
    print("\n" + "="*70)
    print("VERIFICATION RESULTS")
    print("="*70 + "\n")
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    
    if all_passed:
        print("✅ ALL CHECKS PASSED - Balance integration working!")
        print("\nYour CLI now shows:")
        print("  • Real balance from faucet (1,000 tNIGHT + 19.4 tDUST)")
        print("  • Clear explanation of Midnight's privacy features")
        print("  • Links to Lace wallet and explorer")
        print("\nYou're ready to deploy contracts to preprod!")
    else:
        print("❌ SOME CHECKS FAILED - Review output above")
        return False
    
    print("="*70 + "\n")
    
    return all_passed


if __name__ == "__main__":
    try:
        success = test_balance_command()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
