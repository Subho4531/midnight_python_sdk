"""
MidnightClient — the main entry point for the midnight-py SDK.

Usage:
    from midnight_py import MidnightClient
    
    client = MidnightClient(network="preprod")
    print(client.status())
"""

from .wallet import WalletClient
from .indexer import IndexerClient
from .proof import ProofClient
from .contract import ContractClient, Contract
from .models import NetworkConfig
from .exceptions import MidnightSDKError, ProofServerConnectionError

NETWORKS: dict[str, NetworkConfig] = {
    "local": NetworkConfig(
        node_url="http://127.0.0.1:9944",
        indexer_url="http://127.0.0.1:8088/api/v3/graphql",
        indexer_ws_url="ws://127.0.0.1:8088/api/v3/graphql/ws",
        proof_server_url="http://127.0.0.1:6300",
        network_id="undeployed",
    ),
    "undeployed": NetworkConfig(
        node_url="http://127.0.0.1:9944",
        indexer_url="http://127.0.0.1:8088/api/v3/graphql",
        indexer_ws_url="ws://127.0.0.1:8088/api/v3/graphql/ws",
        proof_server_url="http://127.0.0.1:6300",
        network_id="undeployed",
    ),
    "preprod": NetworkConfig(
        node_url="https://rpc.testnet-02.midnight.network",
        indexer_url="https://indexer.testnet-02.midnight.network/api/v3/graphql",
        indexer_ws_url="wss://indexer.testnet-02.midnight.network/api/v3/graphql/ws",
        proof_server_url="http://127.0.0.1:6300",
        network_id="preprod",
    ),
}


class MidnightClient:
    """
    Main entry point for the Midnight Python SDK.
    
    Args:
        network: "preprod" (testnet) or "mainnet"
        node_url: Override the node URL
        indexer_url: Override the indexer URL
        proof_server_url: Override the proof server URL
        
    Example:
        client = MidnightClient(network="preprod")
        status = client.status()
        contract = client.contracts.deploy("my_contract.compact")
    """

    def __init__(
        self,
        network: str = "local",
        wallet_address: str | None = None,
        node_url: str | None = None,
        indexer_url: str | None = None,
        proof_server_url: str | None = None,
    ):
        if network not in NETWORKS:
            raise MidnightSDKError(
                f"Unknown network '{network}'. Choose from: {list(NETWORKS.keys())}"
            )

        cfg = NETWORKS[network]
        self.network = network
        self.wallet_address = wallet_address or ""
        
        # In undeployed mode, only proof server is mandatory
        if network == "undeployed":
            self.prover = ProofClient(proof_server_url or cfg.proof_server_url)
            
            # Health-check proof server immediately
            if not self.prover.is_alive():
                raise ProofServerConnectionError(
                    "Proof server not running on localhost:6300. "
                    "Start it with: docker-compose up proof-server"
                )
            
            # Optional services in undeployed mode
            self.wallet = WalletClient(node_url or cfg.node_url)
            self.indexer = IndexerClient(
                url=indexer_url or cfg.indexer_url,
                ws_url=cfg.indexer_ws_url,
                network_id=cfg.network_id,
            )
        else:
            # All services required for deployed networks
            self.wallet = WalletClient(node_url or cfg.node_url)
            self.indexer = IndexerClient(
                url=indexer_url or cfg.indexer_url,
                ws_url=cfg.indexer_ws_url,
                network_id=cfg.network_id,
            )
            self.prover = ProofClient(proof_server_url or cfg.proof_server_url)
        
        self.contracts = ContractClient(self.wallet, self.prover, self.indexer)
        
        # Initialize AI engine
        from .ai import ZKInferenceEngine
        self.ai = ZKInferenceEngine(self)

    def status(self) -> dict[str, bool]:
        """Check connectivity to all 3 Midnight services."""
        return {
            "node":    self.wallet.is_alive(),
            "indexer": self.indexer.is_alive(),
            "prover":  self.prover.is_alive(),
        }

    def get_contract(self, address: str, circuit_ids: list[str]) -> Contract:
        """Load a previously deployed contract by address."""
        return self.contracts.load(address, circuit_ids)
