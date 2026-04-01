from .proof import ProofClient
from .wallet import WalletClient
from .indexer import IndexerClient
from .models import ContractState, TransactionResult, ZKProof
from .exceptions import ContractDeployError, ContractCallError


class Contract:
    """
    Represents a deployed Midnight smart contract.
    
    Use ContractClient.deploy() or ContractClient.load() to get an instance.
    Don't instantiate this directly.
    """

    def __init__(
        self,
        address: str,
        circuit_ids: list[str],
        wallet: WalletClient,
        prover: ProofClient,
        indexer: IndexerClient,
        private_key: str | None = None,
    ):
        self.address = address
        self.circuit_ids = circuit_ids
        self._wallet = wallet
        self._prover = prover
        self._indexer = indexer
        self._private_key = private_key

    def call(
        self,
        circuit_name: str,
        private_inputs: dict | None = None,
        public_inputs: dict | None = None,
        private_key: str | None = None,
        sign_transaction: bool = True,
    ) -> TransactionResult:
        """
        Call a circuit function on this contract.
        
        1. Generates a ZK proof for the circuit
        2. Builds a transaction with the proof
        3. Signs and submits the transaction (if sign_transaction=True)
        
        Args:
            circuit_name: Name of the circuit to call
            private_inputs: Private inputs (sealed in ZK proof)
            public_inputs: Public inputs (visible on-chain)
            private_key: Private key for signing (overrides self._private_key)
            sign_transaction: Whether to sign the transaction (default: True)
        """
        if circuit_name not in self.circuit_ids:
            raise ContractCallError(
                f"Circuit '{circuit_name}' not found. "
                f"Available: {self.circuit_ids}"
            )

        # Step 1: Generate ZK proof
        proof: ZKProof = self._prover.generate_proof(
            circuit_id=f"{self.address}:{circuit_name}",
            private_inputs=private_inputs or {},
            public_inputs=public_inputs or {},
        )

        # Step 2: Build transaction
        tx = {
            "contractAddress": self.address,
            "circuit": circuit_name,
            "proof": proof.proof,
            "publicInputs": public_inputs or {},
            "publicOutputs": proof.public_outputs,
        }

        # Step 3: Sign (if requested)
        if sign_transaction:
            key = private_key or self._private_key
            if not key:
                raise ContractCallError(
                    "No private key provided. Either:\n"
                    "  1. Pass private_key parameter\n"
                    "  2. Call contract.set_key(key) first\n"
                    "  3. Set sign_transaction=False to skip signing"
                )
            signed = self._wallet.sign_transaction(tx, key)
            
            # Step 4: Submit signed transaction
            return self._wallet.submit_transaction(signed)
        else:
            # Submit unsigned (for testing/development)
            return self._wallet.submit_transaction(tx)

    def state(self) -> ContractState:
        """Read the current public on-chain state of this contract."""
        return self._indexer.get_contract_state(self.address)

    def set_key(self, private_key: str) -> "Contract":
        """Set the private key used for signing. Returns self for chaining."""
        self._private_key = private_key
        return self


class ContractClient:
    """Factory for deploying and loading Midnight contracts."""

    def __init__(
        self,
        wallet: WalletClient,
        prover: ProofClient,
        indexer: IndexerClient,
    ):
        self._wallet = wallet
        self._prover = prover
        self._indexer = indexer

    def deploy(
        self,
        contract_path: str,
        constructor_args: dict | None = None,
        private_key: str | None = None,
        sign_transaction: bool = True,
    ) -> Contract:
        """
        Deploy a .compact contract to the network.
        
        This:
        1. Compiles the contract (if not already compiled)
        2. Creates a deployment transaction
        3. Signs the transaction with private key
        4. Submits to the blockchain
        5. Returns a Contract instance
        
        Args:
            contract_path: Path to .compact file
            constructor_args: Constructor arguments (if any)
            private_key: Private key for signing deployment
            sign_transaction: Whether to sign the transaction (default: True)
        
        Returns:
            Contract instance at the deployed address
        """
        import hashlib
        import json
        from pathlib import Path
        from datetime import datetime
        
        from .codegen import compile_compact, parse_compact_circuits

        # Step 1: Compile contract if needed
        contract_name = Path(contract_path).stem
        managed_dir = Path("contracts/managed") / contract_name
        contract_js = managed_dir / "contract" / "index.js"
        
        if not contract_js.exists():
            print(f"Compiling {contract_path}...")
            compile_compact(contract_path)
            print(f"[OK] Compiled to {managed_dir}")
        
        # Step 2: Parse circuits
        circuit_names = parse_compact_circuits(contract_path)
        
        # Step 3: Generate contract address (deterministic from contract code)
        contract_code = Path(contract_path).read_text()
        contract_hash = hashlib.sha256(contract_code.encode()).hexdigest()
        contract_address = f"contract_{contract_hash[:32]}"
        
        # Step 4: Create deployment transaction
        deployment_tx = {
            "type": "deploy_contract",
            "contract_name": contract_name,
            "contract_address": contract_address,
            "contract_path": str(contract_path),
            "circuits": circuit_names,
            "constructor_args": constructor_args or {},
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "deployer": self._wallet.url,  # Wallet address would go here
        }
        
        # Step 5: Sign and submit transaction
        if sign_transaction:
            if not private_key:
                raise ContractDeployError(
                    "Private key required for signing deployment.\n"
                    "Either:\n"
                    "  1. Pass private_key parameter\n"
                    "  2. Set sign_transaction=False (not recommended)"
                )
            
            # Sign the deployment transaction
            signed_tx = self._wallet.sign_transaction(deployment_tx, private_key)
            
            # Submit to blockchain
            result = self._wallet.submit_transaction(signed_tx)
            
            print(f"[OK] Contract deployed at: {contract_address}")
            print(f"[OK] Transaction hash: {result.tx_hash}")
            print(f"[OK] Circuits: {', '.join(circuit_names)}")
        else:
            print(f"[OK] Contract prepared (not deployed): {contract_address}")
            print(f"[OK] Circuits: {', '.join(circuit_names)}")
        
        # Step 6: Return Contract instance
        return Contract(
            address=contract_address,
            circuit_ids=circuit_names,
            wallet=self._wallet,
            prover=self._prover,
            indexer=self._indexer,
            private_key=private_key,
        )

    def load(self, address: str, circuit_ids: list[str]) -> Contract:
        """Load an already-deployed contract by address."""
        return Contract(
            address=address,
            circuit_ids=circuit_ids,
            wallet=self._wallet,
            prover=self._prover,
            indexer=self._indexer,
        )
