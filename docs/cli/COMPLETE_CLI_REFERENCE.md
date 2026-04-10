# Midnight CLI - Complete Reference

Complete command reference for the Midnight SDK CLI with all commands, options, and examples.

## Table of Contents

- [Global Options](#global-options)
- [Wallet Commands](#wallet-commands)
- [Configuration Commands](#configuration-commands)
- [Contract Commands](#contract-commands)
- [Transaction Commands](#transaction-commands)
- [Transfer Commands](#transfer-commands)
- [Proof Commands](#proof-commands)
- [AI Commands](#ai-commands)
- [Explorer Commands](#explorer-commands)
- [System Commands](#system-commands)
- [Node Commands](#node-commands)
- [Events Commands](#events-commands)
- [Console Commands](#console-commands)

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
