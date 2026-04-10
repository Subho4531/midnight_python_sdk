# Midnight SDK CLI Reference

Production-ready command-line interface for the Midnight blockchain.

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Initialize configuration
midnight config init

# Create a wallet
midnight wallet new my-wallet

# Check service status
midnight status

# Deploy a contract
midnight contract deploy contracts/hello_world.compact

# Check transaction status
midnight tx status <hash>
```

## Global Options

All commands support these global options:

- `-c, --config PATH` - Config file path (default: ~/.midnight/config.yaml)
- `-p, --profile NAME` - Profile to use (default: active profile)
- `-v, --verbose` - Verbose output
- `-q, --quiet` - Suppress output

## Command Groups

### wallet - Key Management

Manage wallets and keys securely.

```bash
# Generate new wallet
midnight wallet new my-wallet

# Import from mnemonic
midnight wallet import my-wallet --mnemonic "word1 word2 ..."

# List wallets
midnight wallet list

# Check balance
midnight wallet balance

# Show address
midnight wallet address my-wallet

# Export mnemonic (with warning)
midnight wallet export my-wallet
```

### config - Configuration

Manage network profiles and settings.

```bash
# Initialize config
midnight config init

# Set value
midnight config set active_profile preprod

# Get value
midnight config get active_profile

# List all config
midnight config list

# Switch profile
midnight config use preprod

# Add custom network
midnight config add-network custom \
  --node https://rpc.custom.network \
  --indexer https://indexer.custom.network/graphql \
  --indexer-ws wss://indexer.custom.network/graphql/ws \
  --proof https://proof.custom.network \
  --network-id custom
```

### contract - Contract Lifecycle

Full contract development workflow.

```bash
# Compile contract
midnight contract compile contracts/my_contract.compact

# Deploy contract
midnight contract deploy contracts/my_contract.compact

# Call circuit (mutating)
midnight contract call <address> <circuit> --args '{"key": "value"}'

# Query state (read-only)
midnight contract query <address> <method>

# Listen to events
midnight contract events <address> --follow

# List deployed contracts
midnight contract list

# Show contract info
midnight contract info <address>
```

### tx - Transaction Management

Submit, sign, and track transactions.

```bash
# Build unsigned transaction
midnight tx build --output unsigned.json

# Sign transaction offline
midnight tx sign unsigned.json --output signed.json

# Submit signed transaction
midnight tx submit signed.json

# Check status
midnight tx status <hash>

# Watch until finality
midnight tx watch <hash>

# List recent transactions
midnight tx list

# Decode transaction
midnight tx decode <hash>

# Transaction history
midnight tx history <address>
```

### proof - ZK Proofs

Generate and verify zero-knowledge proofs.

```bash
# Generate proof
midnight proof generate <circuit> '{"input": "value"}' --output proof.json

# Verify proof
midnight proof verify proof.json

# Show circuit info
midnight proof info <circuit>
```

### ai - AI Inference

Train and run AI models with ZK proofs.

```bash
# Train model
midnight ai train data.csv --name my-model

# Run inference (local)
midnight ai infer '[1, 2, 3]' --model my-model

# Run inference with transaction
midnight ai infer '[1, 2, 3]' --model my-model --sign

# List models
midnight ai model-list

# Show model info
midnight ai model-info my-model
```

### explorer - Explorer Integration

Open blockchain explorer in browser.

```bash
# Open explorer
midnight explorer open

# View transaction
midnight explorer open <tx_hash>

# View address
midnight explorer address <address>

# View block
midnight explorer block <number>
```

### system - System Health

Check service health and diagnostics.

```bash
# Check all services
midnight system status

# Show SDK info
midnight system info

# Tail service logs (Docker)
midnight system logs node --follow
midnight system logs indexer --lines 100
```

### node - Raw RPC

Direct node RPC interaction.

```bash
# Node sync status
midnight node status

# List peers
midnight node peers

# Raw JSON-RPC call
midnight node rpc <method> --params '[...]'
```

### events - Event Subscription

Subscribe to and query blockchain events.

```bash
# Listen to real-time events
midnight events listen --contract <address>

# Query historical events
midnight events query --contract <address> --from 1000 --to 2000
```

### console - Interactive REPL

Start interactive Python console with SDK preloaded.

```bash
# Start console
midnight console

# With specific profile
midnight console --profile preprod
```

## Configuration File

Default location: `~/.midnight/config.yaml`

```yaml
active_profile: local
default_wallet: my-wallet

profiles:
  local:
    name: local
    node_url: http://127.0.0.1:9944
    indexer_url: http://127.0.0.1:8088/api/v4/graphql
    indexer_ws_url: ws://127.0.0.1:8088/api/v4/graphql/ws
    proof_server_url: http://127.0.0.1:6300
    network_id: undeployed
    explorer_url: http://localhost:3000
  
  preprod:
    name: preprod
    node_url: https://rpc.preprod.midnight.network
    indexer_url: https://indexer.preprod.midnight.network/api/v4/graphql
    indexer_ws_url: wss://indexer.preprod.midnight.network/api/v4/graphql/ws
    proof_server_url: https://proof-server.preprod.midnight.network
    network_id: preprod
    explorer_url: https://explorer.preprod.midnight.network

wallets:
  my-wallet: /home/user/.midnight/wallets/my-wallet.txt
```

## Environment Variables

- `MIDNIGHT_CONFIG` - Config file path
- `MIDNIGHT_PROFILE` - Active profile
- `MNEMONIC` - Wallet mnemonic (for signing)

## Examples

### Deploy and Call Contract

```bash
# Create wallet
midnight wallet new deployer

# Deploy contract
midnight contract deploy contracts/counter.compact --wallet deployer

# Call increment circuit
midnight contract call <address> increment --wallet deployer

# Query state
midnight contract query <address> getCount
```

### Offline Transaction Signing

```bash
# Build unsigned transaction
midnight tx build --output unsigned.json

# Sign on air-gapped machine
midnight tx sign unsigned.json --wallet cold-wallet --output signed.json

# Submit from online machine
midnight tx submit signed.json
```

### AI Inference with ZK Proof

```bash
# Train model
midnight ai train training_data.csv --name fraud-detector

# Run inference with on-chain proof
midnight ai infer '[100, 50, 25]' --model fraud-detector --sign --wallet my-wallet
```

## Output Formats

Many commands support multiple output formats:

```bash
# Table (default)
midnight config list

# JSON
midnight config list --output json

# YAML
midnight config list --output yaml
```

## Troubleshooting

### Services Offline

```bash
# Check service status
midnight system status

# View logs
midnight system logs node
midnight system logs indexer
midnight system logs proof
```

### Wallet Issues

```bash
# List wallets
midnight wallet list

# Check balance
midnight wallet balance --profile preprod

# Export for debugging (careful!)
midnight wallet export my-wallet
```

### Transaction Failures

```bash
# Check transaction status
midnight tx status <hash>

# Decode transaction
midnight tx decode <hash>

# Watch for finality
midnight tx watch <hash> --timeout 120
```

## Migration from Legacy CLI

The CLI has been completely redesigned with organized command groups. See the migration guide for command mappings:

| Old Command | New Command |
|-------------|-------------|
| `midnight status` | `midnight system status` or `midnight status` |
| `midnight balance <addr>` | `midnight wallet balance` |
| `midnight deploy <contract>` | `midnight contract deploy <contract>` |
| `midnight call <addr> <fn>` | `midnight contract call <addr> <fn>` |
| `midnight tx get <hash>` | `midnight tx status <hash>` |
| `midnight tx list <addr>` | `midnight tx history <addr>` |

## Best Practices

1. **Use Profiles** - Configure profiles for different networks
2. **Secure Wallets** - Store mnemonics securely, use hardware wallets for production
3. **Offline Signing** - Use `tx build` and `tx sign` for cold wallet signing
4. **Monitor Services** - Regularly check `system status`
5. **Version Control** - Keep config files in version control (without secrets)

## Support

- Documentation: https://docs.midnight.network
- GitHub: https://github.com/midnight/python-sdk
- Discord: https://discord.gg/midnight
