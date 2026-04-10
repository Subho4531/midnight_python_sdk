# Faucet Feature - Get Testnet Tokens

## Overview

Added a new `midnight wallet faucet` command to easily get testnet tokens from Midnight faucets.

## Usage

### Basic Usage

```bash
# Use default wallet
midnight wallet faucet

# Use specific wallet
midnight wallet faucet my-wallet

# Use specific network profile
midnight wallet faucet my-wallet --profile preprod

# Don't open browser automatically
midnight wallet faucet my-wallet --no-browser
```

### Complete Workflow

```bash
# 1. Create a wallet
midnight wallet new my-wallet

# 2. Switch to preprod network
midnight config use preprod

# 3. Get tokens from faucet
midnight wallet faucet my-wallet

# 4. Wait 2-3 minutes, then check balance
midnight wallet balance
```

## Features

### Automatic Network Detection

The command automatically detects which faucet to use based on your active network profile:

- **Preprod**: https://faucet.preprod.midnight.network/
- **Testnet**: https://faucet.testnet.midnight.network/
- **Local**: No faucet needed (pre-funded)
- **Mainnet**: No faucet available (real tokens required)

### Address Display

Shows your wallet address clearly formatted for easy copying:

```
═══ Midnight Faucet ═══

Network: preprod (preprod)
Wallet: my-wallet
Address: mn_addr_preprod1x2w98jvk0wxppn3a3mlfw3ep736tdn7k2rhj7kjv292tcl6a0hyq3g5xa0

Faucet URL: https://faucet.preprod.midnight.network/
```

### Clipboard Integration (Optional)

If you have `pyperclip` installed, the address is automatically copied to your clipboard:

```bash
# Install clipboard support
pip install pyperclip

# Now the address is auto-copied
midnight wallet faucet my-wallet
# ✓ Address copied to clipboard!
```

### Browser Integration

By default, the faucet URL opens in your browser automatically. Use `--no-browser` to disable this:

```bash
midnight wallet faucet my-wallet --no-browser
```

### Clear Instructions

The command provides step-by-step instructions:

```
Instructions:
  1. Copy your address above
  2. Visit the faucet URL
  3. Paste your address
  4. Request tokens (tNIGHT and tDUST)
  5. Wait 2-3 minutes for funding
  6. Check balance: midnight wallet balance
```

## Network Support

| Network | Faucet Available | URL |
|---------|------------------|-----|
| Local (undeployed) | ❌ No (pre-funded) | N/A |
| Preprod | ✅ Yes | https://faucet.preprod.midnight.network/ |
| Testnet | ✅ Yes | https://faucet.testnet.midnight.network/ |
| Mainnet | ❌ No (real tokens) | N/A |

## Examples

### Example 1: First-time Setup

```bash
# Initialize
midnight config init

# Create wallet
midnight wallet new dev-wallet

# Switch to preprod
midnight config use preprod

# Get tokens
midnight wallet faucet
# Opens browser to faucet
# Address is copied to clipboard

# Wait 2-3 minutes...

# Check balance
midnight wallet balance
```

### Example 2: Multiple Wallets

```bash
# Create multiple wallets
midnight wallet new wallet-1
midnight wallet new wallet-2
midnight wallet new wallet-3

# Fund each wallet
midnight wallet faucet wallet-1
midnight wallet faucet wallet-2
midnight wallet faucet wallet-3

# Check balances
midnight wallet balance --wallet wallet-1
midnight wallet balance --wallet wallet-2
midnight wallet balance --wallet wallet-3
```

### Example 3: Different Networks

```bash
# Fund on preprod
midnight config use preprod
midnight wallet faucet my-wallet

# Fund on testnet
midnight config use testnet
midnight wallet faucet my-wallet

# Each network has its own faucet
```

### Example 4: Scripted Workflow

```bash
# Create and fund wallet in one script
midnight wallet new auto-wallet
midnight config use preprod
midnight wallet faucet auto-wallet --no-browser

echo "Waiting for funding..."
sleep 180  # Wait 3 minutes

midnight wallet balance
```

## Error Handling

### No Faucet for Network

```bash
midnight config use mainnet
midnight wallet faucet

# Output:
# No faucet available for network: mainnet
# Mainnet requires real tokens - no faucet available
```

### No Wallet Specified

```bash
midnight wallet faucet

# Output:
# No wallet specified and no default set
```

### Wallet Not Found

```bash
midnight wallet faucet nonexistent-wallet

# Output:
# Wallet 'nonexistent-wallet' not found
```

## Tips

1. **Install pyperclip** for automatic clipboard copying:
   ```bash
   pip install pyperclip
   ```

2. **Use --no-browser** in scripts or CI/CD:
   ```bash
   midnight wallet faucet my-wallet --no-browser
   ```

3. **Wait 2-3 minutes** after requesting tokens before checking balance

4. **Check balance** to verify funding:
   ```bash
   midnight wallet balance
   ```

5. **Use different networks** for different purposes:
   - Preprod: Development and testing
   - Testnet: Pre-production testing
   - Local: Quick local development (no faucet needed)

## Integration with Other Commands

The faucet command integrates seamlessly with other wallet commands:

```bash
# Complete workflow
midnight wallet new my-wallet          # Create wallet
midnight wallet address my-wallet      # Show address
midnight wallet faucet my-wallet       # Get tokens
midnight wallet balance                # Check balance
midnight wallet list                   # List all wallets
```

## Troubleshooting

### Faucet Not Working

1. Check network status:
   ```bash
   midnight system status
   ```

2. Verify you're on the right network:
   ```bash
   midnight config list
   ```

3. Try the faucet URL manually in your browser

### Balance Not Showing

1. Wait 2-3 minutes after requesting tokens
2. Check transaction on explorer:
   ```bash
   midnight explorer address <your-address>
   ```

3. Verify network connectivity:
   ```bash
   midnight node status
   ```

## Command Reference

```
midnight wallet faucet [OPTIONS] [NAME]

Arguments:
  NAME  Wallet name (default: active wallet)

Options:
  -p, --profile TEXT    Network profile (default: active profile)
  --no-browser          Don't open browser automatically
  --help                Show help message
```

## Benefits

1. **Convenience**: One command to get testnet tokens
2. **Automation**: Can be scripted for CI/CD
3. **Clarity**: Clear instructions and error messages
4. **Integration**: Works with existing wallet and config commands
5. **Flexibility**: Supports multiple wallets and networks

## Next Steps

After getting tokens from the faucet:

1. **Deploy a contract**:
   ```bash
   midnight contract deploy my_contract.compact
   ```

2. **Call a contract**:
   ```bash
   midnight contract call <address> myCircuit --args '{}'
   ```

3. **Run AI inference**:
   ```bash
   midnight ai infer '[1,2,3]' --sign
   ```

4. **Transfer tokens**:
   ```bash
   midnight tx transfer <dest-address> 1000
   ```

## Summary

The `midnight wallet faucet` command makes it easy to get testnet tokens for development and testing. It automatically detects the right faucet, displays your address, opens the browser, and provides clear instructions - all in one command.

```bash
# That's it!
midnight wallet faucet
```
