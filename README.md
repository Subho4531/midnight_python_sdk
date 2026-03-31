# midnight-py 🌙

**The first Python SDK for the Midnight blockchain**

Build privacy-preserving dApps with Zero-Knowledge Proofs using Python. Midnight is a ZK-privacy blockchain by IOG (the team behind Cardano) that lets you prove things without revealing private data.

## 5-Line Quickstart

```python
from midnight_py import MidnightClient, compact_to_python

client = MidnightClient(network="preprod")
BulletinBoard = compact_to_python("contracts/bulletin_board.compact")
contract = client.contracts.deploy("contracts/bulletin_board.compact", private_key="...")
board = BulletinBoard(contract)
board.post(message="Hello Midnight from Python!")
```

## Why midnight-py?

The official Midnight SDK is TypeScript-only. This brings the full power of Midnight to Python developers:

- ✅ **Complete SDK** — wallet, contracts, proofs, indexer
- ✅ **Auto-codegen** — turn `.compact` contracts into Python classes
- ✅ **pytest plugin** — test without Docker
- ✅ **Async support** — for high-performance apps
- ✅ **Type-safe** — Pydantic models everywhere
- ✅ **CLI included** — `midnight-py status`, `deploy`, `call`

## Installation

```bash
pip install midnight-py
```

Or for development:

```bash
git clone https://github.com/Samrat25/midnight_python_sdk
cd midnight_python_sdk
pip install -e ".[dev]"
```

## Prerequisites

You need the Midnight services running locally via Docker:

```bash
docker-compose up -d
```

This starts:
- Node (port 9944) — submit transactions
- Indexer (port 8088) — read contract state
- Proof Server (port 6300) — generate ZK proofs

## Features

### 1. Contract Codegen (Killer Feature)

Instead of manually writing wrappers, point at your `.compact` file:

```python
from midnight_py.codegen import compact_to_python

# Auto-generate Python class from Compact contract
VotingContract = compact_to_python("contracts/voting.compact")

# Use it like native Python
contract = client.get_contract("addr123", ["cast_vote"])
voting = VotingContract(contract)
voting.cast_vote(
    private_inputs={"choice": "candidate_A"},
    public_inputs={"election_id": "2024"}
)
```

### 2. Zero-Knowledge Proofs

```python
proof = client.prover.generate_proof(
    circuit_id="my_circuit",
    private_inputs={"secret": "data"},  # Never leaves your machine
    public_inputs={"result": 42}        # Visible on-chain
)
```

### 3. Wallet Operations

```python
balance = client.wallet.get_balance("mn_preprod1abc...")
print(f"DUST: {balance.dust}, NIGHT: {balance.night}")

address = client.wallet.generate_address("my seed phrase")
```

### 4. Contract State

```python
state = client.indexer.get_contract_state("contract_address")
print(f"Block {state.block_height}: {state.state}")
```

### 5. Real-time Events

```python
async for event in client.indexer.stream_events("contract_address"):
    print(f"New event: {event}")
```

## CLI Usage

```bash
# Check services
midnight-py status

# Deploy contract
midnight-py deploy contracts/my_contract.compact --key <private_key>

# Call circuit function
midnight-py call <address> <circuit_name> --args '{"param": "value"}'

# Read state
midnight-py state <address>

# Check balance
midnight-py balance <wallet_address>
```

## Testing

midnight-py includes a pytest plugin with mocked services:

```python
def test_my_feature(midnight_client):
    # midnight_client is fully mocked, no Docker needed
    status = midnight_client.status()
    assert status["node"] == True
```

Run tests:

```bash
pytest
```

## Examples

Check the `examples/` directory:

- `bulletin_board.py` — Simple message posting
- `private_vote.py` — Anonymous voting
- `ai_inference.py` — ML model with ZK proofs

## Architecture

```
midnight_py/
├── client.py        # MidnightClient (main entry)
├── wallet.py        # Keys, signing, balance
├── contract.py      # Deploy & call contracts
├── proof.py         # ZK proof generation
├── indexer.py       # Read on-chain state
├── codegen.py       # .compact → Python classes
├── models.py        # Pydantic data models
├── exceptions.py    # Custom errors
└── cli.py           # Command-line interface
```

## Comparison: midnight-py vs TypeScript SDK

| Feature | TypeScript SDK | midnight-py |
|---------|---------------|-------------|
| Contract deployment | ✅ | ✅ |
| ZK proof generation | ✅ | ✅ |
| Wallet management | ✅ | ✅ |
| GraphQL indexer | ✅ | ✅ |
| Auto-codegen from .compact | ❌ | ✅ |
| pytest plugin | ❌ | ✅ |
| CLI tool | ❌ | ✅ |
| Async/await | ✅ | ✅ |
| Type safety | ✅ | ✅ (Pydantic) |

## Contributing

This is a hackathon project! Contributions welcome:

1. Fork the repo
2. Create a feature branch
3. Add tests
4. Submit a PR

## License

MIT

## Links

- [Midnight Docs](https://docs.midnight.network)
- [Compact Language Spec](https://docs.midnight.network/compact)
- [IOG](https://iohk.io)

---

Built with ❤️ for the Midnight hackathon
