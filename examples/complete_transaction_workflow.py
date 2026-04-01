#!/usr/bin/env python3
"""
Complete Transaction Workflow Demo
Demonstrates the full lifecycle: submit -> pending -> confirmed
"""

import time
import httpx
from pathlib import Path
from midnight_py import MidnightClient


def check_transaction_status(tx_hash: str) -> dict:
    """Check transaction status"""
    try:
        response = httpx.get(f"http://localhost:9944/tx/{tx_hash}", timeout=10.0)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def main():
    print("=" * 70)
    print("  Complete Transaction Workflow Demo")
    print("  Midnight Python SDK - Production Ready")
    print("=" * 70)
    print()
    
    # Step 1: Initialize client
    print("[Step 1] Initialize Midnight Client")
    print("-" * 70)
    
    client = MidnightClient(
        network="undeployed",
        wallet_address="mn_addr_undeployed1zaa268rc7sjz0ctscrsy7mp2ne7khfz8wu2uqsu4msfvxnlt6qfsmfrhr0",
        proof_server_url="http://localhost:6300",
    )
    
    print(f"[OK] Client initialized")
    print(f"[OK] Wallet: {client.wallet_address[:40]}...")
    print(f"[OK] Proof server: {client.prover.url}")
    print()
    
    # Step 2: Train model (if needed)
    print("[Step 2] Prepare ML Model")
    print("-" * 70)
    
    model_path = Path.home() / ".midnight" / "models" / "iris_rf.joblib"
    if not model_path.exists():
        print("Training iris classifier...")
        client.ai.train_iris()
    else:
        print("[OK] Model already trained")
    print()
    
    # Step 3: Get private key
    print("[Step 3] Derive Private Key")
    print("-" * 70)
    
    mnemonic_file = Path("mnemonic.txt")
    if not mnemonic_file.exists():
        print("[ERROR] mnemonic.txt not found")
        return
    
    mnemonic = mnemonic_file.read_text().strip()
    keys = client.wallet.get_private_keys(mnemonic)
    private_key = keys['nightExternal']
    
    print(f"[OK] Private key derived: {private_key[:16]}...")
    print()
    
    # Step 4: Run inference and submit transaction
    print("[Step 4] Run ZK Inference & Submit Transaction")
    print("-" * 70)
    
    features = [5.1, 3.5, 1.4, 0.2]  # Iris setosa sample
    print(f"Input features: {features}")
    print("Generating ZK proof...")
    
    result = client.ai.predict_private(
        features=features,
        sign_transaction=True,
        private_key=private_key
    )
    
    tx_hash = result.transaction_hash
    
    print()
    print(f"[OK] Prediction: {result.prediction}")
    print(f"[OK] Confidence: {result.confidence * 100:.2f}%")
    print(f"[OK] Proof hash: {result.proof_hash[:32]}...")
    print(f"[OK] Transaction hash: {tx_hash}")
    print()
    
    # Step 5: Check initial status (should be pending)
    print("[Step 5] Check Transaction Status (Initial)")
    print("-" * 70)
    
    tx_data = check_transaction_status(tx_hash)
    if tx_data:
        print(f"Status: {tx_data['status']} (pending)")
        print(f"Timestamp: {tx_data['timestamp']}")
        print(f"Block height: {tx_data.get('block_height', 'N/A')}")
    else:
        print("[ERROR] Transaction not found")
        return
    print()
    
    # Step 6: Wait for auto-confirmation
    print("[Step 6] Wait for Auto-Confirmation")
    print("-" * 70)
    print("Waiting 4 seconds for contract execution...")
    
    for i in range(4):
        time.sleep(1)
        print(f"  {i+1}/4 seconds...")
    
    print()
    
    # Step 7: Check final status (should be confirmed)
    print("[Step 7] Check Transaction Status (Final)")
    print("-" * 70)
    
    tx_data = check_transaction_status(tx_hash)
    if tx_data:
        status = tx_data['status']
        
        if status == 'confirmed':
            print(f"Status: {status} [CONFIRMED]")
            print(f"Confirmed at: {tx_data.get('confirmed_at', 'N/A')}")
        elif status == 'rejected':
            print(f"Status: {status} [REJECTED]")
            print(f"Reason: {tx_data.get('error', 'Unknown')}")
        else:
            print(f"Status: {status}")
        
        print(f"Block height: {tx_data.get('block_height', 'N/A')}")
    else:
        print("[ERROR] Transaction not found")
        return
    print()
    
    # Step 8: View in explorer
    print("[Step 8] View in Explorer")
    print("-" * 70)
    
    explorer_url = f"http://localhost:8088/tx/{tx_hash}"
    print(f"Explorer URL: {explorer_url}")
    print()
    
    # Summary
    print("=" * 70)
    print("  Workflow Complete!")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  Transaction: {tx_hash[:32]}...")
    print(f"  Status: {tx_data['status']}")
    print(f"  Prediction: {result.prediction}")
    print(f"  Confidence: {result.confidence * 100:.2f}%")
    print(f"  Explorer: {explorer_url}")
    print()
    print("Key Features Demonstrated:")
    print("  [OK] Real ML inference (sklearn)")
    print("  [OK] Real ZK proof generation")
    print("  [OK] Real transaction signing")
    print("  [OK] Real blockchain submission")
    print("  [OK] Automatic contract execution")
    print("  [OK] Transaction status tracking")
    print("  [OK] Explorer integration")
    print()
    print("Next Steps:")
    print("  - View transaction in explorer (open URL above)")
    print("  - List all transactions: midnight-py tx list")
    print("  - Check status: midnight-py tx status <tx_hash>")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
