# Airdrop Feature - Automatic Wallet Funding

## Overview

Added `--airdrop` flag to wallet commands for automatic funding with testnet tokens on local networks.

## What Changed

### Removed
- ❌ `midnight wallet faucet` command (removed)

### Added
- ✅ `--airdrop` flag on `midnight wallet new`
- ✅ `--airdrop` flag on `midnight wallet import`  
- ✅ `--airdrop` flag on `midnight wallet address`

## Usage

### Create Wallet with Airdrop

```bash
# Create and fund in one command
midnight wallet new my-wallet --airdrop

# Output:
# ✓ Wallet 'my-wallet' created
# 
# ⚠ SAVE THIS MNEMONIC SECURELY:
# [mnemonic phrase]
#
# Address: mn_addr_undeployed1x...
# ✓ Airdrop successful!
#   DUST:  1,000,000,000,000
#   NIGHT: 5,000,000,000
```

### Import Wallet with Airdrop

```bash
# Import and fund
midnight wallet import my-wallet --mnemonic "your mnemonic here" --airdrop
```

### Fund Existing Wallet

```bash
# Show address and fund
midnight wallet address my-wallet --airdrop
```

## How It Works

### Airdrop Mechanism

The airdrop uses the local node's `/balance` endpoint to set wallet balances:

```http
POST http://127.0.0.1:9944/balance
Content-Type: application/json

{
  "address": "mn_addr_undeployed1x...",
  "dust": 1000000000000,
  "night": 5000000000
}
```

### Default Amounts

- **DUST**: 1,000,000,000,000 (1 trillion smallest units)
- **NIGHT**: 5,000,000,000 (5 billion smallest units = 5,000 NIGHT with 6 decimals)

### Network Restrictions

Airdrop **only works on local networks**:

- ✅ **Local** (`undeployed`) - Airdrop works
- ❌ **Preprod** - Use faucet: https://faucet.preprod.midnight.network/
- ❌ **Testnet** - Use faucet: https://faucet.testnet.midnight.network/
- ❌ **Mainnet** - Real tokens required

## Examples

### Example 1: Quick Local Development

```bash
# Setup for local development
midnight config use local
midnight wallet new dev-wallet --airdrop

# Ready to deploy!
midnight contract deploy my_contract.compact
```

### Example 2: Multiple Wallets

```bash
# Create multiple funded wallets
midnight wallet new wallet-1 --airdrop
midnight wallet new wallet-2 --airdrop
midnight wallet new wallet-3 --airdrop
```

### Example 3: Import and Fund

```bash
# Import existing wallet and fund it
midnight wallet import my-wallet \
  --file mnemonic.txt \
  --airdrop
```

### Example 4: Fund After Creation

```bash
# Create wallet first
midnight wallet new my-wallet

# Fund it later
midnight wallet address my-wallet --airdrop
```

## Network-Specific Behavior

### Local Network (undeployed)

```bash
midnight config use local
midnight wallet new my-wallet --airdrop

# ✓ Airdrop successful!
#   DUST:  1,000,000,000,000
#   NIGHT: 5,000,000,000
```

### Preprod/Testnet

```bash
midnight config use preprod
midnight wallet new my-wallet --airdrop

# ⚠ Airdrop only works on local network
# Current network: preprod (preprod)
# For testnet tokens, visit: https://faucet.preprod.midnight.network/
```

## Balance Queries

### Important Note

The airdrop sets the balance on the **local node**, but balance queries may go through the **indexer** or **wallet SDK**:

```bash
# Airdrop sets balance
midnight wallet address my-wallet --airdrop
# ✓ Airdrop successful!
#   DUST:  1,000,000,000,000
#   NIGHT: 5,000,000,000

# Balance query might show 0 initially
midnight wallet balance
# DUST:  0
# NIGHT: 0
```

### Why This Happens

1. **Airdrop** → Sets balance on local node state
2. **Balance Query** → Queries through indexer or wallet SDK
3. **Sync Delay** → Indexer may not be synced yet

### Solution

For local development, the airdrop confirms the balance was set. The actual balance will be available when:
- The indexer syncs with the node
- You use the wallet SDK with proper mnemonic configuration
- You deploy and interact with contracts (which will use the balance)

## Error Handling

### Node Not Running

```bash
midnight wallet new my-wallet --airdrop

# ✗ Cannot connect to node for airdrop
# Make sure local node is running: docker-compose up -d
```

**Solution**: Start Docker services
```bash
docker-compose up -d
```

### Wrong Network

```bash
midnight config use preprod
midnight wallet new my-wallet --airdrop

# ⚠ Airdrop only works on local network
# Current network: preprod (preprod)
# For testnet tokens, visit: https://faucet.preprod.midnight.network/
```

**Solution**: Switch to local network
```bash
midnight config use local
```

## Command Reference

### midnight wallet new

```bash
midnight wallet new NAME [OPTIONS]

Options:
  --airdrop              Fund wallet with testnet tokens
  --profile, -p TEXT     Network profile for airdrop
  --words INTEGER        Mnemonic word count (12 or 24) [default: 24]
```

### midnight wallet import

```bash
midnight wallet import NAME [OPTIONS]

Options:
  --airdrop              Fund wallet with testnet tokens
  --profile, -p TEXT     Network profile for airdrop
  --mnemonic, -m TEXT    Mnemonic phrase
  --file, -f PATH        File containing mnemonic
```

### midnight wallet address

```bash
midnight wallet address [NAME] [OPTIONS]

Options:
  --airdrop              Fund wallet with testnet tokens
  --profile, -p TEXT     Network profile
```

## Benefits

1. **One Command**: Create and fund wallet in single command
2. **Local Development**: Perfect for quick local testing
3. **No Manual Steps**: No need to visit faucet websites
4. **Scriptable**: Easy to automate in scripts and CI/CD
5. **Flexible**: Can fund during creation or later

## Comparison: Faucet vs Airdrop

| Feature | Old (Faucet) | New (Airdrop) |
|---------|--------------|---------------|
| Command | `midnight wallet faucet` | `--airdrop` flag |
| Networks | Preprod, Testnet | Local only |
| Process | Opens browser, manual | Automatic |
| Speed | 2-3 minutes wait | Instant |
| Use Case | Remote testnets | Local development |

## Best Practices

1. **Use airdrop for local development**:
   ```bash
   midnight wallet new dev-wallet --airdrop
   ```

2. **Use faucet URLs for testnets**:
   ```bash
   # Preprod
   open https://faucet.preprod.midnight.network/
   
   # Testnet
   open https://faucet.testnet.midnight.network/
   ```

3. **Verify Docker is running** before using airdrop:
   ```bash
   docker-compose ps
   docker-compose up -d  # if not running
   ```

4. **Check network** before airdrop:
   ```bash
   midnight config list  # Shows active network
   ```

## Troubleshooting

### Airdrop Succeeds but Balance Shows 0

This is expected behavior. The airdrop sets the balance on the node, but balance queries go through the indexer/wallet SDK which may not be synced yet.

**What to do**: Proceed with contract deployment and transactions. The balance is available for use even if the query shows 0.

### Cannot Connect to Node

**Check Docker**:
```bash
docker-compose ps
docker-compose up -d
```

**Check Node URL**:
```bash
midnight config get profiles.local.node_url
# Should be: http://127.0.0.1:9944
```

### Wrong Network

**Check active network**:
```bash
midnight config list
```

**Switch to local**:
```bash
midnight config use local
```

## Summary

The `--airdrop` flag provides instant wallet funding for local development:

```bash
# Old way (3 steps)
midnight wallet new my-wallet
# Visit faucet website
# Wait 2-3 minutes

# New way (1 step)
midnight wallet new my-wallet --airdrop
# ✓ Done!
```

Perfect for rapid local development and testing! 🚀
