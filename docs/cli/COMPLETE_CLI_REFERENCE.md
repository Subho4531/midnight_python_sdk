# Midnight CLI - Complete Reference

Complete command reference for the Midnight SDK CLI with all commands, options, examples, and developer guide.

## Table of Contents

- [Installation & Setup](#installation--setup)
- [Global Options](#global-options)
- [Wallet Commands](#wallet-commands)
- [Configuration Commands](#configuration-commands)
- [Contract Commands](#contract-commands)
- [Transaction Commands](#transaction-commands)
- [Transfer Commands](#transfer-commands)
- [Balance Commands](#balance-commands)
- [Proof Commands](#proof-commands)
- [AI Commands](#ai-commands)
- [Explorer Commands](#explorer-commands)
- [System Commands](#system-commands)
- [Node Commands](#node-commands)
- [Events Commands](#events-commands)
- [Console Commands](#console-commands)
- [Python SDK API](#python-sdk-api)
- [Getting Started Guide](#getting-started-guide)
- [Token Model](#token-model)
- [Network Profiles](#network-profiles)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Installation & Setup

### Prerequisites

- Python 3.11+
- Node.js 22+
- Docker & Docker Compose (for local development)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/midnight-python-sdk.git
cd midnight-python-sdk

# Install Python package
pip install -e .

# Install Node.js dependencies (for wallet operations)
npm install

# Verify installation
midnight --version
```

### Start Local Services

```bash
# Start Docker services
docker-compose up -d

# Check service status
midnight system status
```

### Initialize Configuration

```bash
# Create default configuration
midnight config init

# List available profiles
midnight config list
```

---

## Global Options

These options work with any command:

```bash
midnight [GLOBAL_OPTIONS] <command> [COMMAND_OPTIONS]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--version` | `-v` | Show version and exit |
| `--config <path>` | `-c` | Config file path (env: `MIDNIGHT_CONFIG`) |
| `--profile <name>` | `-p` | Profile to use (env: `MIDNIGHT_PROFILE`) |
| `--verbose` | | Verbose output |
| `--quiet` | `-q` | Suppress output |

### Examples

```bash
# Show version
midnight --version

# Use specific profile
midnight --profile preprod wallet list

# Verbose output
midnight --verbose contract deploy my_contract.compact

# Use custom config file
midnight --config ~/.midnight/custom.yaml config list
```

---

## Wallet Commands

Manage wallets, keys, and addresses.

### `midnight wallet new`

Generate a new wallet with mnemonic.

```bash
midnight wallet new <name> [OPTIONS]
```

**Options:**
- `--words <12|24>` - Mnemonic word count (default: 24)
- `--airdrop` - Fund wallet with testnet tokens
- `--profile <name>` - Network profile for airdrop

**Examples:**

```bash
# Create new 24-word wallet
midnight wallet new my-wallet

# Create 12-word wallet
midnight wallet new my-wallet --words 12

# Create and fund with testnet tokens
midnight wallet new my-wallet --airdrop --profile local

# Create with custom profile
midnight wallet new trading-wallet --profile preprod
```

### `midnight wallet import`

Import wallet from mnemonic or file.

```bash
midnight wallet import <name> [OPTIONS]
```

**Options:**
- `--mnemonic <phrase>` | `-m` - Mnemonic phrase
- `--file <path>` | `-f` - File containing mnemonic
- `--airdrop` - Fund wallet with testnet tokens
- `--profile <name>` - Network profile for airdrop

**Examples:**

```bash
# Import from mnemonic
midnight wallet import imported-wallet --mnemonic "word1 word2 ... word24"

# Import from file
midnight wallet import imported-wallet --file ~/mnemonic.txt

# Import and airdrop
midnight wallet import test-wallet --file ~/test.txt --airdrop --profile local

# Import with confirmation
midnight wallet import backup-wallet --file ~/backup.txt
```

### `midnight wallet list`

List all stored wallets.

```bash
midnight wallet list
```

**Output:**
Shows table with wallet names, paths, and default indicator.

**Examples:**

```bash
midnight wallet list
```

### `midnight wallet address`

Show address for named wallet.

```bash
midnight wallet address [name] [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile
- `--airdrop` - Fund wallet with testnet tokens

**Examples:**

```bash
# Show address for default wallet
midnight wallet address

# Show address for specific wallet
midnight wallet address my-wallet

# Show address and airdrop
midnight wallet address my-wallet --airdrop --profile local

# Show address on specific network
midnight wallet address trading-wallet --profile preprod
```

### `midnight wallet balance`

Show DUST balance for address (queries indexer).

```bash
midnight wallet balance [address] [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile

**Note:** NIGHT tokens are shielded and cannot be queried from the indexer without a viewing key. This is privacy by design.

**Examples:**

```bash
# Check default wallet balance
midnight wallet balance

# Check specific address
midnight wallet balance "mn_addr_undeployed1x2w98jvk0wxppn3a3mlfw3ep736tdn7k2rhj7kjv292tcl6a0hyq3g5xa0"

# Check balance on specific network
midnight wallet balance --profile preprod

# Check specific address on specific network
midnight wallet balance "mn_addr_preprod1..." --profile preprod
```

### `midnight wallet export`

Export wallet mnemonic (with warning).

```bash
midnight wallet export <name> [OPTIONS]
```

**Options:**
- `--private-key` - Show private key

**Examples:**

```bash
# Export mnemonic
midnight wallet export my-wallet

# Export with private key
midnight wallet export my-wallet --private-key
```

---

## Configuration Commands

Manage profiles and network configuration.

### `midnight config init`

Create default configuration.

```bash
midnight config init [OPTIONS]
```

**Options:**
- `--force` - Overwrite existing config

**Examples:**

```bash
# Initialize config
midnight config init

# Reinitialize (overwrite)
midnight config init --force
```

### `midnight config list`

Show all configuration.

```bash
midnight config list [OPTIONS]
```

**Options:**
- `--output <format>` | `-o` - Output format: `table`, `json`, `yaml` (default: table)

**Examples:**

```bash
# Show config as table
midnight config list

# Show config as JSON
midnight config list --output json

# Show config as YAML
midnight config list --output yaml
```

### `midnight config use`

Switch active profile.

```bash
midnight config use <profile>
```

**Examples:**

```bash
midnight config use preprod
midnight config use local
midnight config use mainnet
```

### `midnight config get`

Get configuration value.

```bash
    midnight config get <key>
```

**Key Format:** Dot notation (e.g., `profiles.preprod.node_url`)

**Examples:**

```bash
midnight config get active_profile
midnight config get default_wallet
midnight config get profiles.preprod.node_url
```

### `midnight config set`

Set configuration value.

```bash
midnight config set <key> <value>
```

**Examples:**

```bash
midnight config set default_wallet my-wallet
midnight config set active_profile preprod
```

### `midnight config add-network`

Add custom network profile.

```bash
midnight config add-network <name> [OPTIONS]
```

**Options:**
- `--node <url>` - Node RPC URL (required)
- `--indexer <url>` - Indexer GraphQL URL (required)
- `--indexer-ws <url>` - Indexer WebSocket URL (required)
- `--proof <url>` - Proof server URL (required)
- `--network-id <id>` - Network ID (required)
- `--explorer <url>` - Explorer URL

**Examples:**

```bash
# Add custom network
midnight config add-network custom \
  --node http://localhost:8080 \
  --indexer http://localhost:4000/graphql \
  --indexer-ws ws://localhost:4000/graphql \
  --proof http://localhost:8081 \
  --network-id custom-1 \
  --explorer http://localhost:3000

# Add network with minimal options
midnight config add-network staging \
  --node https://staging-node.midnight.network \
  --indexer https://staging-indexer.midnight.network/graphql \
  --indexer-ws wss://staging-indexer.midnight.network/graphql \
  --proof https://staging-proof.midnight.network \
  --network-id staging
```

---

## Contract Commands

Compile, deploy, and interact with contracts.

### `midnight contract compile`

Compile .compact contract.

```bash
midnight contract compile <path> [OPTIONS]
```

**Options:**
- `--output <dir>` | `-o` - Output directory

**Examples:**

```bash
# Compile contract
midnight contract compile contracts/counter.compact

# Compile with custom output
midnight contract compile contracts/counter.compact --output ./build

# Compile multiple contracts
midnight contract compile contracts/hello_world.compact
midnight contract compile contracts/bulletin_board.compact
```

### `midnight contract deploy`

Deploy contract to network.

```bash
midnight contract deploy <path> [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile
- `--wallet <name>` | `-w` - Wallet name

**Examples:**

```bash
# Deploy with default wallet
midnight contract deploy contracts/counter.compact

# Deploy to specific network
midnight contract deploy contracts/counter.compact --profile preprod

# Deploy with specific wallet
midnight contract deploy contracts/counter.compact --wallet trading-wallet

# Deploy with both options
midnight contract deploy contracts/counter.compact \
  --profile preprod \
  --wallet trading-wallet
```

### `midnight contract call`

Call contract circuit (mutating).

```bash
midnight contract call <address> <circuit> [OPTIONS]
```

**Options:**
- `--args <json>` - JSON arguments (default: `{}`)
- `--profile <name>` | `-p` - Network profile
- `--wallet <name>` | `-w` - Wallet name

**Examples:**

```bash
# Call circuit with no arguments
midnight contract call "0x1234..." increment

# Call with arguments
midnight contract call "0x1234..." transfer --args '{"to":"0x5678...","amount":100}'

# Call on specific network
midnight contract call "0x1234..." vote --profile preprod --args '{"choice":"yes"}'

# Call with specific wallet
midnight contract call "0x1234..." execute \
  --wallet trading-wallet \
  --args '{"data":"value"}'
```

### `midnight contract query`

Query contract state (read-only).

```bash
midnight contract query <address> <method> [OPTIONS]
```

**Options:**
- `--args <json>` - JSON arguments (default: `{}`)
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
# Query contract state
midnight contract query "0x1234..." getBalance

# Query with arguments
midnight contract query "0x1234..." getBalance --args '{"address":"0x5678..."}'

# Query on specific network
midnight contract query "0x1234..." getTotalSupply --profile preprod
```

### `midnight contract events`

Listen to contract events.

```bash
midnight contract events <address> [OPTIONS]
```

**Options:**
- `--follow` | `-f` - Follow new events
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
# Get historical events
midnight contract events "0x1234..."

# Follow new events
midnight contract events "0x1234..." --follow

# Follow events on specific network
midnight contract events "0x1234..." --follow --profile preprod
```

### `midnight contract list`

List locally deployed contracts.

```bash
midnight contract list [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
midnight contract list
midnight contract list --profile preprod
```

### `midnight contract info`

Show contract details.

```bash
midnight contract info <address> [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
midnight contract info "0x1234..."
midnight contract info "0x1234..." --profile preprod
```

---

## Transaction Commands

Submit, sign, and manage transactions.

### `midnight tx submit`

Submit signed transaction from file.

```bash
midnight tx submit <file> [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
# Submit transaction
midnight tx submit signed_tx.json

# Submit to specific network
midnight tx submit signed_tx.json --profile preprod
```

### `midnight tx sign`

Sign transaction offline.

```bash
midnight tx sign <file> [OPTIONS]
```

**Options:**
- `--output <path>` | `-o` - Output file
- `--wallet <name>` | `-w` - Wallet name

**Examples:**

```bash
# Sign transaction
midnight tx sign unsigned_tx.json

# Sign with specific wallet
midnight tx sign unsigned_tx.json --wallet trading-wallet

# Sign with custom output
midnight tx sign unsigned_tx.json --output my_signed_tx.json

# Sign with all options
midnight tx sign unsigned_tx.json \
  --wallet trading-wallet \
  --output signed_tx.json
```

### `midnight tx status`

Get transaction status.

```bash
midnight tx status <tx_hash> [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
midnight tx status "0xabcd1234..."
midnight tx status "0xabcd1234..." --profile preprod
```

### `midnight tx list`

List recent transactions.

```bash
midnight tx list [OPTIONS]
```

**Options:**
- `--limit <n>` | `-n` - Number of transactions (default: 10)
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
# List last 10 transactions
midnight tx list

# List last 50 transactions
midnight tx list --limit 50

# List on specific network
midnight tx list --limit 20 --profile preprod
```

### `midnight tx watch`

Watch transaction until finality.

```bash
midnight tx watch <tx_hash> [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile
- `--timeout <seconds>` - Timeout in seconds (default: 60)

**Examples:**

```bash
# Watch transaction
midnight tx watch "0xabcd1234..."

# Watch with custom timeout
midnight tx watch "0xabcd1234..." --timeout 120

# Watch on specific network
midnight tx watch "0xabcd1234..." --profile preprod --timeout 300
```

### `midnight tx decode`

Decode transaction payload.

```bash
midnight tx decode <tx_hash> [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
midnight tx decode "0xabcd1234..."
midnight tx decode "0xabcd1234..." --profile preprod
```

### `midnight tx history`

Transaction history for address.

```bash
midnight tx history <address> [OPTIONS]
```

**Options:**
- `--limit <n>` | `-n` - Number of transactions (default: 20)
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
# Get transaction history
midnight tx history "0x1234..."

# Get last 50 transactions
midnight tx history "0x1234..." --limit 50

# Get history on specific network
midnight tx history "0x1234..." --profile preprod --limit 100
```

### `midnight tx build`

Build unsigned transaction interactively.

```bash
midnight tx build [OPTIONS]
```

**Options:**
- `--output <path>` | `-o` - Output file (default: `unsigned_tx.json`)

**Examples:**

```bash
# Build transaction interactively
midnight tx build

# Build with custom output
midnight tx build --output my_tx.json
```

---

## Transfer Commands

Transfer NIGHT tokens between wallets (unshielded or shielded).

**Important:** Midnight uses a dual-token model:
- **NIGHT**: Transferable native token for governance, staking, and generating DUST
- **DUST**: Non-transferable resource for transaction fees (generated from NIGHT holdings)

### `midnight transfer unshielded`

Transfer unshielded (public) NIGHT tokens.

```bash
midnight transfer unshielded <recipient> <amount> [OPTIONS]
```

**Options:**
- `--token <type>` | `-t` - Token type (NIGHT only, default: NIGHT)
- `--wallet <name>` | `-w` - Wallet name
- `--profile <name>` | `-p` - Network profile
- `--dry-run` - Simulate without sending

**Examples:**

```bash
# Transfer 1,000,000 NIGHT
midnight transfer unshielded mn_addr_preprod1... 1000000

# Transfer with specific wallet
midnight transfer unshielded mn_addr_preprod1... 5000000 --wallet my-wallet

# Dry run (simulate)
midnight transfer unshielded mn_addr_preprod1... 1000000 --dry-run

# Transfer on specific network
midnight transfer unshielded mn_addr_preprod1... 1000000 --profile preprod
```

**Notes:**
- Unshielded transfers are public (amounts visible on-chain)
- Fast execution (~2 seconds)
- DUST cannot be transferred (it's non-transferable)
- Requires sufficient DUST for transaction fees

### `midnight transfer shielded`

Transfer shielded (private) tokens.

```bash
midnight transfer shielded <recipient_shielded_address> <amount> [OPTIONS]
```

**Options:**
- `--token <type>` | `-t` - Token type (NIGHT or custom, default: NIGHT)
- `--wallet <name>` | `-w` - Wallet name
- `--profile <name>` | `-p` - Network profile
- `--dry-run` - Simulate without sending

**Examples:**

```bash
# Transfer 1,000,000 shielded NIGHT
midnight transfer shielded <shielded_addr> 1000000

# Transfer with specific wallet
midnight transfer shielded <shielded_addr> 5000000 --wallet my-wallet

# Dry run (simulate)
midnight transfer shielded <shielded_addr> 1000000 --dry-run

# Transfer on specific network
midnight transfer shielded <shielded_addr> 1000000 --profile preprod
```

**Notes:**
- Shielded transfers are private (amounts and sender encrypted)
- Slower execution (~30 seconds for ZK proof generation)
- Requires Midnight wallet SDK (Node.js 22+)
- DUST cannot be transferred (it's non-transferable)
- Requires sufficient DUST for transaction fees

### `midnight transfer info`

Show information about Midnight's dual-token model.

```bash
midnight transfer info
```

**Examples:**

```bash
midnight transfer info
```

**Output:**
- NIGHT token properties and use cases
- DUST token properties and limitations
- Transfer types comparison
- Important notes about transferability
- Usage examples

---

## Balance Commands

Check wallet balances for DUST and NIGHT tokens.

### `midnight balance`

Check wallet balance with automatic network detection.

```bash
midnight balance [address] [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile
- `--full` - Use full wallet sync (slower but complete)

**Network Behavior:**
- **Local networks** (undeployed, local): Fast balance query from local node
- **Remote networks** (preprod, testnet, mainnet): Full wallet sync with indexer

**Examples:**

```bash
# Check default wallet balance
midnight balance

# Check specific address
midnight balance mn_addr_preprod1...

# Full balance with wallet sync (remote networks)
midnight balance --full

# Check balance on specific network
midnight balance --profile preprod

# Check local network balance (fast)
midnight balance --profile local
```

**Output:**
```
Wallet Balance
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Token                ┃              Amount ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ DUST                 │ 1000000.000000 DUST │
│ NIGHT (Unshielded)   │   4980.000000 NIGHT │
│ NIGHT (Shielded)     │      0.000000 NIGHT │
└──────────────────────┴─────────────────────┘
```

**Notes:**
- DUST is always visible (unshielded)
- Shielded NIGHT requires viewing key session
- Local networks show mock balances from airdrop
- Remote networks require wallet sync (up to 60 seconds)

---

## Proof Commands

Generate and verify ZK proofs.

### `midnight proof generate`

Generate ZK proof for circuit.

```bash
midnight proof generate <circuit> <inputs> [OPTIONS]
```

**Options:**
- `--output <path>` | `-o` - Output proof file
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
# Generate proof
midnight proof generate my_circuit '{"x":5,"y":10}'

# Generate and save to file
midnight proof generate my_circuit '{"x":5,"y":10}' --output proof.json

# Generate on specific network
midnight proof generate my_circuit '{"x":5,"y":10}' --profile preprod
```

### `midnight proof verify`

Verify ZK proof.

```bash
midnight proof verify <proof_file> [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
midnight proof verify proof.json
midnight proof verify proof.json --profile preprod
```

### `midnight proof info`

Show circuit information.

```bash
midnight proof info <circuit> [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
midnight proof info my_circuit
midnight proof info my_circuit --profile preprod
```

---

## AI Commands

Train and run AI inference.

### `midnight ai train`

Train AI model.

```bash
midnight ai train <data> [OPTIONS]
```

**Options:**
- `--name <name>` | `-n` - Model name (default: `model`)
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
# Train model from CSV
midnight ai train data.csv

# Train with custom name
midnight ai train data.csv --name my_model

# Train from JSON
midnight ai train data.json --name classifier

# Train on specific network
midnight ai train data.csv --name model --profile preprod
```

### `midnight ai infer`

Run AI inference.

```bash
midnight ai infer <features> [OPTIONS]
```

**Options:**
- `--model <name>` | `-m` - Model name (default: `model`)
- `--sign` - Submit as transaction
- `--wallet <name>` | `-w` - Wallet name
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
# Local inference
midnight ai infer '[1.0, 2.0, 3.0]'

# Inference with specific model
midnight ai infer '[1.0, 2.0, 3.0]' --model my_model

# Inference as transaction
midnight ai infer '[1.0, 2.0, 3.0]' --sign --wallet my-wallet

# Inference on specific network
midnight ai infer '[1.0, 2.0, 3.0]' --profile preprod
```

### `midnight ai model-list`

List trained models.

```bash
midnight ai model-list
```

**Examples:**

```bash
midnight ai model-list
```

### `midnight ai model-info`

Show model details.

```bash
midnight ai model-info <name>
```

**Examples:**

```bash
midnight ai model-info my_model
midnight ai model-info classifier
```

---

## Explorer Commands

Integrate with blockchain explorer.

### `midnight explorer open`

Open explorer in browser.

```bash
midnight explorer open [tx_hash] [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
# Open explorer home
midnight explorer open

# Open transaction
midnight explorer open "0xabcd1234..."

# Open on specific network
midnight explorer open "0xabcd1234..." --profile preprod
```

### `midnight explorer address`

View address in explorer.

```bash
midnight explorer address <address> [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
midnight explorer address "0x1234..."
midnight explorer address "0x1234..." --profile preprod
```

### `midnight explorer block`

View block in explorer.

```bash
midnight explorer block <number> [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
midnight explorer block 12345
midnight explorer block 12345 --profile preprod
```

---

## System Commands

Check service health and diagnostics.

### `midnight system status`

Check all service health.

```bash
midnight system status [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
midnight system status
midnight system status --profile preprod
```

### `midnight system info`

Show SDK and environment information.

```bash
midnight system info
```

**Examples:**

```bash
midnight system info
```

### `midnight system logs`

Tail service logs (for local Docker services).

```bash
midnight system logs [service] [OPTIONS]
```

**Services:** `node`, `indexer`, `proof`

**Options:**
- `--follow` | `-f` - Follow log output
- `--lines <n>` | `-n` - Number of lines (default: 50)

**Examples:**

```bash
# Show node logs
midnight system logs node

# Follow node logs
midnight system logs node --follow

# Show last 100 lines
midnight system logs node --lines 100

# Follow indexer logs
midnight system logs indexer --follow

# Show proof server logs
midnight system logs proof
```

---

## Node Commands

Raw node RPC interaction.

### `midnight node status`

Get node sync status.

```bash
midnight node status [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
midnight node status
midnight node status --profile preprod
```

### `midnight node peers`

List connected peers.

```bash
midnight node peers [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
midnight node peers
midnight node peers --profile preprod
```

### `midnight node rpc`

Call raw JSON-RPC method.

```bash
midnight node rpc <method> [OPTIONS]
```

**Options:**
- `--params <json>` - JSON params array (default: `[]`)
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
# Call RPC method
midnight node rpc getBlockNumber

# Call with parameters
midnight node rpc getBlock --params '[12345]'

# Call on specific network
midnight node rpc getBalance --params '["0x1234..."]' --profile preprod
```

---

## Events Commands

Subscribe to and query events.

### `midnight events listen`

Subscribe to real-time events.

```bash
midnight events listen [OPTIONS]
```

**Options:**
- `--contract <address>` | `-c` - Filter by contract
- `--type <type>` | `-t` - Filter by event type
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
# Listen to all events
midnight events listen

# Listen to specific contract
midnight events listen --contract "0x1234..."

# Listen to specific event type
midnight events listen --type Transfer

# Listen with filters
midnight events listen --contract "0x1234..." --type Transfer
```

### `midnight events query`

Query historical events.

```bash
midnight events query [OPTIONS]
```

**Options:**
- `--contract <address>` | `-c` - Filter by contract
- `--type <type>` | `-t` - Filter by event type
- `--from <block>` - Start block
- `--to <block>` - End block
- `--limit <n>` | `-n` - Max events (default: 100)
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
# Query all events
midnight events query

# Query specific contract
midnight events query --contract "0x1234..."

# Query specific event type
midnight events query --type Transfer

# Query with block range
midnight events query --from 1000 --to 2000

# Query with all filters
midnight events query \
  --contract "0x1234..." \
  --type Transfer \
  --from 1000 \
  --to 2000 \
  --limit 50
```

---

## Console Commands

Interactive REPL console.

### `midnight console`

Start interactive Python console with SDK preloaded.

```bash
midnight console [OPTIONS]
```

**Options:**
- `--profile <name>` | `-p` - Network profile

**Examples:**

```bash
# Start console
midnight console

# Start console with specific profile
midnight console --profile preprod
```

**Available in console:**
- `client` - MidnightClient instance
- `config_mgr` - ConfigManager instance

---

## Common Workflows

### Deploy and Call a Contract

```bash
# 1. Compile contract
midnight contract compile contracts/counter.compact

# 2. Deploy contract
midnight contract deploy contracts/counter.compact --wallet my-wallet

# 3. Call contract (increment counter)
midnight contract call "0x1234..." increment

# 4. Query contract state
midnight contract query "0x1234..." getCount

# 5. Check transaction status
midnight tx status "0xabcd1234..."
```

### Create Wallet and Check Balance

```bash
# 1. Create new wallet
midnight wallet new my-wallet --airdrop --profile local

# 2. Check balance
midnight wallet balance

# 3. Show address
midnight wallet address my-wallet

# 4. Export mnemonic (if needed)
midnight wallet export my-wallet
```

### Transfer NIGHT Tokens

```bash
# 1. Check sender balance
midnight wallet balance

# 2. Get recipient address
RECIPIENT="mn_addr_preprod1..."

# 3. Transfer unshielded NIGHT (public, fast)
midnight transfer unshielded $RECIPIENT 1000000 --wallet my-wallet

# 4. Check transaction status
midnight tx status "0xabcd1234..."

# 5. Verify recipient balance
midnight wallet balance $RECIPIENT

# Alternative: Shielded transfer (private, slower)
midnight transfer shielded <shielded_addr> 1000000 --wallet my-wallet
```

### Sign and Submit Transaction

```bash
# 1. Build transaction
midnight tx build --output unsigned_tx.json

# 2. Sign transaction
midnight tx sign unsigned_tx.json --wallet my-wallet

# 3. Submit transaction
midnight tx submit unsigned_tx.json.signed

# 4. Watch for finality
midnight tx watch "0xabcd1234..."
```

### Monitor System Health

```bash
# 1. Check service status
midnight system status

# 2. View system info
midnight system info

# 3. Check node status
midnight node status

# 4. View logs
midnight system logs node --follow
```

---

## Environment Variables

Configure CLI behavior with environment variables:

| Variable | Description |
|----------|-------------|
| `MIDNIGHT_CONFIG` | Path to config file |
| `MIDNIGHT_PROFILE` | Default profile to use |

**Examples:**

```bash
# Set default profile
export MIDNIGHT_PROFILE=preprod
midnight wallet list

# Use custom config
export MIDNIGHT_CONFIG=~/.midnight/custom.yaml
midnight config list

# Temporary override
MIDNIGHT_PROFILE=local midnight wallet balance
```

---

## Error Handling

Common errors and solutions:

| Error | Solution |
|-------|----------|
| `Config not found` | Run `midnight config init` |
| `No wallet specified` | Set default with `midnight config set default_wallet <name>` |
| `Connection refused` | Check service is running and profile is correct |
| `Invalid JSON` | Ensure JSON arguments are properly formatted |
| `Permission denied` | Check wallet file permissions (should be 0600) |

---

## Tips and Tricks

- Use `--profile` to switch networks without changing config
- Use `--verbose` for debugging
- Use `--quiet` to suppress output in scripts
- Use `midnight <command> --help` for command-specific help
- Use `midnight console` for interactive exploration
- Use `midnight tx watch` to wait for transaction finality
- Use `midnight system logs` to debug service issues

---

## Python SDK API

Complete Python API reference for programmatic access.

### Quick Start

```python
from midnight_sdk import MidnightClient
from midnight_sdk.wallet import WalletClient
from midnight_sdk.config import ConfigManager

# Initialize client
client = MidnightClient(network="preprod")

# Check service status
status = client.status()
print(status)  # {'node': True, 'indexer': True, 'prover': True}
```

### Configuration Management

```python
from midnight_sdk.config import ConfigManager

# Initialize
config_mgr = ConfigManager()
config_mgr.load()

# Get profile
profile = config_mgr.get_profile("preprod")
print(profile.node_url)          # wss://rpc.preprod.midnight.network
print(profile.indexer_url)       # https://indexer.preprod.midnight.network/api/v4/graphql
print(profile.network_id)        # preprod

# Set active profile
config_mgr.set("active_profile", "preprod")
config_mgr.save()
```

### Wallet Operations

#### Address Derivation

```python
from midnight_sdk.wallet import WalletClient

wallet = WalletClient()

# Derive all three address types
mnemonic = "your 24-word mnemonic phrase here"
addresses = wallet.get_all_addresses(mnemonic, "preprod")

print(addresses['addresses']['unshielded'])  # mn_addr_preprod1...
print(addresses['addresses']['shielded'])    # mn_shield-addr_preprod1...
print(addresses['addresses']['dust'])        # mn_dust_preprod1...
```

#### Balance Query

```python
# Get full balance (includes DUST, unshielded NIGHT, shielded NIGHT)
balance = wallet.get_full_balance(
    mnemonic=mnemonic,
    network_id="preprod",
    indexer_url="https://indexer.preprod.midnight.network/api/v4/graphql",
    indexer_ws_url="wss://indexer.preprod.midnight.network/api/v4/graphql/ws",
    node_url="wss://rpc.preprod.midnight.network",
    proof_url="https://lace-proof-pub.preprod.midnight.network"
)

# Access balances (in smallest units)
dust = int(balance['balances']['dust'])
night_unshielded = int(balance['balances']['night_unshielded'])
night_shielded = int(balance['balances']['night_shielded'])

# Convert to human-readable
print(f"DUST: {dust / 1_000_000:.6f}")
print(f"NIGHT (Unshielded): {night_unshielded / 1_000_000:.6f}")
print(f"NIGHT (Shielded): {night_shielded / 1_000_000:.6f}")
```

#### Private Key Derivation

```python
# Derive private keys from mnemonic
keys = wallet.get_private_keys(mnemonic)

print(keys['zswap'])          # Shielded operations key
print(keys['nightExternal'])  # Unshielded operations key
print(keys['dust'])           # DUST operations key
```

### Transfer Operations

```python
# Transfer unshielded NIGHT
result = wallet.transfer_unshielded(
    recipient="mn_addr_preprod1...",
    amount=1000000,  # 1 NIGHT in smallest units
    mnemonic=mnemonic,
    network_id="preprod"
)

print(result['tx_hash'])  # Transaction hash
print(result['status'])   # Transaction status
```

### Contract Operations

```python
# Deploy contract
contract = client.contracts.deploy(
    "contracts/my_contract.compact",
    private_key="your_private_key_here",
    sign_transaction=True
)

print(contract.address)      # Contract address
print(contract.circuit_ids)  # Available circuits

# Call circuit
result = contract.call(
    circuit_name="myCircuit",
    private_key="your_private_key_here",
    sign_transaction=True
)

print(result.tx_hash)   # Transaction hash
print(result.status)    # Transaction status

# Query state
state = contract.state()
print(state.block_height)  # Current block height
print(state.state)         # Contract state data
```

### AI Operations

```python
# Train model
client.ai.train_iris()

# Private inference
features = [5.1, 3.5, 1.4, 0.2]  # Iris setosa sample
result = client.ai.predict_private(features=features)

print(result.prediction)   # Predicted class
print(result.confidence)   # Confidence score (0-1)
print(result.model_hash)   # Model hash for verification
print(result.proof_hash)   # ZK proof hash
```

### Error Handling

```python
from midnight_sdk.exceptions import (
    WalletError,
    ContractCallError,
    ProofServerConnectionError,
    ModelNotTrainedError
)

try:
    balance = wallet.get_full_balance(mnemonic, "preprod")
except WalletError as e:
    print(f"Wallet error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Getting Started Guide

### Step 1: Create a Wallet

```bash
# Generate new wallet
midnight wallet new my-wallet

# Or import existing mnemonic
midnight wallet import my-wallet --mnemonic "word1 word2 ... word24"

# Show wallet address
midnight wallet address my-wallet
```

### Step 2: Fund Your Wallet

**Local Network:**
```bash
# Airdrop on local network
midnight wallet address my-wallet --airdrop --profile local
```

**Preprod Network:**
1. Visit https://faucet.preprod.midnight.network/
2. Paste your wallet address
3. Request tNIGHT tokens

### Step 3: Check Balance

```bash
# Check balance
midnight balance

# Full balance with sync
midnight balance --full
```

### Step 4: Deploy a Contract

```bash
# Deploy hello world contract
midnight contract deploy contracts/hello_world.compact

# Call contract circuit
midnight contract call <contract_address> storeMessage --args '{"newMessage": "Hello Midnight!"}'

# Query contract state
midnight contract query <contract_address> getMessage
```

### Step 5: Transfer Tokens

```bash
# Transfer 1 NIGHT (1,000,000 in smallest units)
midnight transfer unshielded <recipient_address> 1000000

# Check transaction status
midnight tx status <tx_hash>
```

---

## Token Model

Midnight uses a dual-token model with specific properties and use cases.

### NIGHT Token

**Properties:**
- **Transferable**: Yes
- **Forms**: Unshielded (public) and Shielded (private)
- **Visibility**: Unshielded amounts are public, shielded amounts are private
- **Units**: 1 NIGHT = 1,000,000 STAR (smallest unit)

**Use Cases:**
- Governance and voting
- Staking and delegation
- Peer-to-peer transfers
- Generating DUST for transaction fees
- Contract deployment and interaction

**Address Formats:**
- Unshielded: `mn_addr_preprod1...`
- Shielded: `mn_shield-addr_preprod1...`

### DUST Token

**Properties:**
- **Transferable**: No (non-transferable by design)
- **Visibility**: Always unshielded (public, queryable)
- **Generation**: Automatic from NIGHT holdings
- **Units**: 1 DUST = 1,000,000,000,000,000 SPECK (smallest unit)

**Use Cases:**
- Transaction fees
- Contract execution costs
- ZK proof generation fees
- Network resource consumption

**Address Format:**
- DUST: `mn_dust_preprod1...`

### Token Conversion

```bash
# NIGHT units
1 NIGHT = 1,000,000 STAR
5.5 NIGHT = 5,500,000 STAR

# DUST units  
1 DUST = 1,000,000,000,000,000 SPECK
0.000001 DUST = 1,000,000,000 SPECK
```

### Important Notes

1. **DUST cannot be transferred** - It's bound to the wallet that generated it
2. **DUST accumulates automatically** - From registered NIGHT UTXOs
3. **Shielded NIGHT is private** - Amounts and balances are encrypted
4. **Unshielded NIGHT is public** - Amounts visible on blockchain
5. **Both tokens required** - NIGHT for value, DUST for fees

---

## Network Profiles

### Available Networks

| Profile | Network ID | Environment | Use Case |
|---------|-----------|-------------|----------|
| `local` | undeployed | Local Docker | Development & testing |
| `preprod` | preprod | Testnet | Integration testing |
| `testnet` | testnet-02 | Alternative testnet | Alternative testing |
| `mainnet` | mainnet | Production | Live applications |

### Network Configuration

#### Local Network (undeployed)
```yaml
node_url: ws://localhost:9944
indexer_url: http://localhost:8088/api/v4/graphql
indexer_ws_url: ws://localhost:8088/api/v4/graphql/ws
proof_server_url: http://localhost:6300
explorer_url: http://localhost:8088
```

#### Preprod Network
```yaml
node_url: wss://rpc.preprod.midnight.network
indexer_url: https://indexer.preprod.midnight.network/api/v4/graphql
indexer_ws_url: wss://indexer.preprod.midnight.network/api/v4/graphql/ws
proof_server_url: https://lace-proof-pub.preprod.midnight.network
explorer_url: https://explorer.preprod.midnight.network
```

### Network Behavior Differences

#### Local Network
- **Fast operations** - No real blockchain sync
- **Mock balances** - Set via airdrop endpoint
- **Instant transfers** - Direct balance updates
- **No ZK proofs** - Simplified validation
- **Local explorer** - http://localhost:8088

#### Remote Networks (preprod, testnet, mainnet)
- **Full blockchain sync** - Real network consensus
- **Real balances** - From actual UTXOs
- **ZK proof transfers** - Complete cryptographic validation
- **Wallet SDK required** - For shielded operations
- **Public explorer** - Network-specific URLs

### Switching Networks

```bash
# Switch to preprod
midnight config use preprod

# Switch to local
midnight config use local

# Use specific network for one command
midnight balance --profile preprod

# Add custom network
midnight config add-network custom \
  --node wss://custom-node.example.com \
  --indexer https://custom-indexer.example.com/graphql \
  --indexer-ws wss://custom-indexer.example.com/graphql \
  --proof https://custom-proof.example.com \
  --network-id custom-1
```

---

## Error Handling

### Common CLI Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Config not found` | No configuration file | Run `midnight config init` |
| `No wallet specified` | No default wallet set | Run `midnight config set default_wallet <name>` |
| `Connection refused` | Service not running | Check `midnight system status` |
| `Invalid JSON` | Malformed JSON arguments | Validate JSON syntax |
| `Permission denied` | Wrong file permissions | Check wallet file permissions (0600) |
| `Insufficient balance` | Not enough tokens | Check balance and fund wallet |
| `Transaction timeout` | Network congestion | Wait and retry |
| `Proof generation failed` | Proof server issue | Check proof server status |

### Python SDK Exceptions

```python
from midnight_sdk.exceptions import (
    WalletError,           # Wallet operations failed
    ContractCallError,     # Contract call failed  
    ProofServerConnectionError,  # Proof server unavailable
    ModelNotTrainedError,  # AI model not trained
    ConnectionError        # Network connection failed
)

# Example error handling
try:
    client = MidnightClient(network="preprod")
    balance = client.wallet.get_full_balance(mnemonic, "preprod")
    
except WalletError as e:
    if "timeout" in str(e).lower():
        print("Wallet sync timed out. Please try again.")
    elif "connection" in str(e).lower():
        print("Cannot connect to network. Check internet connection.")
    else:
        print(f"Wallet error: {e}")
        
except ProofServerConnectionError:
    print("Proof server unavailable. Try again later.")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Network-Specific Issues

#### Local Network
- **Services not running**: `docker-compose up -d`
- **Port conflicts**: Check ports 9944, 8088, 6300
- **Data corruption**: `docker-compose down -v && docker-compose up -d`

#### Remote Networks
- **Slow wallet sync**: Normal, can take 60+ seconds
- **DUST sync issues**: Use 1AM wallet for transfers
- **Indexer lag**: Wait for network synchronization
- **Rate limiting**: Reduce request frequency

---

## Best Practices

### Security

```bash
# ✓ DO: Use secure wallet storage
mkdir -p ~/.midnight/wallets
chmod 700 ~/.midnight/wallets

# ✓ DO: Set proper file permissions
chmod 600 ~/.midnight/wallets/my-wallet.txt

# ✗ DON'T: Store mnemonics in code
# ✗ DON'T: Commit wallet files to git
# ✗ DON'T: Share private keys
```

### Performance

```bash
# ✓ DO: Use local network for development
midnight config use local

# ✓ DO: Cache addresses to avoid re-derivation
midnight wallet address my-wallet > address.txt

# ✓ DO: Use quick balance for fast queries
midnight balance  # Fast on local networks

# ✓ DO: Batch operations when possible
midnight contract call addr1 circuit1 && midnight contract call addr2 circuit2
```

### Development Workflow

```bash
# 1. Start with local development
midnight config use local
docker-compose up -d

# 2. Test on local network
midnight wallet new dev-wallet --airdrop
midnight contract deploy contracts/my_contract.compact

# 3. Test on preprod
midnight config use preprod
midnight wallet new preprod-wallet
# Fund via faucet
midnight contract deploy contracts/my_contract.compact

# 4. Deploy to mainnet (when ready)
midnight config use mainnet
midnight wallet new prod-wallet
# Fund with real tokens
midnight contract deploy contracts/my_contract.compact
```

### Code Organization

```python
# ✓ DO: Reuse client instances
client = MidnightClient(network="preprod")
# Use client for multiple operations

# ✓ DO: Handle errors gracefully
try:
    result = client.contracts.deploy(contract_path, private_key)
except ContractCallError as e:
    logger.error(f"Deployment failed: {e}")
    return None

# ✓ DO: Use configuration management
config = ConfigManager()
config.load()
profile = config.get_profile("preprod")

# ✓ DO: Clear sensitive data
mnemonic = get_mnemonic()
# ... use mnemonic ...
del mnemonic
```

---

## Troubleshooting

### Service Issues

```bash
# Check all services
midnight system status

# Check specific service
curl http://localhost:9944/health  # Node
curl http://localhost:8088/health  # Indexer  
curl http://localhost:6300/health  # Proof server

# Restart services
docker-compose restart

# Clean restart
docker-compose down -v
docker-compose up -d

# View logs
docker-compose logs node
docker-compose logs indexer
docker-compose logs proof-server
```

### Wallet Issues

```bash
# Wallet not found
midnight wallet list
midnight config set default_wallet <existing_wallet>

# Address derivation slow
# Normal - takes 2-3 seconds due to cryptographic operations

# Balance shows zero
midnight balance --full  # Force wallet sync
# Or check on explorer: https://explorer.preprod.midnight.network

# Private key issues
node get_private_key.mjs  # Verify key derivation works
```

### Transfer Issues

```bash
# Transfer hanging (local network)
# Fixed in latest version - should complete instantly

# Transfer failing (remote network)
midnight balance --full  # Check DUST balance
# Use 1AM wallet if DUST sync issues persist

# Transaction not found
midnight tx status <hash>  # Check transaction status
# Check explorer for confirmation
```

### Contract Issues

```bash
# Compilation failed
npm install -g @midnight-ntwrk/compact-compiler
compact --version

# Deployment failed
# Check balance for sufficient DUST
# Verify contract syntax
# Check proof server status

# Circuit call failed
# Verify circuit name and arguments
# Check contract state
midnight contract query <address> <method>
```

### Performance Issues

```bash
# Slow wallet sync
# Normal on first sync - can take 60+ seconds
# Use --profile local for development

# Slow proof generation
# Normal - ZK proofs take 10-30 seconds
# Use local network for faster development

# Connection timeouts
# Check network connectivity
# Verify service URLs in config
midnight config list
```

---

## Environment Variables

Configure CLI behavior with environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `MIDNIGHT_CONFIG` | Path to config file | `~/.midnight/custom.yaml` |
| `MIDNIGHT_PROFILE` | Default profile to use | `preprod` |
| `MIDNIGHT_WALLET` | Default wallet name | `my-wallet` |
| `NODE_URL` | Override node URL | `ws://localhost:9944` |
| `INDEXER_URL` | Override indexer URL | `http://localhost:8088/api/v4/graphql` |
| `PROOF_URL` | Override proof server URL | `http://localhost:6300` |

**Examples:**

```bash
# Set default profile
export MIDNIGHT_PROFILE=preprod
midnight wallet list

# Use custom config
export MIDNIGHT_CONFIG=~/.midnight/custom.yaml
midnight config list

# Temporary override
MIDNIGHT_PROFILE=local midnight balance

# Override service URLs
NODE_URL=ws://custom-node:9944 midnight system status
```

---

## Resources

### Documentation
- **Midnight Docs**: https://docs.midnight.network/
- **Wallet SDK Guide**: https://docs.midnight.network/sdks/official/wallet-developer-guide
- **Compact Language**: https://docs.midnight.network/develop/compact
- **ZK Proofs**: https://docs.midnight.network/learn/zk-proofs

### Tools
- **1AM Wallet**: https://1am.xyz - Official Midnight wallet
- **Midnight Explorer**: https://explorer.preprod.midnight.network - Block explorer
- **Faucet**: https://faucet.preprod.midnight.network - Get testnet tokens
- **Compact Playground**: https://playground.midnight.network - Test contracts online

### Support
- **GitHub Issues**: Report bugs and feature requests
- **Discord**: https://discord.gg/midnight - Community support
- **Forum**: https://forum.midnight.network - Technical discussions
- **Documentation**: https://docs.midnight.network - Official guides

### Examples Repository

Check the `examples/` directory for working code:
- `examples/complete_workflow.py` - End-to-end example
- `examples/ai_inference.py` - AI inference example
- `examples/bulletin_board.py` - Anonymous messaging
- `examples/private_vote.py` - Private voting
- `examples/real_demo.py` - Production-ready example

---

## Quick Reference Card

### Essential Commands

```bash
# Setup
midnight config init
midnight config use preprod

# Wallet
midnight wallet new my-wallet
midnight wallet address
midnight balance

# Contracts  
midnight contract deploy contracts/hello_world.compact
midnight contract call <addr> <circuit> --args '{}'
midnight contract query <addr> <method>

# Transfers
midnight transfer unshielded <recipient> <amount>
midnight tx status <hash>

# System
midnight system status
midnight --help
```

### Common Workflows

```bash
# 1. Local Development
midnight config use local
docker-compose up -d
midnight wallet new dev-wallet --airdrop
midnight contract deploy contracts/my_contract.compact

# 2. Preprod Testing  
midnight config use preprod
midnight wallet new test-wallet
# Fund via faucet
midnight balance --full
midnight contract deploy contracts/my_contract.compact

# 3. Production Deployment
midnight config use mainnet
midnight wallet new prod-wallet
# Fund with real tokens
midnight balance --full
midnight contract deploy contracts/my_contract.compact
```

### File Locations

```bash
~/.midnight/config.yaml           # Main configuration
~/.midnight/wallets/              # Wallet mnemonics
~/.midnight/models/               # AI models
./contracts/                      # Contract source files
./contracts/managed/              # Compiled contracts
./data/                          # Local blockchain data
```

---

**Last Updated**: 2026-04-11  
**CLI Version**: 0.1.0  
**Python**: 3.11+  
**Node.js**: 22+  

For the most up-to-date information, run `midnight --help` or visit https://docs.midnight.network/