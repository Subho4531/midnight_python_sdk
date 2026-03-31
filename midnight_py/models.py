from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime


class NetworkConfig(BaseModel):
    node_url: str
    indexer_url: str
    indexer_ws_url: str
    proof_server_url: str
    network_id: str


class Balance(BaseModel):
    dust: int = 0       # smallest unit (like satoshi in Bitcoin)
    night: int = 0      # NIGHT governance token


class ZKProof(BaseModel):
    proof: str
    public_outputs: dict[str, Any] = Field(default_factory=dict)
    circuit_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def proof_hash(self) -> str:
        """Compute SHA256 hash of the proof"""
        import hashlib
        return hashlib.sha256(self.proof.encode()).hexdigest()


class TransactionResult(BaseModel):
    tx_hash: str
    block_height: Optional[int] = None
    status: str = "pending"


class ContractState(BaseModel):
    address: str
    state: dict[str, Any]
    block_height: int


class DeployedContract(BaseModel):
    address: str
    network: str
    deployed_at: datetime = Field(default_factory=datetime.utcnow)
    circuit_ids: list[str] = Field(default_factory=list)
