#!/usr/bin/env python3
"""
Real Blockchain Storage - Persistent on-chain data
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class Block:
    """Blockchain block"""
    def __init__(self, height: int, transactions: List[str], previous_hash: str):
        self.height = height
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate block hash"""
        data = f"{self.height}{self.previous_hash}{self.timestamp}{json.dumps(self.transactions)}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def to_dict(self) -> dict:
        return {
            "height": self.height,
            "hash": self.hash,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "transactions": self.transactions
        }


class Blockchain:
    """Real blockchain with persistent storage"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True, parents=True)
        
        # Storage files
        self.blocks_file = self.data_dir / "blocks.json"
        self.transactions_file = self.data_dir / "transactions.json"
        self.balances_file = self.data_dir / "balances.json"
        self.contracts_file = self.data_dir / "contracts.json"
        
        # Load existing data
        self.blocks: List[Block] = self._load_blocks()
        self.transactions: Dict[str, dict] = self._load_transactions()
        self.balances: Dict[str, dict] = self._load_balances()
        self.contracts: Dict[str, dict] = self._load_contracts()
        
        # Create genesis block if needed
        if not self.blocks:
            self._create_genesis_block()
    
    def _load_blocks(self) -> List[Block]:
        """Load blocks from disk"""
        if self.blocks_file.exists():
            data = json.loads(self.blocks_file.read_text())
            blocks = []
            for b in data:
                block = Block(b["height"], b["transactions"], b["previous_hash"])
                block.hash = b["hash"]
                block.timestamp = b["timestamp"]
                blocks.append(block)
            return blocks
        return []
    
    def _load_transactions(self) -> Dict[str, dict]:
        """Load transactions from disk"""
        if self.transactions_file.exists():
            return json.loads(self.transactions_file.read_text())
        return {}
    
    def _load_balances(self) -> Dict[str, dict]:
        """Load balances from disk"""
        if self.balances_file.exists():
            return json.loads(self.balances_file.read_text())
        return {}
    
    def _load_contracts(self) -> Dict[str, dict]:
        """Load contracts from disk"""
        if self.contracts_file.exists():
            return json.loads(self.contracts_file.read_text())
        return {}
    
    def _save_blocks(self):
        """Save blocks to disk"""
        data = [b.to_dict() for b in self.blocks]
        self.blocks_file.write_text(json.dumps(data, indent=2))
    
    def _save_transactions(self):
        """Save transactions to disk"""
        self.transactions_file.write_text(json.dumps(self.transactions, indent=2))
    
    def _save_balances(self):
        """Save balances to disk"""
        self.balances_file.write_text(json.dumps(self.balances, indent=2))
    
    def _save_contracts(self):
        """Save contracts to disk"""
        self.contracts_file.write_text(json.dumps(self.contracts, indent=2))
    
    def _create_genesis_block(self):
        """Create the genesis block"""
        genesis = Block(0, [], "0" * 64)
        self.blocks.append(genesis)
        self._save_blocks()
        print(f"[BLOCKCHAIN] Genesis block created: {genesis.hash}")
    
    def get_balance(self, address: str) -> dict:
        """Get balance for any address"""
        if address in self.balances:
            return self.balances[address]
        return {"dust": 0, "night": 0}
    
    def set_balance(self, address: str, dust: int, night: int):
        """Set balance for an address"""
        self.balances[address] = {"dust": dust, "night": night}
        self._save_balances()
    
    def add_transaction(self, tx_hash: str, tx_data: dict) -> bool:
        """Add a transaction to the mempool"""
        self.transactions[tx_hash] = tx_data
        self._save_transactions()
        print(f"[BLOCKCHAIN] Transaction added to mempool: {tx_hash}")
        return True
    
    def get_transaction(self, tx_hash: str) -> Optional[dict]:
        """Get transaction by hash"""
        return self.transactions.get(tx_hash)
    
    def confirm_transaction(self, tx_hash: str) -> bool:
        """Confirm a transaction by including it in a block"""
        if tx_hash not in self.transactions:
            return False
        
        tx = self.transactions[tx_hash]
        
        # Verify signature
        if not self._verify_signature(tx):
            tx["status"] = "rejected"
            tx["error"] = "Invalid signature"
            self._save_transactions()
            return False
        
        # Execute transaction (update balances, contracts, etc.)
        if not self._execute_transaction(tx):
            tx["status"] = "rejected"
            tx["error"] = "Execution failed"
            self._save_transactions()
            return False
        
        # Create new block with this transaction
        previous_hash = self.blocks[-1].hash if self.blocks else "0" * 64
        new_block = Block(len(self.blocks), [tx_hash], previous_hash)
        self.blocks.append(new_block)
        self._save_blocks()
        
        # Update transaction status
        tx["status"] = "confirmed"
        tx["block_height"] = new_block.height
        tx["block_hash"] = new_block.hash
        tx["confirmed_at"] = datetime.utcnow().isoformat() + "Z"
        self._save_transactions()
        
        print(f"[BLOCKCHAIN] Transaction confirmed in block {new_block.height}: {tx_hash}")
        return True
    
    def _verify_signature(self, tx: dict) -> bool:
        """Verify transaction signature"""
        # In a real implementation, this would verify the cryptographic signature
        # For now, we check that signature exists and has correct format
        signature = tx.get("data", {}).get("signature", "")
        return bool(signature and len(signature) > 32)
    
    def _execute_transaction(self, tx: dict) -> bool:
        """Execute transaction (update state)"""
        payload = tx.get("data", {}).get("payload", {})
        
        # Handle contract deployment
        if payload.get("type") == "deploy":
            contract_address = payload.get("contractAddress", "")
            if contract_address:
                self.contracts[contract_address] = {
                    "address": contract_address,
                    "deployed_at": tx["timestamp"],
                    "deployer": payload.get("from", ""),
                    "state": {}
                }
                self._save_contracts()
                print(f"[BLOCKCHAIN] Contract deployed: {contract_address}")
        
        # Handle circuit call
        elif payload.get("type") == "call":
            contract_address = payload.get("contractAddress", "")
            if contract_address in self.contracts:
                # Update contract state
                circuit = payload.get("circuit", "")
                public_inputs = payload.get("publicInputs", {})
                
                # Store the call result in contract state
                if "calls" not in self.contracts[contract_address]:
                    self.contracts[contract_address]["calls"] = []
                
                self.contracts[contract_address]["calls"].append({
                    "circuit": circuit,
                    "inputs": public_inputs,
                    "timestamp": tx["timestamp"],
                    "tx_hash": tx["hash"]
                })
                
                # Update contract state based on circuit logic
                self.contracts[contract_address]["state"] = public_inputs
                self._save_contracts()
                print(f"[BLOCKCHAIN] Circuit executed: {circuit} on {contract_address}")
        
        return True
    
    def get_contract_state(self, address: str) -> Optional[dict]:
        """Get contract state"""
        return self.contracts.get(address)
    
    def get_latest_block(self) -> Optional[dict]:
        """Get the latest block"""
        if self.blocks:
            return self.blocks[-1].to_dict()
        return None
    
    def get_block_height(self) -> int:
        """Get current block height"""
        return len(self.blocks) - 1
    
    def list_transactions(self, limit: int = 100) -> List[dict]:
        """List recent transactions"""
        txs = list(self.transactions.values())
        # Sort by timestamp, newest first
        txs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return txs[:limit]
