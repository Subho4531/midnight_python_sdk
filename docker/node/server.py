#!/usr/bin/env python3
"""
Midnight Node Server - Stores real transactions
"""

import asyncio
import json
import hashlib
import sys
from datetime import datetime
from aiohttp import web
from pathlib import Path

# Force stdout/stderr to be unbuffered
sys.stdout = open(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = open(sys.stderr.fileno(), 'w', buffering=1)

# In-memory storage for transactions
transactions = {}
blocks = []
current_block_height = 0

# Storage directory
STORAGE_DIR = Path("/tmp/midnight_node")
STORAGE_DIR.mkdir(exist_ok=True)

print(f"[INIT] Midnight Node Server starting...", flush=True)
print(f"[INIT] Storage directory: {STORAGE_DIR}", flush=True)


def save_transaction(tx_hash, tx_data):
    """Save transaction to disk"""
    tx_file = STORAGE_DIR / f"tx_{tx_hash}.json"
    tx_file.write_text(json.dumps(tx_data, indent=2))
    print(f"[SAVE] Transaction saved: {tx_hash}", flush=True)


def load_transactions():
    """Load all transactions from disk"""
    global transactions
    print(f"[LOAD] Loading transactions from {STORAGE_DIR}...", flush=True)
    count = 0
    for tx_file in STORAGE_DIR.glob("tx_*.json"):
        try:
            tx_data = json.loads(tx_file.read_text())
            tx_hash = tx_data.get("hash", "")
            if tx_hash:
                transactions[tx_hash] = tx_data
                count += 1
        except Exception as e:
            print(f"[LOAD] Error loading {tx_file}: {e}", flush=True)
    print(f"[LOAD] Loaded {count} transactions", flush=True)


async def process_transaction(tx_hash):
    """
    Process a pending transaction by executing the contract.
    This simulates contract execution and block confirmation.
    """
    if tx_hash not in transactions:
        return False
    
    tx = transactions[tx_hash]
    
    # Verify signature
    payload = tx["data"].get("payload", {})
    signature = tx["data"].get("signature", "")
    
    # Simulate contract execution
    # In a real blockchain, this would execute the Compact contract
    print(f"[PROCESS] Executing contract for tx {tx_hash}...", flush=True)
    
    # Verify the proof (in real implementation, this would verify ZK proof)
    proof = payload.get("proof", "")
    if not proof or not proof.startswith("zk_snark_proof_"):
        tx["status"] = "rejected"
        tx["error"] = "Invalid proof format"
        save_transaction(tx_hash, tx)
        return False
    
    # Update transaction status
    tx["status"] = "confirmed"
    tx["confirmed_at"] = datetime.utcnow().isoformat() + "Z"
    tx["block_height"] = current_block_height + 1
    
    save_transaction(tx_hash, tx)
    print(f"[PROCESS] Transaction confirmed: {tx_hash}", flush=True)
    
    return True


async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "service": "midnight-node",
        "block_height": current_block_height,
        "transactions": len(transactions)
    })


async def handle_rpc(request):
    """Handle JSON-RPC requests"""
    try:
        data = await request.json()
        method = data.get("method", "")
        params = data.get("params", [])
        request_id = data.get("id", 1)
        
        if method == "system_chain":
            return web.json_response({
                "jsonrpc": "2.0",
                "result": "Midnight Undeployed",
                "id": request_id
            })
        
        elif method == "system_health":
            return web.json_response({
                "jsonrpc": "2.0",
                "result": {
                    "peers": 0,
                    "isSyncing": False,
                    "shouldHavePeers": False
                },
                "id": request_id
            })
        
        elif method == "author_submitExtrinsic":
            # Submit transaction
            if not params:
                return web.json_response({
                    "jsonrpc": "2.0",
                    "error": {"code": -32602, "message": "Invalid params"},
                    "id": request_id
                })
            
            signed_tx = params[0]
            
            # Create transaction hash
            tx_data = json.dumps(signed_tx, sort_keys=True)
            tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
            
            # Store transaction
            tx_record = {
                "hash": tx_hash,
                "data": signed_tx,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "block_height": current_block_height + 1,
                "status": "pending"
            }
            
            transactions[tx_hash] = tx_record
            save_transaction(tx_hash, tx_record)
            
            print(f"[TX] Transaction submitted: {tx_hash}", flush=True)
            print(f"[TX] Total transactions: {len(transactions)}", flush=True)
            
            # Auto-process transaction (simulate contract execution)
            # In production, this would be done by miners/validators
            asyncio.create_task(auto_process_transaction(tx_hash))
            
            return web.json_response({
                "jsonrpc": "2.0",
                "result": tx_hash,
                "id": request_id
            })
        
        elif method == "chain_confirmTransaction":
            # Manually confirm a transaction
            if not params or len(params) < 1:
                return web.json_response({
                    "jsonrpc": "2.0",
                    "error": {"code": -32602, "message": "Invalid params"},
                    "id": request_id
                })
            
            tx_hash = params[0]
            success = await process_transaction(tx_hash)
            
            return web.json_response({
                "jsonrpc": "2.0",
                "result": {"confirmed": success, "tx_hash": tx_hash},
                "id": request_id
            })
        
        elif method == "chain_rejectTransaction":
            # Manually reject a transaction
            if not params or len(params) < 1:
                return web.json_response({
                    "jsonrpc": "2.0",
                    "error": {"code": -32602, "message": "Invalid params"},
                    "id": request_id
                })
            
            tx_hash = params[0]
            reason = params[1] if len(params) > 1 else "Rejected by user"
            
            if tx_hash in transactions:
                transactions[tx_hash]["status"] = "rejected"
                transactions[tx_hash]["error"] = reason
                transactions[tx_hash]["rejected_at"] = datetime.utcnow().isoformat() + "Z"
                save_transaction(tx_hash, transactions[tx_hash])
                
                return web.json_response({
                    "jsonrpc": "2.0",
                    "result": {"rejected": True, "tx_hash": tx_hash},
                    "id": request_id
                })
            else:
                return web.json_response({
                    "jsonrpc": "2.0",
                    "error": {"code": -32600, "message": "Transaction not found"},
                    "id": request_id
                })
        
        elif method == "chain_getBlock":
            # Get block by hash or height
            return web.json_response({
                "jsonrpc": "2.0",
                "result": {
                    "block": {
                        "header": {
                            "number": current_block_height,
                            "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000000"
                        },
                        "extrinsics": []
                    }
                },
                "id": request_id
            })
        
        else:
            return web.json_response({
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Method not found: {method}"},
                "id": request_id
            })
    
    except Exception as e:
        return web.json_response({
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": 1
        })


async def get_transaction(request):
    """Get transaction by hash"""
    tx_hash = request.match_info.get('hash', '')
    
    if tx_hash in transactions:
        return web.json_response(transactions[tx_hash])
    else:
        return web.json_response(
            {"error": "Transaction not found"},
            status=404
        )


async def list_transactions(request):
    """List all transactions"""
    return web.json_response({
        "transactions": list(transactions.values()),
        "count": len(transactions)
    })


async def auto_process_transaction(tx_hash):
    """
    Automatically process transaction after a delay.
    Simulates block confirmation time.
    """
    # Wait 3 seconds to simulate block time
    await asyncio.sleep(3)
    await process_transaction(tx_hash)


async def init_app():
    """Initialize the application"""
    # Load existing transactions
    load_transactions()
    
    app = web.Application()
    
    # Add routes
    app.router.add_get('/health', health_check)
    app.router.add_post('/', handle_rpc)
    app.router.add_get('/tx/{hash}', get_transaction)
    app.router.add_get('/transactions', list_transactions)
    
    return app


def main():
    """Main entry point"""
    print("[MAIN] Starting Midnight Node Server on port 9944...", flush=True)
    print(f"[MAIN] Storage directory: {STORAGE_DIR}", flush=True)
    app = asyncio.run(init_app())
    web.run_app(app, host='0.0.0.0', port=9944)


if __name__ == "__main__":
    main()
