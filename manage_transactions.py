#!/usr/bin/env python3
"""
Transaction Management CLI
Approve, reject, or check status of transactions
"""

import httpx
import sys
import json
from typing import Optional


def get_transaction(tx_hash: str) -> Optional[dict]:
    """Get transaction details"""
    try:
        response = httpx.get(f"http://localhost:9944/tx/{tx_hash}", timeout=10.0)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching transaction: {e}")
        return None


def list_transactions() -> list:
    """List all transactions"""
    try:
        response = httpx.get("http://localhost:9944/transactions", timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            return data.get("transactions", [])
        return []
    except Exception as e:
        print(f"Error listing transactions: {e}")
        return []


def confirm_transaction(tx_hash: str) -> bool:
    """Confirm/approve a transaction"""
    try:
        response = httpx.post(
            "http://localhost:9944",
            json={
                "id": 1,
                "jsonrpc": "2.0",
                "method": "chain_confirmTransaction",
                "params": [tx_hash]
            },
            headers={"Content-Type": "application/json"},
            timeout=10.0
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("result", {}).get("confirmed", False)
        return False
    except Exception as e:
        print(f"Error confirming transaction: {e}")
        return False


def reject_transaction(tx_hash: str, reason: str = "Rejected by user") -> bool:
    """Reject a transaction"""
    try:
        response = httpx.post(
            "http://localhost:9944",
            json={
                "id": 1,
                "jsonrpc": "2.0",
                "method": "chain_rejectTransaction",
                "params": [tx_hash, reason]
            },
            headers={"Content-Type": "application/json"},
            timeout=10.0
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("result", {}).get("rejected", False)
        return False
    except Exception as e:
        print(f"Error rejecting transaction: {e}")
        return False


def print_transaction(tx: dict):
    """Pretty print transaction details"""
    print(f"\n{'='*70}")
    print(f"Transaction: {tx['hash'][:32]}...")
    print(f"{'='*70}")
    print(f"Status:      {tx['status']}")
    print(f"Timestamp:   {tx['timestamp']}")
    print(f"Block:       {tx.get('block_height', 'N/A')}")
    
    if tx['status'] == 'confirmed':
        print(f"Confirmed:   {tx.get('confirmed_at', 'N/A')}")
    elif tx['status'] == 'rejected':
        print(f"Rejected:    {tx.get('rejected_at', 'N/A')}")
        print(f"Reason:      {tx.get('error', 'N/A')}")
    
    # Show payload details if available
    data = tx.get('data', {})
    payload = data.get('payload', {})
    
    if payload:
        print(f"\nPayload:")
        print(f"  Proof Hash:  {payload.get('proof_hash', 'N/A')[:32]}...")
        
        public_inputs = payload.get('public_inputs', {})
        if public_inputs:
            print(f"  Prediction:  {public_inputs.get('prediction', 'N/A')}")
            confidence = public_inputs.get('confidence', 0)
            print(f"  Confidence:  {confidence / 100:.2f}%")
            print(f"  Model Hash:  {public_inputs.get('model_hash', 'N/A')[:32]}...")
    
    print(f"{'='*70}\n")


def main():
    if len(sys.argv) < 2:
        print("Transaction Management CLI")
        print("\nUsage:")
        print("  python manage_transactions.py list                    - List all transactions")
        print("  python manage_transactions.py status <tx_hash>        - Check transaction status")
        print("  python manage_transactions.py approve <tx_hash>       - Approve/confirm transaction")
        print("  python manage_transactions.py reject <tx_hash> [reason] - Reject transaction")
        print("\nExamples:")
        print("  python manage_transactions.py list")
        print("  python manage_transactions.py approve a9623dc60545140f9199834017e5956b...")
        print("  python manage_transactions.py reject a9623dc60545140f... 'Invalid proof'")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "list":
        print("\n📋 Listing all transactions...\n")
        txs = list_transactions()
        
        if not txs:
            print("No transactions found.")
            return
        
        # Group by status
        pending = [tx for tx in txs if tx['status'] == 'pending']
        confirmed = [tx for tx in txs if tx['status'] == 'confirmed']
        rejected = [tx for tx in txs if tx['status'] == 'rejected']
        
        print(f"Total: {len(txs)} transactions")
        print(f"  ⏳ Pending:   {len(pending)}")
        print(f"  ✅ Confirmed: {len(confirmed)}")
        print(f"  ❌ Rejected:  {len(rejected)}")
        
        if pending:
            print(f"\n{'='*70}")
            print("PENDING TRANSACTIONS (need approval)")
            print(f"{'='*70}")
            for tx in pending:
                print(f"\n  Hash: {tx['hash']}")
                print(f"  Time: {tx['timestamp']}")
                print(f"  Command: python manage_transactions.py approve {tx['hash']}")
        
        if confirmed:
            print(f"\n{'='*70}")
            print("CONFIRMED TRANSACTIONS")
            print(f"{'='*70}")
            for tx in confirmed:
                print(f"\n  Hash: {tx['hash']}")
                print(f"  Time: {tx.get('confirmed_at', tx['timestamp'])}")
        
        if rejected:
            print(f"\n{'='*70}")
            print("REJECTED TRANSACTIONS")
            print(f"{'='*70}")
            for tx in rejected:
                print(f"\n  Hash: {tx['hash']}")
                print(f"  Reason: {tx.get('error', 'Unknown')}")
    
    elif command == "status":
        if len(sys.argv) < 3:
            print("Error: Transaction hash required")
            print("Usage: python manage_transactions.py status <tx_hash>")
            sys.exit(1)
        
        tx_hash = sys.argv[2]
        print(f"\n🔍 Checking transaction status...\n")
        
        tx = get_transaction(tx_hash)
        if not tx:
            print(f"❌ Transaction not found: {tx_hash}")
            sys.exit(1)
        
        print_transaction(tx)
    
    elif command in ["approve", "confirm"]:
        if len(sys.argv) < 3:
            print("Error: Transaction hash required")
            print("Usage: python manage_transactions.py approve <tx_hash>")
            sys.exit(1)
        
        tx_hash = sys.argv[2]
        print(f"\n✅ Approving transaction...\n")
        
        # Check current status
        tx = get_transaction(tx_hash)
        if not tx:
            print(f"❌ Transaction not found: {tx_hash}")
            sys.exit(1)
        
        if tx['status'] != 'pending':
            print(f"⚠️  Transaction is already {tx['status']}")
            print_transaction(tx)
            sys.exit(0)
        
        # Confirm it
        success = confirm_transaction(tx_hash)
        
        if success:
            print(f"✅ Transaction confirmed successfully!")
            
            # Fetch updated status
            import time
            time.sleep(0.5)
            tx = get_transaction(tx_hash)
            if tx:
                print_transaction(tx)
        else:
            print(f"❌ Failed to confirm transaction")
            sys.exit(1)
    
    elif command == "reject":
        if len(sys.argv) < 3:
            print("Error: Transaction hash required")
            print("Usage: python manage_transactions.py reject <tx_hash> [reason]")
            sys.exit(1)
        
        tx_hash = sys.argv[2]
        reason = sys.argv[3] if len(sys.argv) > 3 else "Rejected by user"
        
        print(f"\n❌ Rejecting transaction...\n")
        
        # Check current status
        tx = get_transaction(tx_hash)
        if not tx:
            print(f"❌ Transaction not found: {tx_hash}")
            sys.exit(1)
        
        if tx['status'] != 'pending':
            print(f"⚠️  Transaction is already {tx['status']}")
            print_transaction(tx)
            sys.exit(0)
        
        # Reject it
        success = reject_transaction(tx_hash, reason)
        
        if success:
            print(f"❌ Transaction rejected successfully!")
            print(f"Reason: {reason}")
            
            # Fetch updated status
            import time
            time.sleep(0.5)
            tx = get_transaction(tx_hash)
            if tx:
                print_transaction(tx)
        else:
            print(f"❌ Failed to reject transaction")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'list', 'status', 'approve', or 'reject'")
        sys.exit(1)


if __name__ == "__main__":
    main()
