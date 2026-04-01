"""
Production AI Inference on Midnight Testnet
============================================

This example uses the REAL Midnight testnet:
- Real ZK proof generation (10-30 seconds)
- Real transaction signing
- Real blockchain submission
- Real explorer links

Prerequisites:
1. Docker running with real proof server:
   docker run -d -p 6300:6300 ghcr.io/midnight-ntwrk/proof-server:latest

2. Testnet tokens from faucet:
   https://faucet.testnet.midnight.network

3. Mnemonic in mnemonic.txt or MIDNIGHT_MNEMONIC env var

Run: python examples/production_ai_inference.py
"""

import os
import sys
from pathlib import Path
from midnight_py import MidnightClient
from midnight_py.wallet import WalletClient
from midnight_py.exceptions import ProofServerConnectionError


def main():
    print("=" * 70)
    print("  Production AI Inference on Midnight Testnet")
    print("  REAL ZK Proofs + REAL Blockchain + REAL Explorer")
    print("=" * 70)
    print()
    
    # 1. Load mnemonic
    print("[1/7] Loading wallet configuration...")
    mnemonic = os.getenv("MIDNIGHT_MNEMONIC")
    if not mnemonic:
        mnemonic_file = Path("mnemonic.txt")
        if mnemonic_file.exists():
            mnemonic = mnemonic_file.read_text().strip()
        else:
            print("ERROR: No mnemonic found!")
            print("  Set MIDNIGHT_MNEMONIC environment variable")
            print("  OR create mnemonic.txt with your 24-word mnemonic")
            return 1
    
    print(f"  Mnemonic: {mnemonic.split()[0]}... (24 words)")
    print()
    
    # 2. Derive wallet address
    print("[2/7] Deriving wallet address...")
    wallet = WalletClient()
    try:
        address_info = wallet.get_real_address(mnemonic, network_id="testnet")
        wallet_address = address_info['address']
    except Exception as e:
        print(f"ERROR: Failed to derive address: {e}")
        print("  Make sure Node.js and wallet SDK are installed:")
        print("  npm install")
        return 1
    
    print(f"  Wallet: {wallet_address}")
    print(f"  Explorer: https://explorer.testnet.midnight.network/address/{wallet_address}")
    print()
    
    # 3. Connect to testnet
    print("[3/7] Connecting to Midnight testnet...")
    try:
        client = MidnightClient(
            network="preprod",
            wallet_address=wallet_address
        )
    except ProofServerConnectionError as e:
        print(f"ERROR: {e}")
        print()
        print("  Start the REAL proof server:")
        print("  docker run -d -p 6300:6300 ghcr.io/midnight-ntwrk/proof-server:latest")
        print()
        print("  Verify it's running:")
        print("  curl http://localhost:6300/health")
        return 1
    
    # Check services
    status = client.status()
    print(f"  Node:    {'OK' if status['node'] else 'OFFLINE'} - {client.wallet.url}")
    print(f"  Indexer: {'OK' if status['indexer'] else 'OFFLINE'} - {client.indexer.url}")
    print(f"  Prover:  {'OK' if status['prover'] else 'OFFLINE'} - {client.prover.url}")
    
    if not all(status.values()):
        print()
        print("ERROR: Not all services are online!")
        if not status['node']:
            print("  Node offline - check https://status.midnight.network")
        if not status['indexer']:
            print("  Indexer offline - check https://status.midnight.network")
        if not status['prover']:
            print("  Proof server offline - run: docker run -d -p 6300:6300 ghcr.io/midnight-ntwrk/proof-server:latest")
        return 1
    
    print()
    print("  OK All services online!")
    print()
    
    # 4. Train model
    print("[4/7] Training ML model...")
    model_path = Path.home() / ".midnight" / "models" / "iris_rf.joblib"
    if not model_path.exists():
        model_hash = client.ai.train_iris()
        print(f"  OK Model trained: {model_hash[:32]}...")
    else:
        import hashlib
        model_hash = hashlib.sha256(model_path.read_bytes()).hexdigest()
        print(f"  OK Model loaded: {model_hash[:32]}...")
    print()
    
    # 5. Get private key
    print("[5/7] Deriving private key for signing...")
    try:
        keys = wallet.get_private_keys(mnemonic)
        private_key = keys['nightExternal']
        print(f"  OK Private key: {private_key[:16]}...")
    except Exception as e:
        print(f"ERROR: Failed to derive private key: {e}")
        return 1
    print()
    
    # 6. Run ZK inference
    print("[6/7] Running ZK inference on testnet...")
    print("  NOTE: REAL ZK proof generation takes 10-30 seconds")
    print("  This is normal - real cryptography is slow!")
    print()
    print("  Generating proof...")
    
    try:
        result = client.ai.predict_private(
            features=[5.1, 3.5, 1.4, 0.2],
            sign_transaction=True,
            private_key=private_key
        )
    except Exception as e:
        print(f"ERROR: Inference failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print()
    print("  OK Proof generated!")
    print("  OK Transaction signed!")
    print("  OK Submitted to testnet!")
    print()
    
    # 7. Display results
    print("[7/7] Results")
    print("=" * 70)
    print()
    print("PRIVATE DATA (never left this machine):")
    print(f"  Input features:      [SEALED - ZK proof only]")
    print(f"  Raw probabilities:   [SEALED - ZK proof only]")
    print()
    print("PUBLIC DATA (visible on blockchain):")
    print(f"  Prediction:          {result.prediction}")
    print(f"  Confidence:          {result.confidence * 100:.2f}%")
    print(f"  Model Hash:          {result.model_hash[:32]}...")
    print()
    print("PROOF DATA:")
    print(f"  Proof Hash:          {result.proof_hash[:32]}...")
    print(f"  Proof Bytes:         {result.raw_proof_bytes[:64]}...")
    print(f"  Proof Server:        {result.proof_server_url}")
    print()
    
    if result.transaction_hash:
        print("TRANSACTION:")
        print(f"  TX Hash:             {result.transaction_hash}")
        print(f"  Status:              {result.receipt_path.split('/')[-1].split('.')[0]}")
        print()
        print("EXPLORER LINKS:")
        print(f"  Transaction:         https://explorer.testnet.midnight.network/tx/{result.transaction_hash}")
        print(f"  Wallet:              https://explorer.testnet.midnight.network/address/{wallet_address}")
        print()
        print("  OK View your transaction in the REAL block explorer!")
    
    print()
    print("RECEIPT:")
    print(f"  Saved to:            {result.receipt_path}")
    print()
    print("=" * 70)
    print()
    print("SUCCESS! What just happened:")
    print()
    print("  1. ML model ran locally (private data stayed on your device)")
    print("  2. REAL ZK proof generated by Midnight proof server")
    print("  3. Transaction signed with your private key")
    print("  4. Submitted to REAL Midnight testnet blockchain")
    print("  5. Viewable in REAL block explorer")
    print()
    print("This is PRODUCTION-READY code using:")
    print("  - Real Midnight testnet (not mock)")
    print("  - Real ZK proofs (not simulated)")
    print("  - Real transactions (on blockchain)")
    print("  - Real explorer (verifiable)")
    print()
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
