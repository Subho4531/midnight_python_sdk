"""Transaction builder for offline transaction construction."""

from typing import Any


class TransactionBuilder:
    """Build unsigned transactions for offline signing."""
    
    def __init__(self):
        self.tx_data: dict[str, Any] = {
            "type": None,
            "nonce": None,
            "fee": None,
            "payload": {},
        }
    
    def call_contract(
        self,
        address: str,
        circuit: str,
        args: dict[str, Any] | None = None,
    ) -> "TransactionBuilder":
        """Build a contract call transaction."""
        self.tx_data["type"] = "contract_call"
        self.tx_data["payload"] = {
            "contract_address": address,
            "circuit": circuit,
            "arguments": args or {},
        }
        return self
    
    def deploy_contract(self, contract_path: str) -> "TransactionBuilder":
        """Build a contract deployment transaction."""
        self.tx_data["type"] = "contract_deploy"
        self.tx_data["payload"] = {
            "contract_path": contract_path,
        }
        return self
    
    def transfer(self, dest: str, amount: int) -> "TransactionBuilder":
        """Build a token transfer transaction."""
        self.tx_data["type"] = "transfer"
        self.tx_data["payload"] = {
            "destination": dest,
            "amount": amount,
        }
        return self
    
    def set_nonce(self, nonce: int) -> "TransactionBuilder":
        """Set transaction nonce."""
        self.tx_data["nonce"] = nonce
        return self
    
    def set_fee(self, fee: int) -> "TransactionBuilder":
        """Set transaction fee."""
        self.tx_data["fee"] = fee
        return self
    
    def build(self) -> dict[str, Any]:
        """Build and return the unsigned transaction."""
        if self.tx_data["type"] is None:
            raise ValueError("Transaction type not set")
        
        return self.tx_data.copy()
    
    def reset(self) -> "TransactionBuilder":
        """Reset the builder for a new transaction."""
        self.tx_data = {
            "type": None,
            "nonce": None,
            "fee": None,
            "payload": {},
        }
        return self
