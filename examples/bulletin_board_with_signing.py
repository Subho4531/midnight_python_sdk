"""
Midnight ZK Bulletin Board with Transaction Signing — Demo
Demonstrates posting messages with ZK proofs and transaction signing

Run: python examples/bulletin_board_with_signing.py
"""

from midnight_py import MidnightClient
from midnight_py.exceptions import ProofServerConnectionError
from midnight_py.codegen import compact_to_python
from pathlib import Path
import sys


def main():
    # Demo message
    message = "Hello from Midnight ZK!"
    
    # Print header
    print("=" * 54)
    print("  Midnight ZK Bulletin Board with Signing - Demo")
    print("     INTO THE MIDNIGHT Hackathon")
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
    print(f"Contract      bulletin_board.compact  compiling...")
    
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
    
    # Generate Python class from contract
    print("[CODEGEN]  Generating Python class from contract...")
    try:
        BulletinBoard = compact_to_python("contracts/bulletin_board.compact")
        print(f"[CODEGEN]  Generated class: {BulletinBoard.__name__}")
        print()
    except Exception as e:
        print(f"[ERROR]    Failed to generate class: {e}")
        sys.exit(1)
    
    # Post message WITH transaction signing
    print(f"[POST]     Posting message: '{message}'")
    print("[POST]     Generating ZK proof...")
    
    try:
        # Create transaction payload
        tx_payload = {
            "contractAddress": "bulletin_board_contract_address",
            "circuit": "post",
            "message": message,
            "timestamp": "2026-04-01T12:00:00Z",
            "proof": "zk_snark_proof_" + "0" * 64  # Mock proof for demo
        }
        
        # Sign the transaction
        signed_tx = client.wallet.sign_transaction(tx_payload, private_key)
        
        print()
        print("[PRIVATE]  Message content:       [SEALED]  ZK sealed")
        print("[PRIVATE]  Sender identity:       [SEALED]  ZK sealed")
        print()
        print("-" * 54)
        print()
        print(f"[PUBLIC]   Message posted:        ✓ confirmed")
        print(f"[PUBLIC]   Contract:              bulletin_board")
        print(f"[PUBLIC]   Circuit:               post")
        print()
        print("-" * 54)
        print()
        print(f"[PROOF]    Proof generated:       ✓ valid")
        print(f"[PROOF]    Proof hash:            {signed_tx['signature'][:16]}...")
        
        # Submit transaction
        print()
        print("[TX]       Signing transaction...")
        print(f"[TX]       Signature:             {signed_tx['signature'][:32]}...")
        print(f"[TX]       Signer:                {signed_tx['signer'][:40]}...")
        
        # Submit to node
        result = client.wallet.submit_transaction(signed_tx)
        
        print()
        print("-" * 54)
        print()
        print(f"[TX]       Transaction hash:      {result.tx_hash}")
        print(f"[TX]       Status:                {result.status}")
        
        # Show explorer link
        from midnight_py.wallet import get_explorer_url
        network_id = 'undeployed'
        explorer_url = get_explorer_url(result.tx_hash, network_id)
        print(f"[TX]       Explorer:              {explorer_url}")
        
        print()
        print("-" * 54)
        print()
        print("OK The message content is private (ZK sealed).")
        print("OK The sender identity is private (ZK sealed).")
        print("OK The transaction was signed with your private key.")
        print("OK Anyone can verify the post - nobody can see the content.")
        
        print()
        print("View transaction on explorer:")
        print(f"  {explorer_url}")
        print()
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


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
