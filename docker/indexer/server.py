#!/usr/bin/env python3
"""
Midnight Indexer Server - Provides GraphQL API and Explorer UI
"""

import asyncio
import json
from datetime import datetime
from aiohttp import web
import aiohttp

NODE_URL = "http://midnight-node:9944"


async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "service": "midnight-indexer"
    })


async def handle_graphql(request):
    """Handle GraphQL queries"""
    try:
        data = await request.json()
        query = data.get("query", "")
        variables = data.get("variables", {})
        
        # Simple __typename query
        if "__typename" in query:
            return web.json_response({
                "data": {
                    "__typename": "Query"
                }
            })
        
        # Get unshielded balance
        if "unshieldedCoins" in query:
            address = variables.get("address", "")
            if address:
                # Query node for balance
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'{NODE_URL}/balance/{address}') as resp:
                            if resp.status == 200:
                                balance_data = await resp.json()
                                return web.json_response({
                                    "data": {
                                        "unshieldedCoins": {
                                            "value": balance_data.get("dust", 0)
                                        }
                                    }
                                })
                except Exception as e:
                    print(f"[ERROR] Failed to fetch balance: {e}", flush=True)
            
            return web.json_response({
                "data": {
                    "unshieldedCoins": {"value": 0}
                }
            })
        
        # Get latest blocks
        if "blocks" in query:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        NODE_URL,
                        json={
                            "jsonrpc": "2.0",
                            "method": "chain_getBlock",
                            "params": [],
                            "id": 1
                        }
                    ) as resp:
                        if resp.status == 200:
                            rpc_data = await resp.json()
                            block = rpc_data.get("result", {}).get("block")
                            if block:
                                return web.json_response({
                                    "data": {
                                        "blocks": [block]
                                    }
                                })
            except Exception as e:
                print(f"[ERROR] Failed to fetch blocks: {e}", flush=True)
            
            return web.json_response({
                "data": {
                    "blocks": []
                }
            })
        
        # Get contract state
        if "contractState" in query or "contractAction" in query:
            address = variables.get("address", "")
            if address:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'{NODE_URL}/contract/{address}') as resp:
                            if resp.status == 200:
                                contract_data = await resp.json()
                                return web.json_response({
                                    "data": {
                                        "contractState": {
                                            "state": contract_data.get("state", {}),
                                            "blockHeight": 0
                                        }
                                    }
                                })
                except Exception as e:
                    print(f"[ERROR] Failed to fetch contract: {e}", flush=True)
            
            return web.json_response({
                "data": {
                    "contractState": None
                }
            })
        
        # Get transaction
        if "transaction" in query:
            tx_hash = variables.get("hash", "")
            if tx_hash:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'{NODE_URL}/tx/{tx_hash}') as resp:
                            if resp.status == 200:
                                tx_data = await resp.json()
                                return web.json_response({
                                    "data": {
                                        "transaction": {
                                            "hash": tx_data.get("hash"),
                                            "blockHeight": tx_data.get("block_height", 0),
                                            "status": tx_data.get("status", "pending")
                                        }
                                    }
                                })
                except Exception as e:
                    print(f"[ERROR] Failed to fetch transaction: {e}", flush=True)
            
            return web.json_response({
                "data": {
                    "transaction": None
                }
            })
        
        # Default response
        return web.json_response({
            "data": {}
        })
    
    except Exception as e:
        return web.json_response({
            "errors": [{"message": str(e)}]
        })


async def explorer_home(request):
    """Explorer home page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Midnight Explorer - Local</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #0a0e27;
                color: #fff;
            }
            h1 {
                color: #00d4ff;
            }
            .container {
                background: #1a1f3a;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }
            .tx-list {
                list-style: none;
                padding: 0;
            }
            .tx-item {
                background: #2a2f4a;
                padding: 15px;
                margin: 10px 0;
                border-radius: 4px;
                border-left: 4px solid #00d4ff;
            }
            .tx-hash {
                font-family: monospace;
                color: #00d4ff;
                word-break: break-all;
            }
            .tx-time {
                color: #888;
                font-size: 0.9em;
            }
            .search-box {
                width: 100%;
                padding: 10px;
                font-size: 16px;
                border: 2px solid #00d4ff;
                border-radius: 4px;
                background: #2a2f4a;
                color: #fff;
            }
            .status {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.8em;
            }
            .status-pending {
                background: #ffa500;
                color: #0a0e27;
            }
            .status-confirmed {
                background: #00ff00;
                color: #0a0e27;
            }
            .status-rejected {
                background: #ff0000;
                color: #fff;
            }
        </style>
    </head>
    <body>
        <h1>🌙 Midnight Explorer</h1>
        <p>Local Development Network</p>
        
        <div class="container">
            <h2>Search Transaction</h2>
            <input type="text" class="search-box" id="searchBox" placeholder="Enter transaction hash...">
            <button onclick="searchTx()" style="margin-top: 10px; padding: 10px 20px; background: #00d4ff; border: none; border-radius: 4px; cursor: pointer;">Search</button>
        </div>
        
        <div class="container">
            <h2>Recent Transactions</h2>
            <ul class="tx-list" id="txList">
                <li>Loading...</li>
            </ul>
        </div>
        
        <script>
            async function loadTransactions() {
                try {
                    const response = await fetch('/api/transactions');
                    const data = await response.json();
                    const txList = document.getElementById('txList');
                    
                    if (data.transactions && data.transactions.length > 0) {
                        // Sort by timestamp (newest first)
                        const sortedTx = data.transactions.sort((a, b) => {
                            return new Date(b.timestamp) - new Date(a.timestamp);
                        });
                        
                        txList.innerHTML = sortedTx.slice(0, 10).map(tx => `
                            <li class="tx-item">
                                <div><strong>Hash:</strong> <span class="tx-hash">${tx.hash}</span></div>
                                <div class="tx-time">${tx.timestamp}</div>
                                <div><span class="status status-${tx.status}">${tx.status}</span></div>
                                <div><a href="/tx/${tx.hash}" style="color: #00d4ff;">View Details →</a></div>
                            </li>
                        `).join('');
                    } else {
                        txList.innerHTML = '<li>No transactions yet</li>';
                    }
                } catch (e) {
                    console.error('Error loading transactions:', e);
                    document.getElementById('txList').innerHTML = '<li>Error loading transactions: ' + e.message + '</li>';
                }
            }
            
            function searchTx() {
                const hash = document.getElementById('searchBox').value;
                if (hash) {
                    window.location.href = '/tx/' + hash;
                }
            }
            
            // Load transactions on page load
            loadTransactions();
            
            // Refresh every 5 seconds
            setInterval(loadTransactions, 5000);
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')


async def explorer_tx(request):
    """Explorer transaction detail page"""
    tx_hash = request.match_info.get('hash', '')
    
    # Get NODE_URL from environment, default to Docker network name
    import os
    node_url = os.getenv('NODE_URL', 'http://midnight-node:9944')
    
    # Fetch transaction from node
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{node_url}/tx/{tx_hash}') as resp:
                if resp.status == 200:
                    tx_data = await resp.json()
                else:
                    tx_data = None
    except Exception as e:
        print(f"[ERROR] Failed to fetch transaction from node: {e}", flush=True)
        tx_data = None
    
    if tx_data:
        tx_json = json.dumps(tx_data, indent=2)
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Transaction {tx_hash[:16]}... - Midnight Explorer</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #0a0e27;
                    color: #fff;
                }}
                h1 {{
                    color: #00d4ff;
                }}
                .container {{
                    background: #1a1f3a;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .field {{
                    margin: 15px 0;
                    padding: 10px;
                    background: #2a2f4a;
                    border-radius: 4px;
                }}
                .label {{
                    color: #888;
                    font-size: 0.9em;
                    margin-bottom: 5px;
                }}
                .value {{
                    font-family: monospace;
                    color: #00d4ff;
                    word-break: break-all;
                }}
                pre {{
                    background: #2a2f4a;
                    padding: 15px;
                    border-radius: 4px;
                    overflow-x: auto;
                }}
                .status {{
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 4px;
                    background: #00d4ff;
                    color: #0a0e27;
                }}
            </style>
        </head>
        <body>
            <h1>🌙 Midnight Explorer</h1>
            <p><a href="/" style="color: #00d4ff;">← Back to Home</a></p>
            
            <div class="container">
                <h2>Transaction Details</h2>
                
                <div class="field">
                    <div class="label">Transaction Hash</div>
                    <div class="value">{tx_data['hash']}</div>
                </div>
                
                <div class="field">
                    <div class="label">Status</div>
                    <div><span class="status status-{tx_data['status']}">{tx_data['status']}</span></div>
                </div>
                
                <div class="field">
                    <div class="label">Timestamp</div>
                    <div class="value">{tx_data['timestamp']}</div>
                </div>
                
                <div class="field">
                    <div class="label">Block Height</div>
                    <div class="value">{tx_data['block_height']}</div>
                </div>
                
                <div class="field">
                    <div class="label">Raw Transaction Data</div>
                    <pre>{tx_json}</pre>
                </div>
            </div>
        </body>
        </html>
        """
    else:
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Transaction Not Found - Midnight Explorer</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #0a0e27;
                    color: #fff;
                }}
                h1 {{
                    color: #00d4ff;
                }}
                .container {{
                    background: #1a1f3a;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <h1>🌙 Midnight Explorer</h1>
            <p><a href="/" style="color: #00d4ff;">← Back to Home</a></p>
            
            <div class="container">
                <h2>Transaction Not Found</h2>
                <p>Transaction hash: <code>{tx_hash}</code></p>
                <p>This transaction does not exist or has not been indexed yet.</p>
            </div>
        </body>
        </html>
        """
    
    return web.Response(text=html, content_type='text/html')


async def list_transactions(request):
    """List all transactions from node"""
    import os
    node_url = os.getenv('NODE_URL', 'http://midnight-node:9944')
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{node_url}/transactions') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return web.json_response(data)
                else:
                    return web.json_response({
                        "transactions": [],
                        "count": 0
                    })
    except Exception as e:
        print(f"[ERROR] Failed to fetch transactions: {e}", flush=True)
        return web.json_response({
            "transactions": [],
            "count": 0
        })


async def init_app():
    """Initialize the application"""
    app = web.Application()
    
    # Add routes
    app.router.add_get('/health', health_check)
    app.router.add_post('/api/v4/graphql', handle_graphql)
    app.router.add_get('/', explorer_home)
    app.router.add_get('/tx/{hash}', explorer_tx)
    app.router.add_get('/api/transactions', list_transactions)
    
    return app


def main():
    """Main entry point"""
    print("Starting Midnight Indexer Server on port 8088...")
    app = asyncio.run(init_app())
    web.run_app(app, host='0.0.0.0', port=8088)


if __name__ == "__main__":
    main()
