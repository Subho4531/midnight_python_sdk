#!/usr/bin/env python3
"""
Midnight Node Server - Real blockchain with persistent storage
"""

import asyncio
import json
import hashlib
import sys
from datetime import datetime
from aiohttp import web
from pathlib import Path
from blockchain import Blockchain

# Force stdout/stderr to be unbuffered
sys.stdout = open(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = open(sys.stderr.fileno(), 'w', buffering=1)

# Storage directory
STORAGE_DIR = Path("/tmp/midnight_node")
STORAGE_DIR.mkdir(exist_ok=True)

# Initialize blockchain
blockchain = Blockchain(STORAGE_DIR)

print(f"[INIT] Midnight Node Server starting...", flush=True)
print(f"[INIT] Storage directory: {STORAGE_DIR}", flush=True)
print(f"[INIT] Current block height: {blockchain.get_block_height()}", flush=True)
print(f"[INIT] Transactions in mempool: {len(blockchain.transactions)}", flush=True)


async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "service": "midnight-node",
        "block_height": blockchain.get_block_height(),
        "transactions": len(blockchain.transactions)
    })


async def get_balance(request):
    """Get balance for any wallet address"""
    address = request.match_info.get('address', '')
    
    if not address:
        return web.json_response(
            {"error": "Address required"},
            status=400
        )
    
    balance = blockchain.get_balance(address)
    return web.json_response({
        "address": address,
        "dust": balance["dust"],
        "night": balance["night"]
    })


async def set_balance(request):
    """Set balance for an address (for testing/funding)"""
    try:
        data = await request.json()
        address = data.get("address", "")
        dust = int(data.get("dust", 0))
        night = int(data.get("night", 0))
        
        if not address:
            return web.json_response(
                {"error": "Address required"},
                status=400
            )
        
        blockchain.set_balance(address, dust, night)
        
        print(f"[BALANCE] Set balance for {address}: DUST={dust}, NIGHT={night}", flush=True)
        
        return web.json_response({
            "success": True,
            "address": address,
            "dust": dust,
            "night": night
        })
    except Exception as e:
        return web.json_response(
            {"error": str(e)},
            status=400
        )


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
                "status": "pending"
            }
            
            blockchain.add_transaction(tx_hash, tx_record)
            
            print(f"[TX] Transaction submitted: {tx_hash}", flush=True)
            print(f"[TX] Total transactions: {len(blockchain.transactions)}", flush=True)
            
            # Auto-confirm transaction after delay
            asyncio.create_task(auto_confirm_transaction(tx_hash))
            
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
            success = blockchain.confirm_transaction(tx_hash)
            
            return web.json_response({
                "jsonrpc": "2.0",
                "result": {"confirmed": success, "tx_hash": tx_hash},
                "id": request_id
            })
        
        elif method == "chain_getBlock":
            # Get latest block
            block = blockchain.get_latest_block()
            return web.json_response({
                "jsonrpc": "2.0",
                "result": {"block": block} if block else None,
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
    
    tx = blockchain.get_transaction(tx_hash)
    if tx:
        return web.json_response(tx)
    else:
        return web.json_response(
            {"error": "Transaction not found"},
            status=404
        )


async def list_transactions(request):
    """List all transactions"""
    limit = int(request.query.get('limit', 100))
    txs = blockchain.list_transactions(limit)
    
    return web.json_response({
        "transactions": txs,
        "count": len(txs)
    })


async def get_contract_state(request):
    """Get contract state"""
    address = request.match_info.get('address', '')
    
    state = blockchain.get_contract_state(address)
    if state:
        return web.json_response(state)
    else:
        return web.json_response(
            {"error": "Contract not found"},
            status=404
        )


async def auto_confirm_transaction(tx_hash):
    """
    Automatically confirm transaction after a delay.
    Simulates block confirmation time.
    """
    # Wait 3 seconds to simulate block time
    await asyncio.sleep(3)
    blockchain.confirm_transaction(tx_hash)


async def init_app():
    """Initialize the application"""
    app = web.Application()
    
    # Add routes
    app.router.add_get('/health', health_check)
    app.router.add_post('/', handle_rpc)
    app.router.add_get('/tx/{hash}', get_transaction)
    app.router.add_get('/transactions', list_transactions)
    app.router.add_get('/balance/{address}', get_balance)
    app.router.add_post('/balance', set_balance)
    app.router.add_get('/contract/{address}', get_contract_state)
    
    return app


def main():
    """Main entry point"""
    print("[MAIN] Starting Midnight Node Server on port 9944...", flush=True)
    print(f"[MAIN] Storage directory: {STORAGE_DIR}", flush=True)
    print(f"[MAIN] Block height: {blockchain.get_block_height()}", flush=True)
    app = asyncio.run(init_app())
    web.run_app(app, host='0.0.0.0', port=9944)


if __name__ == "__main__":
    main()
