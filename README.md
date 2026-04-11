# 🌙 Midnight Python SDK

The first comprehensive Python SDK for building zero-knowledge applications on the Midnight blockchain. Build privacy-preserving applications with automatic Python bindings from Compact contracts, cryptographic transaction signing, and ZK-SNARK proof generation.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/midnight-sdk.svg)](https://pypi.org/project/midnight-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/midnight-sdk.svg)](https://pypi.org/project/midnight-sdk/)

## ✨ Features

### 🔥 What Makes This Special

- **Auto-Generated Bindings**: Automatically generate type-safe Python classes from `.compact` smart contracts
- **Real Cryptographic Signing**: Sign transactions with private keys using the official Midnight wallet SDK
- **ZK-SNARK Proofs**: Generate and verify zero-knowledge proofs for privacy-preserving computations
- **Privacy-First AI**: Run machine learning inference with ZK proofs to keep data private
- **Production Ready**: Full transaction lifecycle with proper error handling and retry logic

### 🛠️ Core Capabilities

- ✅ Smart contract compilation and deployment
- ✅ ZK-SNARK proof generation and verification
- ✅ Cryptographic transaction signing and submission
- ✅ Real-time blockchain interaction and monitoring
- ✅ Privacy-preserving AI inference (ZK-ML)
- ✅ GraphQL indexer integration for data queries
- ✅ Complete CLI for blockchain operations
- ✅ Type-safe Python bindings with full IDE support

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install midnight-sdk

# Or install with development dependencies
pip install midnight-sdk[dev]
```

### Prerequisites for Local Development

If you want to run a local Midnight network for development:

- Python 3.10+
- Docker & Docker Compose (for local network)
- Node.js 22+ (for wallet SDK integration)

### Basic Usage

```python
from midnight_sdk import MidnightClient

# Connect to Midnight network
client = MidnightClient(
    network="testnet",  # or "mainnet", "undeployed" for local
    wallet_address="your_midnight_address"
)

# Check your balance
balance = client.get_balance()
print(f"DUST: {balance.dust}, NIGHT: {balance.night}")

# Deploy a smart contract
contract_address = client.deploy_contract(
    contract_path="path/to/contract.compact",
    private_key="your_private_key"
)

# Call a contract method
result = client.call_contract(
    contract_address=contract_address,
    method="your_method",
    args={"param": "value"},
    private_key="your_private_key"
)
```

## 📖 Usage Guide

### Command Line Interface (CLI)

The Midnight SDK includes a powerful CLI for all blockchain operations:

```bash
# Check network status and connectivity
midnight status

# Get latest block information
midnight block

# Check wallet balance
midnight balance <wallet_address>

# Deploy a smart contract
midnight deploy <contract.compact> --wallet <address> --key <private_key>

# Call a contract method
midnight call <contract_address> <method_name> --args '{"param": "value"}'

# Get contract state
midnight state <contract_address>

# Transaction operations
midnight tx get <transaction_hash>        # Get transaction details
midnight tx list <contract_address>       # List contract transactions
midnight tx status <transaction_hash>     # Check transaction status

# Wallet operations
midnight wallet create                    # Create new wallet
midnight wallet balance <address>         # Check balance
midnight wallet transfer <to> <amount>    # Transfer tokens

# AI inference with privacy
midnight ai predict <model> --features '[1,2,3,4]' --private

# System utilities
midnight config show                      # Show configuration
midnight config set <key> <value>        # Update configuration
midnight node info                        # Get node information
midnight proof generate <circuit>         # Generate ZK proof
```

### Python SDK Examples

#### 1. Basic Contract Interaction

```python
from midnight_sdk import MidnightClient
from pathlib import Path

# Initialize client
client = MidnightClient(network="testnet")

# Load your private key
private_key = "your_private_key_here"

# Deploy a contract
contract_path = Path("contracts/bulletin_board.compact")
contract_address = client.deploy_contract(
    contract_path=contract_path,
    private_key=private_key
)

print(f"Contract deployed at: {contract_address}")

# Call a contract method
result = client.call_contract(
    contract_address=contract_address,
    method="post",
    args={"message": "Hello Midnight!"},
    private_key=private_key
)

print(f"Transaction hash: {result.tx_hash}")
```

#### 2. Privacy-Preserving AI Inference

```python
from midnight_sdk import MidnightClient

client = MidnightClient(network="testnet")

# Run private AI inference with ZK proofs
result = client.ai.predict_private(
    model="iris_classifier",
    features=[5.1, 3.5, 1.4, 0.2],
    private_key=private_key
)

print(f"Prediction: {result.prediction}")
print(f"Confidence: {result.confidence:.2%}")
print(f"ZK Proof: {result.proof_hash}")
print(f"Transaction: {result.tx_hash}")
```

#### 3. Auto-Generated Contract Bindings

```python
from midnight_sdk.codegen import generate_bindings

# Generate Python class from Compact contract
BulletinBoard = generate_bindings("contracts/bulletin_board.compact")

# Use the generated class with full type safety
board = BulletinBoard(
    contract_address="your_contract_address",
    client=client
)

# Call methods with IDE autocomplete and type checking
tx_hash = board.post(
    message="Hello from Python!",
    private_key=private_key
)

# Read contract state
messages = board.get_messages()
for msg in messages:
    print(f"Message: {msg.content} (from: {msg.author})")
```

#### 4. Transaction Management

```python
from midnight_sdk import MidnightClient, TransactionBuilder

client = MidnightClient(network="testnet")

# Build a complex transaction
tx_builder = TransactionBuilder(client)

tx = (tx_builder
    .contract_call(
        address="contract_addr",
        method="transfer",
        args={"to": "recipient", "amount": 100}
    )
    .with_gas_limit(1000000)
    .with_fee(1000)
    .build())

# Sign and submit
signed_tx = client.sign_transaction(tx, private_key)
result = client.submit_transaction(signed_tx)

# Monitor transaction
status = client.wait_for_confirmation(result.tx_hash, timeout=60)
print(f"Transaction confirmed: {status.confirmed}")
```

#### 5. Real-time Event Monitoring

```python
from midnight_sdk import MidnightClient

client = MidnightClient(network="testnet")

# Subscribe to contract events
async def handle_event(event):
    print(f"New event: {event.name}")
    print(f"Data: {event.data}")
    print(f"Block: {event.block_number}")

# Monitor specific contract
await client.subscribe_to_contract_events(
    contract_address="your_contract",
    event_handler=handle_event
)

# Monitor all transactions
await client.subscribe_to_transactions(
    handler=lambda tx: print(f"New tx: {tx.hash}")
)
```

## 🏗️ Architecture & Networks

### Supported Networks

| Network | Description | Use Case |
|---------|-------------|----------|
| `mainnet` | Midnight mainnet | Production applications |
| `testnet` | Midnight testnet | Testing and development |
| `undeployed` | Local development | Local testing with Docker |

### Local Development Setup

For local development, you can run a complete Midnight network locally:

```bash
# Clone the SDK repository for local development
git clone https://github.com/midnight-labs/midnight-python-sdk.git
cd midnight-python-sdk

# Start local Midnight network
docker-compose up -d

# Verify services are running
midnight status
```

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Your Application                      │
│                  (Python + midnight-sdk)                │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│   Node   │  │ Indexer  │  │  Proof   │
│  :9944   │  │  :8088   │  │  :6300   │
└──────────┘  └──────────┘  └──────────┘
     │             │              │
     └─────────────┴──────────────┘
              Midnight Network
```

### Core Components

| Component | Purpose | Port (Local) |
|-----------|---------|--------------|
| **Midnight Node** | Transaction processing, consensus, state management | 9944 |
| **GraphQL Indexer** | Query API, transaction history, block explorer | 8088 |
| **Proof Server** | ZK-SNARK proof generation and verification | 6300 |
| **Wallet SDK** | Key management, transaction signing | N/A |

## 📚 API Reference

### MidnightClient

The main client class for interacting with the Midnight blockchain.

```python
from midnight_sdk import MidnightClient

client = MidnightClient(
    network="testnet",           # Network to connect to
    wallet_address="mn_addr...", # Your wallet address
    node_url=None,              # Custom node URL (optional)
    indexer_url=None,           # Custom indexer URL (optional)
    proof_server_url=None       # Custom proof server URL (optional)
)
```

#### Methods

- `get_balance(address=None) -> Balance` - Get wallet balance
- `deploy_contract(contract_path, private_key, **kwargs) -> str` - Deploy smart contract
- `call_contract(contract_address, method, args, private_key) -> TransactionResult` - Call contract method
- `get_contract_state(contract_address) -> dict` - Get contract state
- `get_transaction(tx_hash) -> Transaction` - Get transaction details
- `wait_for_confirmation(tx_hash, timeout=60) -> TransactionStatus` - Wait for transaction confirmation

### CLI Commands Reference

#### Network & Status
```bash
midnight status                    # Check network connectivity
midnight block [number]           # Get block information
midnight node info                # Get node information
```

#### Wallet Operations
```bash
midnight wallet create            # Create new wallet
midnight wallet balance <addr>    # Check balance
midnight wallet transfer <to> <amount> [--token DUST|NIGHT]
```

#### Contract Operations
```bash
midnight deploy <contract.compact> --wallet <addr> --key <key>
midnight call <contract> <method> --args '{"key": "value"}'
midnight state <contract_address>
```

#### Transaction Management
```bash
midnight tx get <hash>           # Get transaction details
midnight tx list <contract>      # List contract transactions
midnight tx status <hash>        # Check transaction status
midnight tx wait <hash>          # Wait for confirmation
```

#### AI & Privacy
```bash
midnight ai predict <model> --features '[1,2,3]' --private
midnight proof generate <circuit> --inputs '{"x": 1}'
```

#### Configuration
```bash
midnight config show             # Show current configuration
midnight config set <key> <val> # Update configuration
midnight config reset           # Reset to defaults
```

## 🧪 Examples & Testing

### Example Scripts

The SDK includes comprehensive examples for common use cases:

```python
# Basic contract deployment and interaction
from midnight_sdk.examples import basic_contract_example
basic_contract_example()

# AI inference with privacy
from midnight_sdk.examples import ai_inference_example
ai_inference_example()

# Complete transaction workflow
from midnight_sdk.examples import transaction_workflow_example
transaction_workflow_example()
```

### Running Examples

```bash
# Install the SDK with examples
pip install midnight-sdk[examples]

# Run individual examples
python -m midnight_sdk.examples.basic_contract
python -m midnight_sdk.examples.ai_inference
python -m midnight_sdk.examples.bulletin_board
python -m midnight_sdk.examples.private_voting

# Run all examples
python -m midnight_sdk.examples.run_all
```

### Testing Your Integration

```python
from midnight_sdk.testing import TestClient

# Use test client for unit tests
test_client = TestClient()

# Mock contract interactions
result = test_client.mock_contract_call(
    contract="test_contract",
    method="test_method",
    expected_result={"success": True}
)

assert result.success == True
```

## 🔧 Development & Contributing

### Development Setup

```bash
# Clone the repository
git clone https://github.com/midnight-labs/midnight-python-sdk.git
cd midnight-python-sdk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linting
ruff check midnight_sdk/
mypy midnight_sdk/
```

### Project Structure

```
midnight-sdk/
├── midnight_sdk/              # Core SDK package
│   ├── __init__.py           # Main exports
│   ├── client.py             # MidnightClient class
│   ├── wallet.py             # Wallet operations
│   ├── ai.py                 # AI inference
│   ├── codegen.py            # Contract bindings generator
│   ├── cli/                  # Command-line interface
│   │   ├── __init__.py
│   │   ├── commands/         # CLI command modules
│   │   └── utils.py
│   ├── types.py              # Type definitions
│   ├── exceptions.py         # Custom exceptions
│   └── utils.py              # Utility functions
├── tests/                    # Test suite
├── examples/                 # Example scripts
├── pyproject.toml           # Package configuration
└── README.md                # This file
```

### Running Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests (requires local network)
pytest tests/integration/

# All tests
pytest

# With coverage
pytest --cov=midnight_sdk --cov-report=html
```

### Contributing Guidelines

1. **Fork the repository** and create a feature branch
2. **Write tests** for new functionality
3. **Follow code style** (ruff + mypy)
4. **Update documentation** as needed
5. **Submit a pull request** with clear description

### Code Style

We use `ruff` for linting and `mypy` for type checking:

```bash
# Format code
ruff format midnight_sdk/

# Check linting
ruff check midnight_sdk/

# Type checking
mypy midnight_sdk/
```

## � Security & Privacy

### Privacy Features

- **Shielded Transactions**: NIGHT tokens are private by default
- **Zero-Knowledge Proofs**: Prove computations without revealing data
- **Private AI**: Run ML inference while keeping data confidential
- **Cryptographic Signing**: All transactions are cryptographically signed

### Security Best Practices

```python
# ✅ Good: Store private keys securely
import os
private_key = os.getenv("MIDNIGHT_PRIVATE_KEY")

# ❌ Bad: Never hardcode private keys
private_key = "your_private_key_here"  # Don't do this!

# ✅ Good: Use environment variables or secure key management
from midnight_sdk.security import SecureKeyManager
key_manager = SecureKeyManager()
private_key = key_manager.get_key("main_wallet")
```

### Key Management

```python
from midnight_sdk import WalletManager

# Create secure wallet
wallet = WalletManager.create_wallet()
print(f"Address: {wallet.address}")
print(f"Mnemonic: {wallet.mnemonic}")  # Store securely!

# Load from mnemonic
wallet = WalletManager.from_mnemonic("your 24 word mnemonic phrase...")
private_key = wallet.get_private_key()
```

## 📊 Performance & Limits

### Performance Metrics

| Operation | Typical Time | Notes |
|-----------|--------------|-------|
| Contract Deployment | 3-5 seconds | Includes compilation + proof generation |
| Contract Call | 1-3 seconds | Depends on circuit complexity |
| ZK Proof Generation | 1-2 seconds | For standard circuits |
| Transaction Confirmation | 10-30 seconds | Network dependent |
| Balance Query | <1 second | Cached results |

### Rate Limits

- **Testnet**: 100 requests/minute per IP
- **Mainnet**: 50 requests/minute per IP
- **Local**: No limits

### Optimization Tips

```python
# Use connection pooling for better performance
client = MidnightClient(
    network="testnet",
    connection_pool_size=10,
    timeout=30
)

# Batch multiple operations
results = client.batch_operations([
    ("get_balance", {"address": addr1}),
    ("get_balance", {"address": addr2}),
    ("get_contract_state", {"address": contract_addr})
])
```

## 🚨 Troubleshooting

### Common Issues

#### Connection Issues
```bash
# Check network connectivity
midnight status

# Test specific endpoints
midnight node info
midnight block
```

#### Transaction Failures
```python
from midnight_sdk.exceptions import TransactionError, InsufficientFundsError

try:
    result = client.call_contract(...)
except InsufficientFundsError:
    print("Not enough DUST for transaction fees")
except TransactionError as e:
    print(f"Transaction failed: {e.message}")
    print(f"Error code: {e.code}")
```

#### Private Key Issues
```python
# Validate private key format
from midnight_sdk.utils import validate_private_key

if not validate_private_key(private_key):
    print("Invalid private key format")

# Check key permissions
balance = client.get_balance()
if balance.dust < 1000:
    print("Need DUST for transaction fees")
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug mode
client = MidnightClient(network="testnet", debug=True)
```

### Getting Help

- **GitHub Issues**: [Report bugs and request features](https://github.com/midnight-labs/midnight-python-sdk/issues)
- **Documentation**: Check the API reference above
- **Community**: Join the Midnight developer community
- **Examples**: See the `examples/` directory for working code

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the Midnight blockchain ecosystem
- Uses the official Midnight wallet SDK
- Inspired by the need for privacy-preserving applications
- Thanks to the Midnight Labs team for their support

## 🗺️ Roadmap

- [x] Core SDK implementation with full transaction support
- [x] Auto-generated Python bindings from Compact contracts
- [x] Cryptographic transaction signing with private keys
- [x] ZK-SNARK proof generation and verification
- [x] Privacy-preserving AI inference capabilities
- [x] Comprehensive CLI for all blockchain operations
- [x] Type-safe API with full IDE support
- [ ] Advanced contract interaction patterns
- [ ] Performance optimizations and caching
- [ ] Enhanced error handling and retry logic
- [ ] Additional privacy-preserving algorithms
- [ ] Integration with more Midnight ecosystem tools

---

**Made with ❤️ for privacy-preserving applications on Midnight**

*The first Python SDK that makes zero-knowledge blockchain development accessible to everyone.*
