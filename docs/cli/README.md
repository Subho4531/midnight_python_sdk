# Midnight SDK CLI Documentation

Production-ready command-line interface for the Midnight blockchain.

## Overview

The Midnight SDK CLI provides a comprehensive toolkit for interacting with the Midnight blockchain, featuring:

- **Organized Command Groups** - Logical grouping of related commands
- **Configuration Management** - Multi-network profile support
- **Wallet Management** - Secure key storage and management
- **Offline Signing** - Build and sign transactions offline
- **Transaction Builder** - Construct complex transactions programmatically
- **AI Integration** - Train and deploy AI models with ZK proofs
- **Event Subscription** - Real-time and historical event querying
- **Interactive Console** - REPL with SDK preloaded
- **Rich Output** - Tables, JSON, and YAML formatting
- **Comprehensive Help** - Built-in documentation for all commands

## Quick Start

```bash
# Install
pip install midnight-sdk

# Initialize
midnight config init

# Create wallet
midnight wallet new my-wallet

# Check status
midnight status

# Deploy contract
midnight contract deploy contracts/hello_world.compact
```

## Command Groups

### Core Commands

- **wallet** - Key management and balance queries
- **config** - Profile and network configuration
- **contract** - Contract compilation, deployment, and interaction
- **tx** - Transaction submission and management
- **proof** - ZK proof generation and verification

### Advanced Commands

- **ai** - AI model training and inference
- **explorer** - Blockchain explorer integration
- **system** - Service health and diagnostics
- **events** - Event subscription and querying
- **node** - Raw RPC interaction
- **console** - Interactive REPL

## Documentation

- [CLI Reference](./CLI_REFERENCE.md) - Complete command reference
- [Migration Guide](./MIGRATION_GUIDE.md) - Migrating from legacy CLI
- [Examples](./EXAMPLES.md) - Practical usage examples

## Architecture

```
midnight_sdk/
├── cli_new.py              # Main CLI entry point
├── cli/
│   └── commands/           # Command modules
│       ├── wallet.py       # Wallet commands
│       ├── config.py       # Config commands
│       ├── contract.py     # Contract commands
│       ├── tx.py           # Transaction commands
│       ├── proof.py        # Proof commands
│       ├── ai.py           # AI commands
│       ├── explorer.py     # Explorer commands
│       ├── system.py       # System commands
│       ├── node.py         # Node commands
│       ├── events.py       # Event commands
│       └── console.py      # Console command
├── config/
│   └── manager.py          # Configuration manager
└── builder/
    └── transaction_builder.py  # Transaction builder
```

## Configuration

Default config location: `~/.midnight/config.yaml`

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

## Features

### 1. Multi-Network Support

Easily switch between networks:

```bash
midnight config use local      # Local development
midnight config use preprod    # Pre-production
midnight config use mainnet    # Production
```

### 2. Secure Wallet Management

Store and manage wallets securely:

```bash
midnight wallet new deployer
midnight wallet import my-wallet --file mnemonic.txt
midnight wallet list
midnight wallet balance
```

### 3. Offline Transaction Signing

Build and sign transactions offline for enhanced security:

```bash
midnight tx build --output unsigned.json
midnight tx sign unsigned.json --wallet cold-wallet
midnight tx submit signed.json
```

### 4. Transaction Builder

Programmatically construct transactions:

```python
from midnight_sdk.builder import TransactionBuilder

builder = TransactionBuilder()
tx = (
    builder
    .call_contract("addr", "increment", {"value": 1})
    .set_nonce(10)
    .set_fee(50)
    .build()
)
```

### 5. AI Integration

Train and deploy AI models with ZK proofs:

```bash
midnight ai train data.csv --name my-model
midnight ai infer '[1, 2, 3]' --model my-model --sign
```

### 6. Event Monitoring

Subscribe to blockchain events:

```bash
midnight events listen --contract <address>
midnight events query --from 1000 --to 2000
```

### 7. Interactive Console

REPL with SDK preloaded:

```bash
midnight console

>>> client.status()
>>> client.indexer.get_latest_block()
```

### 8. Rich Output Formatting

Multiple output formats:

```bash
midnight config list                    # Table
midnight config list --output json      # JSON
midnight config list --output yaml      # YAML
```

## Global Options

All commands support:

- `-c, --config PATH` - Config file path
- `-p, --profile NAME` - Profile to use
- `-v, --verbose` - Verbose output
- `-q, --quiet` - Suppress output

## Environment Variables

- `MIDNIGHT_CONFIG` - Config file path
- `MIDNIGHT_PROFILE` - Active profile
- `MNEMONIC` - Wallet mnemonic for signing

## Testing

```bash
# Run tests
pytest tests/cli/

# Specific test file
pytest tests/cli/test_config.py

# With coverage
pytest --cov=midnight_sdk.cli tests/cli/
```

## Development

### Adding New Commands

1. Create command module in `midnight_sdk/cli/commands/`
2. Define typer app and commands
3. Import and register in `cli_new.py`

Example:

```python
# midnight_sdk/cli/commands/my_command.py
import typer
from rich.console import Console

app = typer.Typer(help="My command group")
console = Console()

@app.command()
def my_action():
    """Do something."""
    console.print("[green]Done![/green]")
```

```python
# midnight_sdk/cli_new.py
from .cli.commands import my_command

app.add_typer(my_command.app, name="my-command")
```

### Adding New Configuration Options

Update `midnight_sdk/config/manager.py`:

```python
class Config(BaseModel):
    active_profile: str = "local"
    profiles: dict[str, NetworkProfile] = {}
    wallets: dict[str, str] = {}
    my_new_option: str = "default"  # Add here
```

## Comparison with Other CLIs

### Solana CLI

```bash
# Solana
solana config set --url https://api.mainnet-beta.solana.com
solana balance <address>
solana program deploy program.so

# Midnight
midnight config use mainnet
midnight wallet balance
midnight contract deploy contract.compact
```

### Foundry (Ethereum)

```bash
# Foundry
forge build
forge create Contract --rpc-url <url>
cast call <address> "function()"

# Midnight
midnight contract compile contract.compact
midnight contract deploy contract.compact
midnight contract call <address> function
```

### Aptos CLI

```bash
# Aptos
aptos init
aptos account create
aptos move compile
aptos move publish

# Midnight
midnight config init
midnight wallet new my-wallet
midnight contract compile contract.compact
midnight contract deploy contract.compact
```

## Best Practices

1. **Use Profiles** - Configure profiles for different networks
2. **Secure Wallets** - Store mnemonics securely, use hardware wallets for production
3. **Offline Signing** - Use transaction builder for cold wallet signing
4. **Monitor Services** - Regularly check `system status`
5. **Version Control** - Keep config files in version control (without secrets)
6. **Test First** - Always test on local/preprod before mainnet
7. **Use Meaningful Names** - Name wallets and profiles descriptively
8. **Check Transactions** - Always verify transaction status after submission

## Troubleshooting

### Services Offline

```bash
midnight system status
midnight system logs node
```

### Wallet Issues

```bash
midnight wallet list
midnight wallet balance --profile preprod
```

### Transaction Failures

```bash
midnight tx status <hash>
midnight tx decode <hash>
midnight tx watch <hash>
```

### Configuration Problems

```bash
midnight config list
midnight config init --force
```

## Support

- **Documentation**: https://docs.midnight.network
- **GitHub**: https://github.com/midnight/python-sdk
- **Discord**: https://discord.gg/midnight
- **Issues**: https://github.com/midnight/python-sdk/issues

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Changelog

### v0.1.0 (2024)

- Initial production-ready CLI release
- Command groups: wallet, config, contract, tx, proof, ai, explorer, system, node, events, console
- Configuration management system
- Transaction builder
- Offline signing support
- Rich output formatting
- Interactive console
- Comprehensive documentation
