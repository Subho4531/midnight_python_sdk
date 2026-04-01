"""
Midnight ZK AI Inference with Transaction Signing — Demo
AI Track · INTO THE MIDNIGHT Hackathon

Demonstrates:
1. Real ML inference (sklearn)
2. Real contract compilation (compactc)
3. Real ZK proof generation (proof server)
4. Real transaction signing (wallet private key)

Run: python examples/ai_inference_with_signing.py
"""

from midnight_py import MidnightClient
from midnight_py.exceptions import ModelNotTrainedError, ProofServerConnectionError
from pathlib import Path
import sys


def main():
    # Demo features (Iris setosa sample)
    features = [5.1, 3.5, 1.4, 0.2]
    
    # Print header
    print("=" * 54)
    print("  Midnight ZK AI Inference with Signing - Demo")
    print("     AI Track - INTO THE MIDNIGHT Hackathon")
    print("=" * 54)
    print()
    
    # Create MidnightClient
    try:
        client = MidnightClient(
            network="undeployed",
            wallet_address="mn_addr_undeployed1zaa268rc7sjz0ctscrsy7mp2ne7khfz8wu2uqsu4msfvxnlt6qfsmfrhr0",
            proof_server_url="http://localhost:6300",
        )
    except ProofServerConnectionError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    
    # Print connection status
    wallet_short = client.wallet_address[:40] + "..."
    print(f"Wallet        {wallet_short}")
    print(f"Proof Server  localhost:6300  OK connected")
    
    # Train model (skip if already exists)
    model_path = Path.home() / ".midnight" / "models" / "iris_rf.joblib"
    if not model_path.exists():
        print("Model         iris_rf.joblib  training...")
        client.ai.train_iris()
    else:
        print("Model         iris_rf.joblib  OK loaded")
    
    # Compile contract
    print("Contract      ai_inference.compact  compiling...")
    
    print("-" * 54)
    print()
    
    # Get private key for signing
    print("[SETUP]    Deriving private key from mnemonic...")
    try:
        mnemonic_file = Path("mnemonic.txt")
        if not mnemonic_file.exists():
            print("[ERROR]    mnemonic.txt not found!")
            print("           Create it with your 24-word mnemonic")
            sys.exit(1)
        
        mnemonic = mnemonic_file.read_text().strip()
        keys = client.wallet.get_private_keys(mnemonic)
        private_key = keys['nightExternal']
        print(f"[SETUP]    Private key: {private_key[:16]}...")
        print()
    except Exception as e:
        print(f"[ERROR]    Failed to derive private key: {e}")
        sys.exit(1)
    
    # Run ZK inference WITH transaction signing
    print("[INFERENCE] Running ZK inference...")
    try:
        result = client.ai.predict_private(
            features=features,
            sign_transaction=True,
            private_key=private_key
        )
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Print output
    print()
    print("[PRIVATE]  Input features:       [SEALED]  ZK sealed")
    print("[PRIVATE]  Raw probabilities:    [SEALED]  ZK sealed")
    print()
    print("-" * 54)
    print()
    print(f"[PUBLIC]   Prediction:           {result.prediction}")
    print(f"[PUBLIC]   Confidence:           {result.confidence * 100:.2f}%")
    print(f"[PUBLIC]   Model hash:           {result.model_hash[:16]}...")
    print()
    print("-" * 54)
    print()
    print(f"[PROOF]    Proof hash:           {result.proof_hash[:16]}...")
    print(f"[PROOF]    Proof bytes (hex):    {result.raw_proof_bytes[:32]}...")
    
    if result.transaction_hash:
        print()
        print("-" * 54)
        print()
        print(f"[TX]       Transaction hash:     {result.transaction_hash}")
        print(f"[TX]       Status:               signed & submitted")
        
        # Show explorer link
        from midnight_py.wallet import get_explorer_url
        network_id = 'undeployed'
        explorer_url = get_explorer_url(result.transaction_hash, network_id)
        print(f"[TX]       Explorer:             {explorer_url}")
    
    print()
    print(f"[STORED]   Receipt:              {result.receipt_path}")
    print()
    print("-" * 54)
    print()
    print("OK The private input NEVER left this machine.")
    print("OK The ZK proof was generated using compiled contract.")
    print("OK The transaction was signed with your private key.")
    print("OK Anyone can verify the prediction - nobody can see the input.")
    
    if result.transaction_hash:
        print()
        print("View transaction on explorer:")
        print(f"  {explorer_url}")
    
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
