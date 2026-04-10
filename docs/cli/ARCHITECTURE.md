# Midnight SDK CLI Architecture

## Overview

The Midnight SDK CLI is a production-ready command-line interface built with a modular architecture that separates concerns and provides extensibility.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     midnight CLI                             │
│                  (midnight_sdk/cli.py)                       │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Command    │    │    Config    │    │  Transaction │
│   Groups     │    │   Manager    │    │   Builder    │
│  (11 groups) │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │   Midnight SDK Core   │
                │  (client, wallet,     │
                │   indexer, proof)     │
                └───────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│     Node     │    │   Indexer    │    │    Proof     │
│   (RPC API)  │    │  (GraphQL)   │    │   Server     │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Module Structure

### 1. CLI Entry Point (`cli.py`)

The main entry point that:
- Registers all command groups
- Handles global options
- Provides version information
- Manages context passing

```python
app = typer.Typer(name="midnight", help="...")

# Register command groups
app.add_typer(wallet.app, name="wallet")
app.add_typer(config.app, name="config")
# ... 9 more groups

def cli_main():
    app()
```

### 2. Command Groups (`cli/commands/`)

Each command group is a separate module with its own typer app:

```
cli/commands/
├── wallet.py      # Key management
├── config.py      # Configuration
├── contract.py    # Contract operations
├── tx.py          # Transactions
├── proof.py       # ZK proofs
├── ai.py          # AI inference
├── explorer.py    # Browser integration
├── system.py      # Health checks
├── node.py        # Raw RPC
├── events.py      # Event subscription
└── console.py     # Interactive REPL
```

Each module follows this pattern:

```python
import typer
from rich.console import Console

app = typer.Typer(help="Command group description")
console = Console()

@app.command()
def command_name(
    arg: str = typer.Argument(..., help="..."),
    option: str = typer.Option(None, "--option", help="..."),
):
    """Command description."""
    # Implementation
```

### 3. Configuration System (`config/`)

Manages network profiles and settings:

```
config/
├── __init__.py
└── manager.py
    ├── ConfigManager      # Main config manager
    ├── NetworkProfile     # Network profile model
    └── Config             # Configuration data model
```

**Configuration Flow:**

```
User Command
    │
    ▼
ConfigManager.load()
    │
    ▼
~/.midnight/config.yaml
    │
    ▼
NetworkProfile (local/preprod/testnet/mainnet)
    │
    ▼
MidnightClient(network=profile.name)
```

### 4. Transaction Builder (`builder/`)

Constructs transactions for offline signing:

```
builder/
├── __init__.py
└── transaction_builder.py
    └── TransactionBuilder
        ├── call_contract()
        ├── deploy_contract()
        ├── transfer()
        ├── set_nonce()
        ├── set_fee()
        └── build()
```

**Transaction Flow:**

```
TransactionBuilder()
    │
    ▼
.call_contract(addr, circuit, args)
    │
    ▼
.set_nonce(10)
    │
    ▼
.set_fee(50)
    │
    ▼
.build() → unsigned_tx.json
    │
    ▼
WalletClient.sign_transaction()
    │
    ▼
signed_tx.json
    │
    ▼
WalletClient.submit_transaction()
```

### 5. Core SDK Integration

The CLI integrates with core SDK modules:

```
MidnightClient
├── wallet: WalletClient
│   ├── get_balance()
│   ├── sign_transaction()
│   └── submit_transaction()
├── indexer: IndexerClient
│   ├── get_transaction()
│   ├── get_contract_state()
│   └── query_events()
├── prover: ProofClient
│   ├── generate_proof()
│   └── verify_proof()
└── contracts: ContractClient
    ├── deploy()
    └── call()
```

## Data Flow

### Contract Deployment Flow

```
User: midnight contract deploy contract.compact --wallet my-wallet
    │
    ▼
contract.py: contract_deploy()
    │
    ├─→ ConfigManager.load() → Get active profile
    │
    ├─→ Load wallet mnemonic from ~/.midnight/wallets/
    │
    ▼
MidnightClient(network=profile.name)
    │
    ▼
client.contracts.deploy(contract_path, mnemonic)
    │
    ├─→ Compile contract (codegen)
    │
    ├─→ Generate proof (ProofClient)
    │
    ├─→ Sign transaction (WalletClient)
    │
    ├─→ Submit transaction (WalletClient)
    │
    ▼
Result: contract_address, tx_hash
    │
    ▼
Display to user with rich formatting
```

### Transaction Status Flow

```
User: midnight tx status <hash>
    │
    ▼
tx.py: tx_status()
    │
    ├─→ ConfigManager.get_profile()
    │
    ▼
MidnightClient(network=profile.name)
    │
    ▼
client.indexer.get_transaction_status(hash)
    │
    ├─→ GraphQL query to indexer
    │
    ▼
Result: {status, block_number, ...}
    │
    ▼
Display with rich table formatting
```

### Wallet Balance Flow

```
User: midnight wallet balance
    │
    ▼
wallet.py: wallet_balance()
    │
    ├─→ ConfigManager.load()
    │   ├─→ Get default wallet
    │   └─→ Get active profile
    │
    ├─→ Load mnemonic from wallet file
    │
    ▼
WalletClient.get_real_address(mnemonic, network_id)
    │
    ▼
WalletClient.get_balance(address, network_id)
    │
    ├─→ Query indexer for balance
    │
    ▼
Result: Balance(dust, night)
    │
    ▼
Display with rich table
```

## Command Execution Pipeline

```
1. User Input
   └─→ midnight contract deploy contract.compact --wallet my-wallet

2. Typer Parsing
   └─→ Parse command, arguments, options

3. Global Options Processing
   └─→ Load config file, set profile, verbose mode

4. Command Handler
   └─→ contract.py: contract_deploy()

5. Configuration Loading
   └─→ ConfigManager.load()
   └─→ Get profile and wallet

6. SDK Client Creation
   └─→ MidnightClient(network=profile.name)

7. Operation Execution
   └─→ client.contracts.deploy()

8. Result Formatting
   └─→ Rich console output (table/JSON/YAML)

9. Exit Code
   └─→ 0 (success) or 1 (error)
```

## Error Handling

```
Try:
    Command execution
Except MidnightSDKError:
    console.print("[red]Error: {message}[/red]")
    raise typer.Exit(1)
Except Exception:
    console.print("[red]Unexpected error: {message}[/red]")
    raise typer.Exit(1)
```

## Output Formatting

The CLI supports multiple output formats:

```python
def format_output(data, format: str):
    if format == "json":
        return json.dumps(data, indent=2)
    elif format == "yaml":
        return yaml.dump(data)
    else:  # table
        table = Table()
        # Build rich table
        return table
```

## Configuration Hierarchy

```
1. Command-line options (highest priority)
   └─→ --profile preprod

2. Environment variables
   └─→ MIDNIGHT_PROFILE=preprod

3. Config file
   └─→ ~/.midnight/config.yaml
       active_profile: preprod

4. Defaults (lowest priority)
   └─→ active_profile: local
```

## Extension Points

### Adding New Commands

1. Create new command module in `cli/commands/`
2. Define typer app and commands
3. Import and register in `cli.py`

```python
# cli/commands/my_command.py
import typer
app = typer.Typer(help="My commands")

@app.command()
def my_action():
    """Do something."""
    pass

# cli.py
from .cli.commands import my_command
app.add_typer(my_command.app, name="my-command")
```

### Adding New Configuration Options

1. Update `Config` model in `config/manager.py`
2. Add getter/setter methods if needed
3. Update default config creation

```python
class Config(BaseModel):
    active_profile: str = "local"
    my_new_option: str = "default"
```

### Adding New Output Formats

1. Add format option to command
2. Implement formatter function
3. Use in command handler

```python
@app.command()
def my_command(
    output: str = typer.Option("table", "--output", "-o")
):
    data = get_data()
    if output == "custom":
        print(custom_format(data))
```

## Testing Architecture

```
tests/cli/
├── test_config.py              # ConfigManager tests
├── test_transaction_builder.py # TransactionBuilder tests
└── test_cli_commands.py        # CLI command tests
```

Test pattern:

```python
from typer.testing import CliRunner
from midnight_sdk.cli import app

runner = CliRunner()

def test_command():
    result = runner.invoke(app, ["command", "arg"])
    assert result.exit_code == 0
    assert "expected" in result.stdout
```

## Security Considerations

1. **Wallet Storage**
   - Mnemonics stored with 0600 permissions
   - Located in `~/.midnight/wallets/`
   - Never logged or displayed without confirmation

2. **Configuration**
   - No secrets in config file
   - Wallet paths only, not mnemonics
   - Config file readable by user only

3. **Offline Signing**
   - Build unsigned transactions
   - Sign on air-gapped machine
   - Submit from online machine

4. **Input Validation**
   - All inputs validated
   - JSON parsing with error handling
   - Address format validation

## Performance Considerations

1. **Lazy Loading**
   - SDK clients created only when needed
   - Configuration loaded once per command

2. **Caching**
   - Configuration cached in memory
   - Network profiles cached

3. **Async Operations**
   - HTTP requests use httpx
   - WebSocket support for events

## Best Practices

1. **Command Design**
   - Clear, descriptive names
   - Consistent option naming
   - Comprehensive help text

2. **Error Messages**
   - User-friendly messages
   - Actionable suggestions
   - Colored output for visibility

3. **Output Formatting**
   - Default to human-readable tables
   - JSON/YAML for scripting
   - Consistent formatting across commands

4. **Documentation**
   - Every command has help text
   - Examples in documentation
   - Migration guides for changes

## Future Enhancements

1. **Shell Completion**
   - Bash/Zsh completion scripts
   - Auto-complete for addresses/contracts

2. **Plugin System**
   - Third-party command groups
   - Custom formatters

3. **Interactive Mode**
   - Wizard-style workflows
   - Guided contract deployment

4. **Advanced Features**
   - Transaction simulation
   - Gas estimation
   - Batch operations
   - Hardware wallet support
