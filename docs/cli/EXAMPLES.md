# CLI Examples

Practical examples for common Midnight SDK CLI workflows.

## Getting Started

### Initialize and Configure

```bash
# Initialize configuration
midnight config init

# View configuration
midnight config list

# Switch to preprod network
midnight config use preprod

# Check service status
midnight status
```

### Create and Manage Wallets

```bash
# Create new wallet
midnight wallet new deployer

# Import existing wallet
midnight wallet import my-wallet --mnemonic "word1 word2 ... word24"

# List all wallets
midnight wallet list

# Check balance
midnight wallet balance

# Show address
midnight wallet address deployer
```

## Contract Development

### Compile and Deploy

```bash
# Compile contract
midnight contract compile contracts/counter.compact

# Deploy to local network
midnight contract deploy contracts/counter.compact --wallet deployer

# Deploy to preprod
midnight contract deploy contracts/counter.compact --wallet deployer --profile preprod
```

### Interact with Contracts

```bash
# Call increment circuit
midnight contract call <address> increment --wallet deployer

# Call with arguments
midnight contract call <address> setValue --args '{"value": 42}' --wallet deployer

# Query state
midnight contract query <address> getValue

# Listen to events
midnight contract events <address> --follow
```

## Transaction Management

### Build and Sign Offline

```bash
# Build unsigned transaction
midnight tx build

# Follow prompts:
# Transaction type: call
# Contract address: <address>
# Circuit name: increment
# Arguments: {}
# Nonce: (optional)
# Fee: (optional)

# Sign on air-gapped machine
midnight tx sign unsigned_tx.json --wallet cold-wallet --output signed_tx.json

# Submit from online machine
midnight tx submit signed_tx.json
```

### Monitor Transactions

```bash
# Check status
midnight tx status <hash>

# Watch until finality
midnight tx watch <hash>

# View transaction details
midnight tx decode <hash>

# Transaction history
midnight tx history <address>
```

## AI Inference

### Train and Deploy Model

```bash
# Prepare training data (CSV format)
# features1,features2,features3,label
# 1.0,2.0,3.0,0
# 4.0,5.0,6.0,1

# Train model
midnight ai train training_data.csv --name fraud-detector

# Test inference locally
midnight ai infer '[1.0, 2.0, 3.0]' --model fraud-detector

# Run inference with on-chain proof
midnight ai infer '[1.0, 2.0, 3.0]' --model fraud-detector --sign --wallet my-wallet
```

### Manage Models

```bash
# List trained models
midnight ai model-list

# Show model details
midnight ai model-info fraud-detector
```

## ZK Proofs

### Generate and Verify

```bash
# Generate proof
midnight proof generate increment '{"value": 1}' --output proof.json

# Verify proof
midnight proof verify proof.json

# Show circuit info
midnight proof info increment
```

## Network Operations

### Check Service Health

```bash
# Check all services
midnight system status

# Show SDK info
midnight system info

# View service logs (Docker)
midnight system logs node --follow
midnight system logs indexer --lines 100
```

### Raw RPC Calls

```bash
# Node status
midnight node status

# List peers
midnight node peers

# Custom RPC call
midnight node rpc chain_getBlock --params '["latest"]'
```

## Event Monitoring

### Subscribe to Events

```bash
# Listen to all events
midnight events listen

# Filter by contract
midnight events listen --contract <address>

# Filter by type
midnight events listen --type Transfer

# Query historical events
midnight events query --contract <address> --from 1000 --to 2000 --limit 100
```

## Explorer Integration

### Open in Browser

```bash
# Open explorer
midnight explorer open

# View transaction
midnight explorer open <tx_hash>

# View address
midnight explorer address <address>

# View block
midnight explorer block 12345
```

## Interactive Console

### REPL Session

```bash
# Start console
midnight console --profile preprod

# In console:
>>> client.status()
{'node': True, 'indexer': True, 'prover': True}

>>> balance = client.indexer.get_balance("mn_addr_...")
>>> print(f"DUST: {balance.dust}")

>>> block = client.indexer.get_latest_block()
>>> print(f"Height: {block['height']}")
```

## Advanced Workflows

### Multi-Network Deployment

```bash
# Deploy to local for testing
midnight contract deploy contracts/my_contract.compact --profile local --wallet test

# Test locally
midnight contract call <local_address> testFunction --profile local --wallet test

# Deploy to preprod
midnight contract deploy contracts/my_contract.compact --profile preprod --wallet deployer

# Verify on preprod
midnight contract info <preprod_address> --profile preprod
```

### Automated Testing

```bash
#!/bin/bash
# test_contract.sh

# Deploy contract
ADDRESS=$(midnight contract deploy contracts/counter.compact --wallet test --profile local | grep "Address:" | awk '{print $2}')

# Call increment 5 times
for i in {1..5}; do
  midnight contract call $ADDRESS increment --wallet test --profile local
done

# Verify final count
COUNT=$(midnight contract query $ADDRESS getCount --profile local | jq '.count')

if [ "$COUNT" -eq 5 ]; then
  echo "✓ Test passed"
else
  echo "✗ Test failed: expected 5, got $COUNT"
  exit 1
fi
```

### Batch Operations

```bash
#!/bin/bash
# batch_deploy.sh

CONTRACTS=(
  "contracts/counter.compact"
  "contracts/bulletin_board.compact"
  "contracts/private_vote.compact"
)

for contract in "${CONTRACTS[@]}"; do
  echo "Deploying $contract..."
  midnight contract deploy "$contract" --wallet deployer --profile preprod
  sleep 5  # Wait between deployments
done
```

### Monitoring Script

```bash
#!/bin/bash
# monitor.sh

while true; do
  clear
  echo "=== Midnight Network Status ==="
  midnight system status --profile preprod
  
  echo ""
  echo "=== Latest Block ==="
  midnight node status --profile preprod | jq '.height'
  
  sleep 10
done
```

## Configuration Management

### Multiple Profiles

```bash
# Add custom network
midnight config add-network custom \
  --node https://rpc.custom.network \
  --indexer https://indexer.custom.network/graphql \
  --indexer-ws wss://indexer.custom.network/graphql/ws \
  --proof https://proof.custom.network \
  --network-id custom \
  --explorer https://explorer.custom.network

# Switch between networks
midnight config use local      # Local development
midnight config use preprod    # Pre-production testing
midnight config use custom     # Custom network
midnight config use mainnet    # Production

# View active profile
midnight config get active_profile
```

### Wallet Organization

```bash
# Create wallets for different purposes
midnight wallet new deployer      # For contract deployment
midnight wallet new tester        # For testing
midnight wallet new cold-wallet   # For offline signing

# Set default wallet
midnight config set default_wallet deployer

# Use specific wallet
midnight contract deploy contracts/my_contract.compact --wallet tester
```

## Output Formatting

### JSON Output

```bash
# Get JSON output
midnight config list --output json > config.json
midnight tx status <hash> --output json | jq '.status'
midnight wallet balance --output json | jq '.dust'
```

### Table Output

```bash
# Default table format
midnight wallet list
midnight contract list
midnight tx list
```

### YAML Output

```bash
# YAML format
midnight config list --output yaml
```

## Troubleshooting

### Debug Mode

```bash
# Verbose output
midnight --verbose contract deploy contracts/my_contract.compact

# Quiet mode (errors only)
midnight --quiet tx submit signed_tx.json
```

### Service Diagnostics

```bash
# Check all services
midnight system status

# View logs
midnight system logs node
midnight system logs indexer --follow

# Test connectivity
midnight node status
midnight node peers
```

### Wallet Issues

```bash
# List wallets
midnight wallet list

# Check balance
midnight wallet balance --profile preprod

# Export for debugging (careful!)
midnight wallet export my-wallet --private-key
```

## Best Practices

1. **Use profiles for different networks**
2. **Store mnemonics securely**
3. **Test on local/preprod before mainnet**
4. **Use offline signing for production**
5. **Monitor transaction status**
6. **Keep configuration in version control (without secrets)**
7. **Use meaningful wallet names**
8. **Regularly check service health**

## Tips and Tricks

### Aliases

Add to your shell profile:

```bash
alias mn='midnight'
alias mnw='midnight wallet'
alias mnc='midnight contract'
alias mnt='midnight tx'
alias mns='midnight system status'
```

### Environment Variables

```bash
# Set default profile
export MIDNIGHT_PROFILE=preprod

# Set config location
export MIDNIGHT_CONFIG=~/.midnight/custom-config.yaml
```

### Shell Completion

```bash
# Generate completion script
midnight --install-completion

# Or manually:
eval "$(_MIDNIGHT_COMPLETE=bash_source midnight)"  # Bash
eval "$(_MIDNIGHT_COMPLETE=zsh_source midnight)"   # Zsh
```
