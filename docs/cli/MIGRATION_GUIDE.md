# CLI Migration Guide

Guide for migrating from the legacy CLI to the new production-ready CLI.

## Overview

The new CLI provides:
- Organized command groups
- Configuration management
- Offline transaction signing
- Enhanced output formatting
- Better error handling
- Comprehensive help system

## Command Mapping

### Status Checks

**Legacy:**
```bash
midnight status
```

**New:**
```bash
midnight system status
# or quick check:
midnight status
```

### Balance Queries

**Legacy:**
```bash
midnight balance <address>
midnight balance <address> --network preprod
```

**New:**
```bash
midnight wallet balance
midnight wallet balance --profile preprod
midnight wallet balance <address> --profile preprod
```

### Contract Deployment

**Legacy:**
```bash
midnight deploy contracts/my_contract.compact --wallet <addr> --key <key>
```

**New:**
```bash
# First time: create wallet
midnight wallet new my-wallet

# Deploy
midnight contract deploy contracts/my_contract.compact --wallet my-wallet
```

### Contract Calls

**Legacy:**
```bash
midnight call <address> <circuit> --args '{"key": "value"}' --key <key>
```

**New:**
```bash
midnight contract call <address> <circuit> --args '{"key": "value"}' --wallet my-wallet
```

### Transaction Queries

**Legacy:**
```bash
midnight tx get <hash>
midnight tx list <address>
```

**New:**
```bash
midnight tx status <hash>
midnight tx history <address>
midnight tx list  # Recent transactions
```

### Block Information

**Legacy:**
```bash
midnight block
```

**New:**
```bash
midnight node status
# or use indexer:
midnight system status
```

## New Features

### 1. Configuration Profiles

Manage multiple networks easily:

```bash
# Initialize config
midnight config init

# Add custom network
midnight config add-network custom \
  --node https://rpc.custom.network \
  --indexer https://indexer.custom.network/graphql \
  --indexer-ws wss://indexer.custom.network/graphql/ws \
  --proof https://proof.custom.network \
  --network-id custom

# Switch networks
midnight config use preprod
midnight config use custom
```

### 2. Wallet Management

Secure wallet storage:

```bash
# Create wallet
midnight wallet new my-wallet

# Import existing
midnight wallet import my-wallet --mnemonic "word1 word2 ..."

# List wallets
midnight wallet list

# Check balance
midnight wallet balance

# Export (with warning)
midnight wallet export my-wallet
```

### 3. Offline Transaction Signing

Build and sign transactions offline:

```bash
# Build unsigned transaction
midnight tx build --output unsigned.json

# Sign on air-gapped machine
midnight tx sign unsigned.json --wallet cold-wallet --output signed.json

# Submit from online machine
midnight tx submit signed.json
```

### 4. Enhanced AI Commands

```bash
# Train model
midnight ai train data.csv --name my-model

# Inference without transaction
midnight ai infer '[1, 2, 3]' --model my-model

# Inference with on-chain proof
midnight ai infer '[1, 2, 3]' --model my-model --sign

# List models
midnight ai model-list
```

### 5. Event Subscription

```bash
# Listen to real-time events
midnight events listen --contract <address>

# Query historical events
midnight events query --contract <address> --from 1000 --to 2000
```

### 6. Interactive Console

```bash
# Start REPL with SDK preloaded
midnight console

# Available objects: client, config_mgr
>>> client.status()
>>> client.indexer.get_latest_block()
```

## Configuration File

The new CLI uses `~/.midnight/config.yaml`:

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

**Legacy:**
```bash
export MIDNIGHT_KEY=<private_key>
```

**New:**
```bash
# Use wallet names instead
midnight wallet new my-wallet

# Or set mnemonic for signing
export MNEMONIC="word1 word2 ..."

# Set active profile
export MIDNIGHT_PROFILE=preprod
```

## Migration Steps

### Step 1: Install New CLI

```bash
pip install --upgrade midnight-sdk
```

### Step 2: Initialize Configuration

```bash
midnight config init
```

### Step 3: Import Existing Wallets

If you have existing mnemonics:

```bash
midnight wallet import my-wallet --file mnemonic.txt
```

### Step 4: Test Commands

```bash
# Check status
midnight status

# List wallets
midnight wallet list

# Check balance
midnight wallet balance
```

### Step 5: Update Scripts

Update any automation scripts to use new commands:

**Before:**
```bash
#!/bin/bash
midnight deploy contracts/my_contract.compact --wallet $WALLET --key $KEY
midnight call $CONTRACT increment --key $KEY
```

**After:**
```bash
#!/bin/bash
midnight contract deploy contracts/my_contract.compact --wallet my-wallet
midnight contract call $CONTRACT increment --wallet my-wallet
```

## Backward Compatibility

The legacy CLI is still available:

```bash
# Use legacy commands
midnight-legacy status
midnight-legacy balance <address>
midnight-legacy deploy <contract>
```

## Breaking Changes

1. **Wallet Management**: Private keys are no longer passed via `--key`. Use wallet names instead.

2. **Network Selection**: `--network` flag replaced with `--profile` for consistency.

3. **Command Structure**: Commands are now organized into groups (wallet, contract, tx, etc.).

4. **Configuration**: New YAML-based configuration system replaces environment variables.

## Troubleshooting

### "Command not found"

Reinstall the package:
```bash
pip install --upgrade --force-reinstall midnight-sdk
```

### "Wallet not found"

Import your wallet:
```bash
midnight wallet import my-wallet --file mnemonic.txt
```

### "Profile not found"

Initialize config:
```bash
midnight config init
```

### Legacy commands still needed

Use the legacy CLI:
```bash
midnight-legacy <command>
```

## Getting Help

```bash
# General help
midnight --help

# Command group help
midnight wallet --help
midnight contract --help

# Specific command help
midnight contract deploy --help
```

## Support

- Documentation: https://docs.midnight.network
- GitHub Issues: https://github.com/midnight/python-sdk/issues
- Discord: https://discord.gg/midnight
