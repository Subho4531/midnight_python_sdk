# Production Setup - Real Midnight Testnet

## Quick Start (Production)

### 1. Install Dependencies

```bash
pip install -e ".[dev]"
npm install  # For wallet SDK
```

### 2. Start Real Proof Server

```bash
# Pull official Midnight proof server
docker pull ghcr.io/midnight-ntwrk/proof-server:latest

# Run it
docker run -d \
  --name midnight-proof-server \
  -p 6300:6300 \
  ghcr.io/midnight-ntwrk/proof-server:latest

# Verify
curl http://localhost:6300/health
```

### 3. Get Testnet Tokens

1. Visit: https://faucet.testnet.midnight.network
2. Enter your wallet address (derive it first - see below)
3. Request DUST and NIGHT tokens
4. Wait for confirmation

### 4. Configure Wallet

```bash
# Create mnemonic.txt with your 24-word mnemonic
echo "your twenty four word mnemonic phrase here..." > mnemonic.txt

# OR set environment variable
export MIDNIGHT_MNEMONIC="your twenty four word mnemonic phrase here..."
```

### 5. Run Production Example

```bash
python examples/production_ai_inference.py
```

## Network Endpoints

### Testnet (Production)

- **RPC Node:** https://rpc.testnet.midnight.network
- **Indexer:** https://indexer.testnet.midnight.network/api/v3/graphql
- **Explorer:** https://explorer.testnet.midnight.network
- **Faucet:** https://faucet.testnet.midnight.network
- **Status:** https://status.midnight.network

### Local (Development)

- **RPC Node:** http://localhost:9944
- **Indexer:** http://localhost:8088/api/v3/graphql
- **Proof Server:** http://localhost:6300

## Explorer Links

### View Transaction

```
https://explorer.testnet.midnight.network/tx/{transaction_hash}
```

Example:
```
https://explorer.testnet.midnight.network/tx/f992de1239bdc167eeaab86bcda6a9e8f7cfc0ef71a6d6ee5b6cd4ac42ce14cc
```

### View Wallet

```
https://explorer.testnet.midnight.network/address/{wallet_address}
```

Example:
```
https://explorer.testnet.midnight.network/address/mn_testnet1abc123def456...
```

### View Block

```
https://explorer.testnet.midnight.network/block/{block_number}
```

## Production Code Example

```python
from midnight_py import MidnightClient
from midnight_py.wallet import WalletClient
from pathlib import Path

# 1. Load mnemonic
mnemonic = Path("mnemonic.txt").read_text().strip()

# 2. Derive wallet address
wallet = WalletClient()
address_info = wallet.get_real_address(mnemonic, network_id="testnet")
wallet_address = address_info['address']

print(f"Wallet: {wallet_address}")
print(f"Explorer: https://explorer.testnet.midnight.network/address/{wallet_address}")

# 3. Connect to REAL testnet
client = MidnightClient(
    network="preprod",  # Real testnet
    wallet_address=wallet_address
)

# 4. Check services
status = client.status()
print(f"Node: {status['node']}")      # Should be True
print(f"Indexer: {status['indexer']}")  # Should be True
print(f"Prover: {status['prover']}")    # Should be True

# 5. Get private key
keys = wallet.get_private_keys(mnemonic)
private_key = keys['nightExternal']

# 6. Train model
client.ai.train_iris()

# 7. Run ZK inference with REAL proof and signing
result = client.ai.predict_private(
    features=[5.1, 3.5, 1.4, 0.2],
    sign_transaction=True,
    private_key=private_key
)

# 8. View in explorer
print(f"Transaction: https://explorer.testnet.midnight.network/tx/{result.transaction_hash}")
```

## Verification Steps

### 1. Verify Proof Server

```bash
curl http://localhost:6300/health
```

Expected response:
```json
{"status": "healthy", "service": "midnight-proof-server"}
```

### 2. Verify Testnet Connection

```bash
curl https://rpc.testnet.midnight.network/health
```

### 3. Verify Indexer

```bash
curl -X POST https://indexer.testnet.midnight.network/api/v3/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}'
```

### 4. Run Test

```bash
python examples/production_ai_inference.py
```

Expected output:
```
[1/7] Loading wallet configuration...
[2/7] Deriving wallet address...
[3/7] Connecting to Midnight testnet...
[4/7] Training ML model...
[5/7] Deriving private key for signing...
[6/7] Running ZK inference on testnet...
  NOTE: REAL ZK proof generation takes 10-30 seconds
  Generating proof...
  OK Proof generated!
  OK Transaction signed!
  OK Submitted to testnet!
[7/7] Results
...
EXPLORER LINKS:
  Transaction: https://explorer.testnet.midnight.network/tx/...
  Wallet: https://explorer.testnet.midnight.network/address/...
```

## Troubleshooting

### Proof Server Not Running

**Error:** `ProofServerConnectionError: Proof server not running on localhost:6300`

**Solution:**
```bash
docker run -d -p 6300:6300 ghcr.io/midnight-ntwrk/proof-server:latest
```

### Insufficient Balance

**Error:** `InsufficientFundsError: Not enough DUST/NIGHT`

**Solution:**
1. Visit https://faucet.testnet.midnight.network
2. Enter your wallet address
3. Request tokens
4. Wait 1-2 minutes

### Network Unreachable

**Error:** `ConnectionError: Cannot connect to https://rpc.testnet.midnight.network`

**Solution:**
1. Check internet connection
2. Verify testnet status: https://status.midnight.network
3. Try again in a few minutes

### Transaction Pending

**Issue:** Transaction shows as "pending" in explorer

**Solution:**
- Wait 1-2 minutes for confirmation
- Testnet blocks are produced every ~10 seconds
- Refresh explorer page

## Production vs Development

| Feature | Development (undeployed) | Production (preprod) |
|---------|-------------------------|---------------------|
| Network | Local | Testnet |
| Node | localhost:9944 | rpc.testnet.midnight.network |
| Indexer | localhost:8088 | indexer.testnet.midnight.network |
| Proof Server | Mock (instant) | Real (10-30s) |
| Transactions | Local only | On blockchain |
| Explorer | No link | https://explorer.testnet.midnight.network |
| Tokens | Unlimited | From faucet |

## Security Notes

### DO NOT Commit

- ❌ `mnemonic.txt` - Contains your private keys
- ❌ `.env` - Contains sensitive configuration
- ❌ `*.key` - Private key files
- ❌ `.wallet_*.json` - Wallet data

### DO Commit

- ✅ `examples/` - Example code
- ✅ `midnight_py/` - SDK code
- ✅ `tests/` - Test code
- ✅ `README.md` - Documentation

### .gitignore

Make sure your `.gitignore` includes:
```
mnemonic.txt
.env
.env.*
*.key
*.pem
.wallet_*.json
accounts.json
```

## Production Checklist

Before deploying to production:

- [ ] Real proof server running (not mock)
- [ ] Connected to testnet (not local)
- [ ] Wallet funded with testnet tokens
- [ ] Mnemonic stored securely (not in git)
- [ ] All services online (node, indexer, prover)
- [ ] Test transaction submitted successfully
- [ ] Transaction visible in explorer
- [ ] Receipt saved with real data

## Support

- **Documentation:** https://docs.midnight.network
- **Explorer:** https://explorer.testnet.midnight.network
- **Faucet:** https://faucet.testnet.midnight.network
- **Status:** https://status.midnight.network
- **Discord:** https://discord.gg/midnight

## Summary

✅ **Production-Ready:**
- Real Midnight testnet
- Real ZK proof generation
- Real transaction signing
- Real blockchain submission
- Real explorer verification

✅ **No Mocks:**
- No simulated proofs
- No fake transactions
- No mock data
- All operations are real

✅ **Verifiable:**
- View transactions in explorer
- Check wallet balance
- Verify proof hashes
- Audit on blockchain

The Midnight Python SDK is production-ready for the real Midnight testnet!
