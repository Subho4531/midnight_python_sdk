# Midnight Transfer Commands Guide

Complete guide to transferring tokens on the Midnight blockchain using the Python SDK CLI.

## Table of Contents

- [Understanding Midnight's Dual-Token Model](#understanding-midnights-dual-token-model)
- [Transfer Types](#transfer-types)
- [Command Reference](#command-reference)
- [Examples](#examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Understanding Midnight's Dual-Token Model

Midnight uses a unique dual-token system designed for privacy and functionality:

### NIGHT Token

**Properties:**
- Native token of Midnight
- **Transferable** between wallets
- Exists in two forms:
  - **Unshielded NIGHT**: Public, visible on-chain
  - **Shielded NIGHT**: Private, encrypted on-chain
- Used for governance and staking
- Generates DUST automatically when held

**Use Cases:**
- Governance voting
- Staking for network security
- Generating DUST for transaction fees
- Public transfers (unshielded)
- Private transfers (shielded)

### DUST Token

**Properties:**
- Resource token for transaction fees
- **Non-transferable** between wallets
- **Unshielded (public)** - queryable from indexer
- Generated automatically from NIGHT holdings
- Used exclusively for transaction fees

**Use Cases:**
- Paying transaction fees
- Executing smart contracts
- Private contract interactions

**Important:** DUST cannot be transferred between wallets. Any attempt to transfer DUST will result in an error.

---

## Transfer Types

### Unshielded Transfers

**Characteristics:**
- Public (amounts visible on-chain)
- Fast execution (~2 seconds)
- Lower computational requirements
- No ZK proof generation needed
- Suitable for non-sensitive transfers

**Command:**
```bash
midnight transfer unshielded <recipient> <amount> [OPTIONS]
```

**When to use:**
- Public transactions where privacy isn't required
- Fast transfers
- Lower fee requirements
- Testing and development

### Shielded Transfers

**Characteristics:**
- Private (amounts and sender encrypted)
- Slower execution (~30 seconds)
- Requires ZK proof generation
- Higher computational requirements
- Requires Midnight wallet SDK

**Command:**
```bash
midnight transfer shielded <recipient_shielded_address> <amount> [OPTIONS]
```

**When to use:**
- Privacy-sensitive transactions
- Confidential business transfers
- Personal financial privacy
- Compliance with privacy regulations

---

## Command Reference

### `midnight transfer unshielded`

Transfer unshielded (public) NIGHT tokens.

**Syntax:**
```bash
midnight transfer unshielded <RECIPIENT> <AMOUNT> [OPTIONS]
```

**Arguments:**
- `RECIPIENT` - Recipient address (format: `mn_addr_<network>1...`)
- `AMOUNT` - Amount in smallest units (e.g., 1000000 = 1 NIGHT with 6 decimals)

**Options:**
- `--token <type>` | `-t` - Token type (NIGHT only, default: NIGHT)
- `--wallet <name>` | `-w` - Wallet name (uses default if not specified)
- `--profile <name>` | `-p` - Network profile (local, preprod, testnet, mainnet)
- `--dry-run` - Simulate transfer without sending

**Examples:**

```bash
# Basic transfer
midnight transfer unshielded mn_addr_preprod1abc... 1000000

# With specific wallet
midnight transfer unshielded mn_addr_preprod1abc... 5000000 --wallet my-wallet

# Dry run (test without sending)
midnight transfer unshielded mn_addr_preprod1abc... 1000000 --dry-run

# On specific network
midnight transfer unshielded mn_addr_preprod1abc... 1000000 --profile preprod
```

### `midnight transfer shielded`

Transfer shielded (private) tokens.

**Syntax:**
```bash
midnight transfer shielded <RECIPIENT_SHIELDED_ADDRESS> <AMOUNT> [OPTIONS]
```

**Arguments:**
- `RECIPIENT_SHIELDED_ADDRESS` - Recipient's shielded address
- `AMOUNT` - Amount in smallest units

**Options:**
- `--token <type>` | `-t` - Token type (NIGHT or custom, default: NIGHT)
- `--wallet <name>` | `-w` - Wallet name (uses default if not specified)
- `--profile <name>` | `-p` - Network profile
- `--dry-run` - Simulate transfer without sending

**Requirements:**
- Node.js 22+ installed
- Midnight wallet SDK packages installed (`npm install`)
- Sufficient DUST for transaction fees

**Examples:**

```bash
# Basic shielded transfer
midnight transfer shielded <shielded_addr> 1000000

# With specific wallet
midnight transfer shielded <shielded_addr> 5000000 --wallet my-wallet

# Dry run
midnight transfer shielded <shielded_addr> 1000000 --dry-run

# On specific network
midnight transfer shielded <shielded_addr> 1000000 --profile preprod
```

### `midnight transfer info`

Display information about Midnight's token model and transfer types.

**Syntax:**
```bash
midnight transfer info
```

**Output:**
- NIGHT token properties
- DUST token properties
- Transfer types comparison
- Important notes
- Usage examples

---

## Examples

### Example 1: Simple Unshielded Transfer

Transfer 1 NIGHT (1,000,000 smallest units) to another wallet:

```bash
# Check your balance first
midnight wallet balance

# Get recipient address
RECIPIENT="mn_addr_preprod1x2w98jvk0wxppn3a3mlfw3ep736tdn7k2rhj7kjv292tcl6a0hyq3g5xa0"

# Transfer 1 NIGHT
midnight transfer unshielded $RECIPIENT 1000000

# Check transaction status
midnight tx status <tx_hash>
```

### Example 2: Transfer with Specific Wallet

Transfer using a specific wallet (not the default):

```bash
# List available wallets
midnight wallet list

# Transfer with specific wallet
midnight transfer unshielded mn_addr_preprod1... 5000000 --wallet trading-wallet

# Verify transaction
midnight tx watch <tx_hash>
```

### Example 3: Dry Run Before Transfer

Test a transfer without actually sending it:

```bash
# Dry run to check everything
midnight transfer unshielded mn_addr_preprod1... 1000000 --dry-run

# If successful, run for real
midnight transfer unshielded mn_addr_preprod1... 1000000
```

### Example 4: Shielded Transfer for Privacy

Transfer NIGHT privately using shielded transfer:

```bash
# Check balance
midnight wallet balance

# Shielded transfer (private)
midnight transfer shielded <shielded_addr> 1000000 --wallet my-wallet

# Note: This takes ~30 seconds for ZK proof generation
```

### Example 5: Cross-Network Transfer

Transfer on a specific network:

```bash
# Transfer on preprod testnet
midnight transfer unshielded mn_addr_preprod1... 1000000 --profile preprod

# Transfer on mainnet
midnight transfer unshielded mn_addr_mainnet1... 1000000 --profile mainnet
```

### Example 6: Batch Transfers

Transfer to multiple recipients:

```bash
# Create a script for batch transfers
cat > batch_transfer.sh << 'EOF'
#!/bin/bash
RECIPIENTS=(
  "mn_addr_preprod1abc..."
  "mn_addr_preprod1def..."
  "mn_addr_preprod1ghi..."
)

AMOUNT=1000000

for recipient in "${RECIPIENTS[@]}"; do
  echo "Transferring to $recipient..."
  midnight transfer unshielded "$recipient" "$AMOUNT" --wallet my-wallet
  sleep 2  # Wait between transfers
done
EOF

chmod +x batch_transfer.sh
./batch_transfer.sh
```

---

## Best Practices

### Before Transferring

1. **Check Balance**
   ```bash
   midnight wallet balance
   ```
   Ensure you have sufficient NIGHT and DUST

2. **Verify Recipient Address**
   - Double-check the recipient address
   - Ensure it matches the network (preprod, testnet, mainnet)
   - Use `--dry-run` to test first

3. **Estimate Fees**
   - Ensure sufficient DUST for transaction fees
   - Unshielded transfers: ~100-1000 DUST
   - Shielded transfers: ~1000-10000 DUST (higher due to ZK proofs)

### During Transfer

1. **Use Dry Run First**
   ```bash
   midnight transfer unshielded <recipient> <amount> --dry-run
   ```

2. **Monitor Transaction**
   ```bash
   midnight tx watch <tx_hash>
   ```

3. **Keep Transaction Hash**
   - Save the transaction hash for tracking
   - Use for support if issues arise

### After Transfer

1. **Verify Transaction Status**
   ```bash
   midnight tx status <tx_hash>
   ```

2. **Check Recipient Balance**
   ```bash
   midnight wallet balance <recipient_address>
   ```

3. **Keep Records**
   - Save transaction hashes
   - Document transfer amounts and recipients
   - Useful for accounting and auditing

### Security Best Practices

1. **Protect Your Mnemonic**
   - Never share your mnemonic phrase
   - Store securely offline
   - Use hardware wallets for large amounts

2. **Verify Addresses**
   - Always double-check recipient addresses
   - Transactions are irreversible
   - Use address book for frequent recipients

3. **Use Appropriate Transfer Type**
   - Unshielded for public, non-sensitive transfers
   - Shielded for privacy-sensitive transactions
   - Consider privacy requirements

4. **Test with Small Amounts**
   - Test with small amounts first
   - Verify recipient can receive
   - Then send larger amounts

---

## Troubleshooting

### Error: "Insufficient balance"

**Cause:** Not enough NIGHT tokens to transfer

**Solution:**
```bash
# Check balance
midnight wallet balance

# Fund wallet if needed
midnight wallet new my-wallet --airdrop --profile local
```

### Error: "DUST cannot be transferred"

**Cause:** Attempting to transfer DUST tokens

**Solution:**
- DUST is non-transferable by design
- Only NIGHT can be transferred
- DUST is generated automatically from NIGHT holdings

```bash
# Transfer NIGHT instead
midnight transfer unshielded <recipient> <amount> --token NIGHT
```

### Error: "Invalid recipient address format"

**Cause:** Recipient address doesn't match expected format

**Solution:**
- Ensure address starts with `mn_addr_`
- Verify network matches (preprod, testnet, mainnet)
- Check for typos

```bash
# Correct format
midnight transfer unshielded mn_addr_preprod1... 1000000
```

### Error: "No wallet specified"

**Cause:** No default wallet set and no wallet specified

**Solution:**
```bash
# Set default wallet
midnight config set default_wallet my-wallet

# Or specify wallet in command
midnight transfer unshielded <recipient> <amount> --wallet my-wallet
```

### Error: "Wallet file not found"

**Cause:** Wallet file doesn't exist

**Solution:**
```bash
# List wallets
midnight wallet list

# Create new wallet if needed
midnight wallet new my-wallet

# Or import existing wallet
midnight wallet import my-wallet --file mnemonic.txt
```

### Error: "Shielded transfers require the Midnight wallet SDK"

**Cause:** Node.js or wallet SDK not installed

**Solution:**
```bash
# Install Node.js 22+ from https://nodejs.org

# Install wallet SDK packages
npm install

# Verify installation
node --version  # Should be 22+
```

### Error: "Transaction submission failed"

**Cause:** Network issues or insufficient DUST for fees

**Solution:**
```bash
# Check network status
midnight system status

# Check DUST balance
midnight wallet balance

# Try again with smaller amount
midnight transfer unshielded <recipient> <smaller_amount>
```

### Shielded Transfer Timeout

**Cause:** ZK proof generation takes too long

**Solution:**
- Shielded transfers can take 30-60 seconds
- Ensure good network connection
- Wait for completion
- Check system resources (CPU, memory)

### Transaction Stuck in Pending

**Cause:** Network congestion or low fees

**Solution:**
```bash
# Check transaction status
midnight tx status <tx_hash>

# Watch for updates
midnight tx watch <tx_hash> --timeout 300

# Check network status
midnight system status
```

---

## Additional Resources

- [CLI Complete Reference](./COMPLETE_CLI_REFERENCE.md)
- [Wallet Commands Guide](./README.md)
- [Transaction Management](../../docs/TRANSACTION_MANAGEMENT.md)
- [Midnight Documentation](https://docs.midnight.network)

---

## FAQ

**Q: Can I transfer DUST tokens?**
A: No, DUST is non-transferable. It's generated automatically from NIGHT holdings and used only for transaction fees.

**Q: What's the difference between unshielded and shielded transfers?**
A: Unshielded transfers are public and fast. Shielded transfers are private (encrypted) but slower due to ZK proof generation.

**Q: How long do transfers take?**
A: Unshielded transfers: ~2 seconds. Shielded transfers: ~30 seconds (due to ZK proof generation).

**Q: Can I cancel a transfer?**
A: No, transactions are irreversible once submitted to the blockchain.

**Q: What are the transaction fees?**
A: Fees are paid in DUST. Unshielded: ~100-1000 DUST. Shielded: ~1000-10000 DUST.

**Q: Do I need Node.js for unshielded transfers?**
A: No, only shielded transfers require Node.js and the wallet SDK.

**Q: Can I transfer to any address?**
A: You can transfer to any valid Midnight address on the same network. Ensure the address format matches the network.

**Q: How do I get DUST for transaction fees?**
A: DUST is generated automatically from NIGHT holdings. Hold NIGHT tokens to generate DUST.

**Q: What if I don't have enough DUST?**
A: You need to hold more NIGHT tokens to generate DUST, or wait for DUST to accumulate from your existing NIGHT holdings.
