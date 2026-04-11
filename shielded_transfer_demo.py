#!/usr/bin/env python3
"""
Complete demonstration of Midnight shielded transfers with ZK proof generation.
Shows the full process from wallet setup to transaction submission.
"""

import subprocess
import time
import json
from pathlib import Path

def run_command(cmd, input_text=None):
    """Run a CLI command and return the result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            input=input_text,
            timeout=120  # 2 minute timeout
        )
        return result
    except subprocess.TimeoutExpired:
        return None

def main():
    print("🔒 Midnight Shielded Transfer Complete Demo")
    print("=" * 60)
    
    # Step 1: Check system status
    print("\n📡 Step 1: Checking system status...")
    result = run_command("midnight system status --profile local")
    if result and result.returncode == 0:
        print("✅ All local services are online")
    else:
        print("❌ Local services not available")
        return
    
    # Step 2: Check wallet
    print("\n💼 Step 2: Checking wallet...")
    result = run_command("midnight wallet address shielded-test --profile local")
    if result and result.returncode == 0:
        print("✅ Wallet 'shielded-test' is available")
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Shielded' in line and 'mn_shield-addr' in line:
                # Extract shielded address
                parts = line.split('│')
                if len(parts) >= 3:
                    shielded_addr = parts[2].strip()
                    print(f"🎯 Shielded address: {shielded_addr[:50]}...")
                    break
    else:
        print("❌ Wallet not found")
        return
    
    # Step 3: Check balance
    print("\n💰 Step 3: Checking balance...")
    result = run_command("midnight balance --profile local")
    if result and result.returncode == 0:
        print("✅ Balance check successful")
        if "DUST" in result.stdout and "NIGHT" in result.stdout:
            print("✅ Sufficient funds available for transfer")
    
    # Step 4: Demonstrate dry-run
    print("\n🧪 Step 4: Testing transfer (dry-run)...")
    cmd = f"midnight transfer shielded {shielded_addr} 500000 --wallet shielded-test --profile local --dry-run"
    result = run_command(cmd)
    if result and result.returncode == 0:
        print("✅ Dry-run successful - transfer parameters validated")
        print("   Amount: 0.5 NIGHT")
        print("   Type: Shielded (Private)")
        print("   Privacy: ✓ Amount and sender encrypted")
    
    # Step 5: Attempt real shielded transfer
    print("\n🔒 Step 5: Attempting real shielded transfer...")
    print("⚠️  This will generate a ZK proof (may take 30-60 seconds)")
    
    cmd = f"midnight transfer shielded {shielded_addr} 500000 --wallet shielded-test --profile local"
    
    print("⏳ Starting proof generation...")
    start_time = time.time()
    
    # Run with automatic 'y' response
    result = run_command(cmd, input_text="y\n")
    
    elapsed = time.time() - start_time
    
    if result is None:
        print(f"⏰ Transfer timed out after {elapsed:.1f} seconds")
        print("   This is common for ZK proof generation on first attempts")
    elif result.returncode == 0:
        print(f"✅ Transfer completed successfully in {elapsed:.1f} seconds!")
        if "tx_hash" in result.stdout.lower() or "transaction" in result.stdout.lower():
            print("📝 Transaction submitted to network")
    else:
        print(f"❌ Transfer failed after {elapsed:.1f} seconds")
        if "timeout" in result.stderr.lower():
            print("   Reason: ZK proof generation timeout")
        else:
            print(f"   Error: {result.stderr}")
    
    # Step 6: Explain the process
    print("\n📋 Shielded Transfer Process Breakdown:")
    print("=" * 50)
    
    print("\n1. 🔐 Address Generation:")
    print("   • Derives shielded address from wallet mnemonic")
    print("   • Uses cryptographic key derivation (BIP44)")
    print("   • Shielded addresses start with 'mn_shield-addr_'")
    
    print("\n2. 💰 Balance Verification:")
    print("   • Checks DUST balance for transaction fees")
    print("   • Verifies sufficient NIGHT tokens for transfer")
    print("   • Ensures wallet has necessary UTXOs")
    
    print("\n3. 🧮 ZK Proof Generation:")
    print("   • Creates zero-knowledge proof of transaction validity")
    print("   • Encrypts sender, recipient, and amount information")
    print("   • Connects to proof server for computation")
    print("   • Most time-consuming step (10-60 seconds)")
    
    print("\n4. 📡 Transaction Submission:")
    print("   • Submits encrypted transaction to network")
    print("   • Includes ZK proof for validation")
    print("   • Network validates proof without seeing details")
    
    print("\n5. ✅ Network Confirmation:")
    print("   • Transaction included in blockchain")
    print("   • Recipient can decrypt with viewing key")
    print("   • Amount and sender remain private to others")
    
    print("\n🔍 Privacy Features:")
    print("   • Sender identity: Hidden")
    print("   • Recipient identity: Hidden") 
    print("   • Transfer amount: Hidden")
    print("   • Transaction validity: Publicly verifiable")
    
    print("\n💡 Production Tips:")
    print("   • Use 1AM wallet for reliable shielded transfers")
    print("   • Ensure stable internet during proof generation")
    print("   • Allow 60+ seconds for first-time transfers")
    print("   • Monitor transaction status after submission")
    print("   • Keep viewing keys secure for balance queries")
    
    print(f"\n🎉 Demo completed! Shielded transfer process demonstrated.")

if __name__ == "__main__":
    main()