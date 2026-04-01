# Quick Start Guide

Get up and running with Midnight Python SDK in 5 minutes.

## 1. Install (1 minute)

```bash
# Install package
pip install -e .

# Install Node dependencies
npm install

# Verify
midnight-py --help
```

## 2. Configure (1 minute)

```bash
# Create mnemonic file
echo "your 24 word mnemonic phrase here" > mnemonic.txt

# Get wallet address
node get_wallet_address.mjs

# Fund wallet at https://faucet.midnight.network/
```

## 3. Start Services (1 minute)

```bash
# Start Docker services
docker-compose up -d

# Verify
midnight-py status
```

## 4. Run AI Inference (2 minutes)

```bash
# Train model
midnight-py ai train

# Run inference with transaction signing
midnight-py ai infer --features "5.1,3.5,1.4,0.2" --sign

# Check transaction
midnight-py tx list
```

## 5. View in Explorer

Open: http://localhost:8088/

## Common Commands

```bash
# List transactions
midnight-py tx list

# Check transaction status
midnight-py tx status <tx_hash>

# Approve transaction
midnight-py tx approve <tx_hash>

# Run complete workflow
python examples/complete_transaction_workflow.py
```

## Troubleshooting

```bash
# Restart services
docker-compose restart

# Check logs
docker logs midnightsdk-midnight-node-1

# Kill port conflicts
netstat -ano | Select-String ":9944"
Stop-Process -Id <PID> -Force
```

## Next Steps

- Read `DEPLOYMENT_GUIDE.md` for full documentation
- Read `TRANSACTION_MANAGEMENT.md` for transaction details
- Explore `examples/` directory for more examples
