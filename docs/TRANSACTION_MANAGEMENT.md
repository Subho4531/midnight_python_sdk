# Transaction Management Guide

## Overview

The Midnight SDK now includes a complete transaction lifecycle management system with:

- **Real transaction submission** to blockchain node
- **Automatic confirmation** after 3 seconds (simulates block time)
- **Manual approval/rejection** via CLI
- **Transaction status tracking** (pending, confirmed, rejected)
- **Explorer UI** with color-coded status badges

## Transaction Lifecycle

```
1. Submit → 2. Pending → 3. Confirmed/Rejected
```

### 1. Submit Transaction

Transactions are submitted when you run AI inference with signing:

```bash
python examples/ai_inference_with_signing.py
```

This creates a signed transaction with:
- ZK proof
- Model hash
- Prediction
- Confidence score
- Wallet signature

### 2. Pending Status

New transactions start in "pending" status. They can be:
- **Auto-confirmed** after 3 seconds (default behavior)
- **Manually approved** using the CLI
- **Manually rejected** using the CLI

### 3. Confirmed/Rejected

Once processed, transactions are either:
- **Confirmed** ✅ - Transaction executed successfully
- **Rejected** ❌ - Transaction failed or was rejected

## CLI Commands

### List All Transactions

```bash
python manage_transactions.py list
```

Shows:
- Total transaction count
- Breakdown by status (pending, confirmed, rejected)
- Pending transactions with approval commands
- Confirmed transactions with timestamps
- Rejected transactions with reasons

### Check Transaction Status

```bash
python manage_transactions.py status <tx_hash>
```

Example:
```bash
python manage_transactions.py status a9623dc60545140f9199834017e5956b47e689870cbda32623201e29b8d4992b
```

Shows detailed information:
- Transaction hash
- Status (pending/confirmed/rejected)
- Timestamp
- Block height
- Proof hash
- Prediction and confidence
- Model hash

### Approve Transaction

```bash
python manage_transactions.py approve <tx_hash>
```

Example:
```bash
python manage_transactions.py approve a9623dc60545140f9199834017e5956b47e689870cbda32623201e29b8d4992b
```

This:
1. Verifies the ZK proof
2. Executes the contract
3. Updates status to "confirmed"
4. Records confirmation timestamp

### Reject Transaction

```bash
python manage_transactions.py reject <tx_hash> [reason]
```

Example:
```bash
python manage_transactions.py reject f0e1843c6260775a8bdaedc0bcfa51b246a2bd83e66c37346cd57795dc625a73 "Invalid proof"
```

This:
1. Updates status to "rejected"
2. Records rejection reason
3. Records rejection timestamp

## Explorer UI

Access the explorer at: http://localhost:8088/

### Features

- **Home page** - Lists all transactions with status badges
- **Transaction details** - Click any transaction to see full details
- **Color-coded status**:
  - 🟠 Orange = Pending
  - 🟢 Green = Confirmed
  - 🔴 Red = Rejected
- **Real-time updates** - Refreshes every 5 seconds
- **Search** - Enter transaction hash to view details

### Transaction Details Page

Shows:
- Transaction hash
- Status badge (color-coded)
- Timestamp
- Block height
- Raw transaction data (JSON)
- Proof details
- Public inputs (prediction, confidence, model hash)
- Signature

## Auto-Confirmation

By default, transactions are automatically confirmed after 3 seconds. This simulates:
- Block production time
- Contract execution
- Proof verification

To disable auto-confirmation, you can modify the node server to not call `auto_process_transaction()`.

## Manual Workflow

For production use, you may want manual approval:

1. **Submit transaction**
   ```bash
   python examples/ai_inference_with_signing.py
   ```

2. **List pending transactions**
   ```bash
   python manage_transactions.py list
   ```

3. **Review transaction details**
   ```bash
   python manage_transactions.py status <tx_hash>
   ```

4. **Approve or reject**
   ```bash
   # Approve
   python manage_transactions.py approve <tx_hash>
   
   # Or reject
   python manage_transactions.py reject <tx_hash> "Reason for rejection"
   ```

5. **View in explorer**
   ```
   http://localhost:8088/tx/<tx_hash>
   ```

## API Endpoints

### Node (port 9944)

- `POST /` - JSON-RPC endpoint
  - `author_submitExtrinsic` - Submit transaction
  - `chain_confirmTransaction` - Confirm transaction
  - `chain_rejectTransaction` - Reject transaction
  - `system_health` - Health check

- `GET /tx/{hash}` - Get transaction details
- `GET /transactions` - List all transactions
- `GET /health` - Health check

### Indexer/Explorer (port 8088)

- `GET /` - Explorer home page
- `GET /tx/{hash}` - Transaction details page
- `POST /api/v4/graphql` - GraphQL API
- `GET /health` - Health check

## Docker Services

All services run in Docker with persistent storage:

```bash
# Start services
docker-compose up -d

# Check status
docker ps

# View logs
docker logs midnightsdk-midnight-node-1
docker logs midnightsdk-midnight-indexer-1
docker logs midnightsdk-proof-server-1

# Stop services
docker-compose down
```

### Data Persistence

Transaction data is persisted in:
- `./data/node/` - Transaction files (JSON)

This ensures transactions survive container restarts.

## Example Workflow

```bash
# 1. Start services
docker-compose up -d

# 2. Submit AI inference transaction
python examples/ai_inference_with_signing.py

# Output:
# [TX] Transaction hash: a9623dc60545140f9199834017e5956b...
# [TX] Explorer: http://localhost:8088/tx/a9623dc60545140f...

# 3. Wait 3 seconds for auto-confirmation
sleep 3

# 4. Check status
python manage_transactions.py status a9623dc60545140f9199834017e5956b...

# Output:
# Status: confirmed ✅
# Prediction: setosa
# Confidence: 100.00%

# 5. View in explorer
# Open: http://localhost:8088/tx/a9623dc60545140f...
```

## Troubleshooting

### Transaction stuck in pending

If auto-confirmation is disabled or failed:

```bash
# Manually approve
python manage_transactions.py approve <tx_hash>
```

### Transaction not found

Check if services are running:

```bash
docker ps
curl http://localhost:9944/health
curl http://localhost:8088/health
```

### Port conflicts

If port 9944 or 8088 is already in use:

```bash
# Find process using port
netstat -ano | Select-String ":9944"

# Kill process (Windows)
Stop-Process -Id <PID> -Force
```

## Production Considerations

For production deployment:

1. **Disable auto-confirmation** - Require manual approval for all transactions
2. **Add authentication** - Protect approval endpoints
3. **Implement proper ZK verification** - Use real cryptographic proof verification
4. **Add rate limiting** - Prevent spam transactions
5. **Use real blockchain** - Connect to Midnight testnet or mainnet
6. **Implement proper key management** - Use hardware wallets or HSMs
7. **Add monitoring** - Track transaction success rates and latency

## Next Steps

- Deploy contracts to Midnight testnet
- Integrate with real Midnight explorer (https://explorer.nocy.io/)
- Add multi-signature approval workflow
- Implement transaction batching
- Add gas fee estimation
