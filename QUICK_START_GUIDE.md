# Midnight SDK CLI - Quick Start Guide

## Installation

```bash
# Install the SDK
pip install -e .

# Verify installation
midnight --version
```

## Initial Setup

```bash
# Initialize configuration
midnight config init

# View configuration
midnight config list

# Switch to preprod network
midnight config use preprod
```

## Wallet Management

```bash
# Create a new wallet
midnight wallet new my-wallet

# Import existing wallet
midnight wallet import my-wallet --mnemonic "your twelve word mnemonic phrase here"

# List all wallets
midnight wallet list

# Show wallet address
midnight wallet address my-wallet

# Get testnet tokens from faucet
midnight wallet faucet my-wallet

# Check balance
midnight wallet balance <address>
```

## Contract Development

```bash
# Compile a contract
midnight contract compile contracts/hello_world.compact

# Deploy a contract
midnight contract deploy contracts/hello_world.compact --wallet my-wallet

# Call a contract circuit
midnight contract call <contract-address> storeMessage --args '{"message": "Hello"}' --wallet my-wallet

# Query contract state
midnight contract query <contract-address> getMessage

# List deployed contracts
midnight contract list

# Show contract info
midnight contract info <contract-address>
```

## Transaction Management

```bash
# Build unsigned transaction
midnight tx build --output unsigned.json

# Sign transaction
midnight tx sign unsigned.json --wallet my-wallet

# Submit transaction
midnight tx submit signed.json

# Check transaction status
midnight tx status <tx-hash>

# Watch transaction until finality
midnight tx watch <tx-hash>

# View transaction history
midnight tx history <address>
```

## AI Inference

```bash
# Train a model
midnight ai train data.csv --name my-model

# Run inference (no transaction)
midnight ai infer '[1, 2, 3]' --model my-model

# Run inference with ZK proof (creates transaction)
midnight ai infer '[1, 2, 3]' --model my-model --sign --wallet my-wallet

# List trained models
midnight ai model-list

# Show model details
midnight ai model-info my-model
```

## System Monitoring

```bash
# Quick health check
midnight status

# Detailed system status
midnight system status

# Show SDK info
midnight system info

# View service logs
midnight system logs node
midnight system logs indexer
midnight system logs prover
```

## Network Configuration

```bash
# Add custom network
midnight config add-network custom \
  --node-url https://custom-node.example.com \
  --indexer-url https://custom-indexer.example.com \
  --proof-server-url https://custom-prover.example.com \
  --network-id custom-net

# Switch networks
midnight config use local      # Local development
midnight config use preprod    # Pre-production
midnight config use testnet    # Testnet
midnight config use mainnet    # Mainnet

# Set config values
midnight config set default_wallet my-wallet
midnight config set profiles.local.node_url http://localhost:9944

# Get config values
midnight config get active_profile
midnight config get profiles.preprod.node_url
```

## Explorer Integration

```bash
# Open transaction in browser
midnight explorer open <tx-hash>

# View address in explorer
midnight explorer address <address>

# View block in explorer
midnight explorer block <block-number>
```

## Event Monitoring

```bash
# Listen to real-time events
midnight events listen --contract <address>

# Query historical events
midnight events query --contract <address> --from-block 100 --to-block 200
```

## Interactive Console

```bash
# Start interactive REPL with SDK preloaded
midnight console

# In the console, you have access to:
# - client: MidnightClient instance
# - wallet: Wallet utilities
# - contract: Contract utilities
# - All SDK modules
```

## Advanced Usage

### Offline Transaction Signing

```bash
# On online machine: build transaction
midnight tx build \
  --type contract_call \
  --contract <address> \
  --circuit myCircuit \
  --args '{"param": "value"}' \
  --output unsigned.json

# Transfer unsigned.json to offline machine

# On offline machine: sign transaction
midnight tx sign unsigned.json --wallet cold-wallet --output signed.json

# Transfer signed.json back to online machine

# On online machine: submit transaction
midnight tx submit signed.json
```

### Batch Operations

```bash
# Deploy multiple contracts
for contract in contracts/*.compact; do
  midnight contract deploy "$contract" --wallet my-wallet
done

# Check multiple transaction statuses
for hash in tx1 tx2 tx3; do
  midnight tx status "$hash"
done
```

### Using Different Profiles

```bash
# Use specific profile for a command
midnight --profile preprod contract deploy my_contract.compact

# Or set environment variable
export MIDNIGHT_PROFILE=preprod
midnight contract deploy my_contract.compact
```

### Custom Config File

```bash
# Use custom config file
midnight --config /path/to/custom-config.yaml config list

# Or set environment variable
export MIDNIGHT_CONFIG=/path/to/custom-config.yaml
midnight config list
```

## Output Formats

Most commands support different output formats:

```bash
# Table format (default)
midnight wallet list

# JSON format
midnight wallet list --output json

# YAML format
midnight wallet list --output yaml
```

## Verbose and Quiet Modes

```bash
# Verbose output (more details)
midnight --verbose contract deploy my_contract.compact

# Quiet mode (minimal output)
midnight --quiet contract deploy my_contract.compact
```

## Getting Help

```bash
# General help
midnight --help

# Command group help
midnight wallet --help
midnight contract --help
midnight tx --help

# Specific command help
midnight contract deploy --help
midnight wallet new --help
midnight tx status --help
```

## Common Workflows

### Development Workflow

```bash
# 1. Setup
midnight config init
midnight config use local
midnight wallet new dev-wallet

# 2. Develop and test
midnight contract compile contracts/my_contract.compact
midnight contract deploy contracts/my_contract.compact --wallet dev-wallet

# 3. Interact
midnight contract call <address> myCircuit --args '{"data": "test"}' --wallet dev-wallet
midnight contract query <address> getState
```

### Production Deployment

```bash
# 1. Switch to production network
midnight config use mainnet

# 2. Use production wallet
midnight wallet import prod-wallet --mnemonic "..."

# 3. Deploy
midnight contract deploy contracts/my_contract.compact --wallet prod-wallet

# 4. Verify
midnight contract info <address>
midnight explorer open <tx-hash>
```

### AI Model Deployment

```bash
# 1. Train model locally
midnight ai train training_data.csv --name my-model

# 2. Test inference
midnight ai infer '[1, 2, 3]' --model my-model

# 3. Deploy with ZK proof
midnight ai infer '[1, 2, 3]' --model my-model --sign --wallet my-wallet

# 4. Verify on-chain
midnight tx status <tx-hash>
```

## Troubleshooting

### Check Service Status

```bash
midnight status
midnight system status
```

### View Logs

```bash
midnight system logs node
midnight system logs indexer
midnight system logs prover
```

### Verify Configuration

```bash
midnight config list
midnight config get active_profile
```

### Test Network Connectivity

```bash
midnight node status
midnight node peers
```

## Tips and Best Practices

1. **Always initialize config first**: `midnight config init`
2. **Use named wallets**: Easier to manage than raw mnemonics
3. **Test on local/preprod first**: Before deploying to mainnet
4. **Use `--help` liberally**: Every command has detailed help
5. **Check status regularly**: `midnight status` for quick health check
6. **Use profiles**: Switch between networks easily
7. **Keep wallets secure**: Use `wallet export` carefully
8. **Monitor transactions**: Use `tx watch` for important transactions
9. **Use the console**: Great for experimentation and debugging
10. **Read the docs**: Check `docs/cli/` for detailed information

## Next Steps

- Read the [CLI Reference](docs/cli/CLI_REFERENCE.md) for complete command documentation
- Check [Examples](docs/cli/EXAMPLES.md) for practical use cases
- Review [Migration Guide](docs/cli/MIGRATION_GUIDE.md) if upgrading from legacy CLI
- Explore [Architecture](docs/cli/ARCHITECTURE.md) to understand the design

## Support

For issues or questions:
- Check the documentation in `docs/cli/`
- Run commands with `--help` flag
- Use `midnight --verbose` for detailed output
- Check service status with `midnight status`
