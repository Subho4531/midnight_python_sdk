# 📁 Project Structure

## Overview

```
midnight-python-sdk/
├── 📦 midnight_py/              # Core SDK package
├── 📜 contracts/                # Compact smart contracts
├── 🐳 docker/                   # Docker services
├── 💡 examples/                 # Example scripts
├── 🧪 tests/                    # Test suite
├── 📚 docs/                     # Documentation
├── 🔧 Configuration files
└── 📄 README.md
```

## Detailed Structure

### Core SDK (`midnight_py/`)

```
midnight_py/
├── __init__.py              # Package initialization
├── client.py                # Main MidnightClient
├── wallet.py                # Wallet operations & signing
├── ai.py                    # AI inference with ZK
├── codegen.py               # Auto-codegen from Compact
├── compiler.py              # Contract compilation
├── proof.py                 # Proof server client
├── indexer.py               # GraphQL indexer client
├── models.py                # Data models
├── exceptions.py            # Custom exceptions
└── cli.py                   # Command-line interface
```

**Key Components:**

- **client.py**: Main entry point, orchestrates all services
- **wallet.py**: Derives addresses, signs transactions, submits to blockchain
- **ai.py**: ZK-ML inference with privacy guarantees
- **codegen.py**: Generates Python classes from `.compact` files
- **compiler.py**: Compiles Compact contracts using `compactc`
- **proof.py**: Communicates with proof server for ZK-SNARK generation

### Contracts (`contracts/`)

```
contracts/
├── hello_world.compact          # Simple message storage
├── counter.compact              # Increment counter
├── bulletin_board.compact       # Anonymous message board
├── ai_inference.compact         # AI inference contract
├── private_vote.compact         # Private voting
└── managed/                     # Compiled contracts
    ├── hello_world/
    │   ├── compiler/            # Compilation artifacts
    │   ├── contract/            # Generated JS
    │   └── zkir/                # ZK intermediate representation
    ├── counter/
    ├── bulletin_board/
    ├── ai_inference/
    └── private_vote/
```

**Contract Types:**

- **hello_world**: Basic contract for testing
- **counter**: State management example
- **bulletin_board**: Privacy-preserving messaging
- **ai_inference**: ZK-ML inference
- **private_vote**: Anonymous voting system

### Docker Services (`docker/`)

```
docker/
├── node/
│   ├── Dockerfile               # Midnight node image
│   └── server.py                # Node server implementation
├── indexer/
│   ├── Dockerfile               # Indexer + Explorer image
│   └── server.py                # GraphQL API + Web UI
└── proof/
    ├── Dockerfile               # Proof server image
    └── server.py                # ZK-SNARK proof generation
```

**Services:**

1. **Node (port 9944)**
   - Stores transactions
   - Processes contracts
   - Validates proofs
   - Maintains blockchain state

2. **Indexer (port 8088)**
   - GraphQL API
   - Transaction explorer UI
   - Real-time updates
   - Query interface

3. **Proof Server (port 6300)**
   - Generates ZK-SNARK proofs
   - Compiles circuits
   - Validates proofs

### Examples (`examples/`)

```
examples/
├── ai_inference_with_signing.py          # AI + signing
├── bulletin_board_with_signing.py        # Message board + signing
├── bulletin_board.py                     # Auto-codegen demo
├── complete_transaction_workflow.py      # Full workflow
└── production_ai_inference.py            # Production example
```

**Example Categories:**

- **Basic**: Simple contract interactions
- **Signing**: Transaction signing demonstrations
- **AI**: ZK-ML inference examples
- **Production**: Production-ready patterns

### Tests (`tests/`)

```
tests/
├── test_wallet.py               # Wallet operations
├── test_compiler.py             # Contract compilation
├── test_codegen.py              # Auto-codegen
├── test_ai.py                   # AI inference
└── test_integration.py          # End-to-end tests
```

### Documentation (`docs/`)

```
docs/
├── QUICK_START.md                        # 5-minute setup
├── DOCKER_SETUP.md                       # Docker guide
├── CONTRACT_TESTING_GUIDE.md             # Testing contracts
├── QUICK_SIGNING_GUIDE.md                # Transaction signing
├── EXPLORER_AND_SIGNING_VERIFICATION.md  # Explorer guide
├── PRODUCTION_SETUP.md                   # Production deployment
├── DEPLOYMENT_GUIDE.md                   # Deployment steps
├── TRANSACTION_MANAGEMENT.md             # Transaction handling
└── PROJECT_STRUCTURE.md                  # This file
```

### Configuration Files

```
Root Directory/
├── docker-compose.yml           # Docker services configuration
├── pyproject.toml               # Python package configuration
├── package.json                 # Node.js dependencies (wallet SDK)
├── package_wallet.json          # Wallet SDK specific deps
├── Makefile                     # Build automation
├── setup.sh                     # Setup script
├── .gitignore                   # Git ignore rules
├── LICENSE                      # MIT License
└── CONTRIBUTING.md              # Contribution guidelines
```

## File Purposes

### Root Level Scripts

| File | Purpose |
|------|---------|
| `check_services.py` | Verify all services are running |
| `start_services.py` | Start Docker services |
| `start_proof_server.py` | Start proof server standalone |
| `manage_transactions.py` | Transaction management CLI |
| `run_all_tests.py` | Run complete test suite |
| `test_signing_examples.py` | Test signing functionality |
| `verify_all.py` | Verify complete installation |

### Helper Scripts

| File | Purpose |
|------|---------|
| `get_wallet_address.mjs` | Derive wallet address from mnemonic |
| `get_private_key.mjs` | Derive private keys from mnemonic |

## Data Flow

### Transaction Submission

```
1. User Code
   ↓
2. MidnightClient.wallet.sign_transaction()
   ↓
3. Sign with private key (SHA256)
   ↓
4. Submit to Node (port 9944)
   ↓
5. Node stores & processes
   ↓
6. Indexer fetches (port 8088)
   ↓
7. Explorer displays
```

### ZK Proof Generation

```
1. User Code
   ↓
2. MidnightClient.ai.predict_private()
   ↓
3. Compile contract (compactc)
   ↓
4. Generate proof (Proof Server :6300)
   ↓
5. Sign transaction
   ↓
6. Submit to blockchain
```

### Contract Auto-Codegen

```
1. .compact file
   ↓
2. compact_to_python()
   ↓
3. Parse contract structure
   ↓
4. Generate Python class
   ↓
5. Return type-safe API
```

## Key Directories

### Must Keep

- ✅ `midnight_py/` - Core SDK
- ✅ `contracts/` - Smart contracts
- ✅ `docker/` - Services
- ✅ `examples/` - Examples
- ✅ `tests/` - Tests
- ✅ `docs/` - Documentation

### Generated/Temporary

- ⚠️ `contracts/managed/` - Compiled contracts (regenerated)
- ⚠️ `node_modules/` - Node dependencies (npm install)
- ⚠️ `.pytest_cache/` - Test cache
- ⚠️ `__pycache__/` - Python cache

### Sensitive (Gitignored)

- 🔒 `mnemonic.txt` - Your mnemonic phrase
- 🔒 `.wallet_*.json` - Wallet data
- 🔒 `accounts.json` - Account information
- 🔒 `data/` - Transaction data

## Build Artifacts

### Python Package

```
build/
dist/
*.egg-info/
```

### Docker Images

```
midnightsdk-midnight-node
midnightsdk-midnight-indexer
midnightsdk-midnight-proof
```

### Compiled Contracts

```
contracts/managed/*/
├── compiler/contract-info.json
├── contract/index.js
└── zkir/*.zkir
```

## Environment Variables

### Docker Compose

```yaml
NODE_URL: http://midnight-node:9944
INDEXER_URL: http://midnight-indexer:8088
PROOF_SERVER_URL: http://midnight-proof:6300
```

### Python SDK

```python
MIDNIGHT_NETWORK: undeployed | testnet | mainnet
MIDNIGHT_NODE_URL: http://localhost:9944
MIDNIGHT_PROOF_URL: http://localhost:6300
```

## Dependencies

### Python

```
aiohttp>=3.9.0
httpx>=0.25.0
pydantic>=2.0.0
rich>=13.0.0
click>=8.1.0
scikit-learn>=1.3.0
joblib>=1.3.0
```

### Node.js

```
@midnight-ntwrk/wallet-sdk-hd
@midnight-ntwrk/compact-compiler
```

### System

```
Docker 20.10+
Docker Compose 2.0+
Python 3.11+
Node.js 22+
```

## Size Information

### Package Sizes

- SDK: ~500 KB
- Contracts: ~100 KB
- Docker images: ~2 GB total
- Documentation: ~200 KB

### Runtime Memory

- Node: ~200 MB
- Indexer: ~100 MB
- Proof Server: ~300 MB
- Python SDK: ~50 MB

## Maintenance

### Regular Updates

- Update dependencies: `pip install -U -e .`
- Rebuild Docker: `docker-compose build`
- Clean cache: `make clean`

### Cleanup Commands

```bash
# Remove Python cache
find . -type d -name __pycache__ -exec rm -rf {} +

# Remove compiled contracts
rm -rf contracts/managed/

# Remove Docker volumes
docker-compose down -v

# Remove all build artifacts
make clean
```

## Best Practices

### Development

1. Use virtual environment
2. Install in editable mode: `pip install -e .`
3. Run tests before committing
4. Keep documentation updated

### Production

1. Use specific versions in requirements
2. Build optimized Docker images
3. Enable logging
4. Monitor service health

### Security

1. Never commit `mnemonic.txt`
2. Keep wallet files private
3. Use environment variables for secrets
4. Regularly update dependencies

---

This structure is designed for:
- ✅ Easy navigation
- ✅ Clear separation of concerns
- ✅ Scalability
- ✅ Maintainability
- ✅ Developer experience
