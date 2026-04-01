# Quick Transaction Signing Guide

## Prerequisites

1. **Mnemonic file** - Create `mnemonic.txt` with your 24-word mnemonic
2. **Services running** - `docker-compose up -d`
3. **Python packages** - `pip install -e .`

## Quick Start

### 1. Test Everything

```bash
python test_signing_examples.py
```

This will:
- ✅ Check all services
- ✅ Test AI inference with signing
- ✅ Test bulletin board with signing
- ✅ Verify explorer integration
- ✅ Show recent transactions

### 2. Run Signing Examples

**AI Inference:**
```bash
python examples/ai_inference_with_signing.py
```

**Bulletin Board:**
```bash
python examples/bulletin_board_with_signing.py
```

### 3. View in Explorer

Open browser: `http://localhost:8088`

## Code Examples

### Basic Signing

```python
from midnight_py import MidnightClient
from pathlib import Path

# 1. Create client
client = MidnightClient(
    network="undeployed",
    wallet_address="your_address"
)

# 2. Get private key
mnemonic = Path("mnemonic.txt").read_text().strip()
keys = client.wallet.get_private_keys(mnemonic)
private_key = keys['nightExternal']

# 3. Create transaction
tx = {
    "contractAddress": "contract_addr",
    "circuit": "method_name",
    "data": {...},
    "proof": "zk_proof..."
}

# 4. Sign transaction
signed_tx = client.wallet.sign_transaction(tx, private_key)

# 5. Submit to blockchain
result = client.wallet.submit_transaction(signed_tx)

# 6. Get explorer URL
from midnight_py.wallet import get_explorer_url
url = get_explorer_url(result.tx_hash, "undeployed")
print(f"View: {url}")
```

### AI Inference with Signing

```python
from midnight_py import MidnightClient
from pathlib import Path

client = MidnightClient(network="undeployed")

# Get private key
mnemonic = Path("mnemonic.txt").read_text().strip()
keys = client.wallet.get_private_keys(mnemonic)
private_key = keys['nightExternal']

# Run inference with signing
result = client.ai.predict_private(
    features=[5.1, 3.5, 1.4, 0.2],
    sign_transaction=True,
    private_key=private_key
)

print(f"Transaction: {result.transaction_hash}")
print(f"Explorer: http://localhost:8088/tx/{result.transaction_hash}")
```

### Bulletin Board with Signing

```python
from midnight_py import MidnightClient
from midnight_py.codegen import compact_to_python
from pathlib import Path

client = MidnightClient(network="undeployed")

# Get private key
mnemonic = Path("mnemonic.txt").read_text().strip()
keys = client.wallet.get_private_keys(mnemonic)
private_key = keys['nightExternal']

# Generate Python class from contract
BulletinBoard = compact_to_python("contracts/bulletin_board.compact")

# Create and sign transaction
tx = {
    "contractAddress": "bulletin_board_addr",
    "circuit": "post",
    "message": "Hello Midnight!",
    "proof": "zk_proof..."
}

signed_tx = client.wallet.sign_transaction(tx, private_key)
result = client.wallet.submit_transaction(signed_tx)

print(f"Posted! View: http://localhost:8088/tx/{result.tx_hash}")
```

## Explorer Features

### Home Page
- **URL:** `http://localhost:8088`
- **Features:**
  - Recent transactions list
  - Auto-refresh every 5 seconds
  - Search by transaction hash
  - Transaction status indicators

### Transaction Detail
- **URL:** `http://localhost:8088/tx/{hash}`
- **Features:**
  - Full transaction data
  - Status, timestamp, block height
  - Raw JSON view
  - Back to home link

## Transaction Status

| Status | Meaning |
|--------|---------|
| `pending` | Submitted, waiting for processing |
| `confirmed` | Processed successfully |
| `rejected` | Failed validation |

**Processing time:** ~3 seconds

## Troubleshooting

### Services Not Running

```bash
# Check status
docker-compose ps

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Mnemonic Not Found

```bash
# Create mnemonic.txt
echo "your 24 word mnemonic here" > mnemonic.txt
```

### Transaction Not Appearing

1. Wait 3 seconds for processing
2. Refresh explorer page
3. Check node logs: `docker-compose logs midnight-node`

### Explorer Not Loading

```bash
# Check indexer
curl http://localhost:8088/health

# Restart if needed
docker-compose restart midnight-indexer
```

## API Endpoints

### Node (port 9944)

```bash
# Health check
curl http://localhost:9944/health

# Get transaction
curl http://localhost:9944/tx/{hash}

# List all transactions
curl http://localhost:9944/transactions
```

### Indexer/Explorer (port 8088)

```bash
# Health check
curl http://localhost:8088/health

# GraphQL endpoint
curl -X POST http://localhost:8088/api/v4/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}'
```

## Testing Checklist

- [ ] Services running (`docker-compose ps`)
- [ ] Mnemonic file exists (`cat mnemonic.txt`)
- [ ] Test script passes (`python test_signing_examples.py`)
- [ ] AI inference works (`python examples/ai_inference_with_signing.py`)
- [ ] Bulletin board works (`python examples/bulletin_board_with_signing.py`)
- [ ] Explorer shows transactions (`http://localhost:8088`)
- [ ] Transaction details load (`http://localhost:8088/tx/{hash}`)

## Quick Commands

```bash
# Run all tests
python test_signing_examples.py

# Test AI inference
python examples/ai_inference_with_signing.py

# Test bulletin board
python examples/bulletin_board_with_signing.py

# Check services
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down
```

## Files Created

| File | Purpose |
|------|---------|
| `test_signing_examples.py` | Comprehensive test script |
| `examples/ai_inference_with_signing.py` | AI inference with signing |
| `examples/bulletin_board_with_signing.py` | Bulletin board with signing |
| `EXPLORER_AND_SIGNING_VERIFICATION.md` | Detailed verification doc |
| `QUICK_SIGNING_GUIDE.md` | This quick reference |

## Success Indicators

✅ All services show "OK" in test script  
✅ Transactions appear in explorer  
✅ Transaction status updates after 3 seconds  
✅ Explorer shows 30+ transactions  
✅ Transaction detail pages load  

## Next Steps

1. Run the test script to verify everything
2. Try the signing examples
3. View transactions in explorer
4. Create your own signed transactions
5. Test with different contracts

Happy signing! 🚀
