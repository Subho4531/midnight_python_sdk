# Transfer Commands - Quick Reference

Quick reference card for Midnight transfer commands.

## Token Model

| Token | Transferable | Use Case |
|-------|--------------|----------|
| **NIGHT** | ✅ Yes | Governance, staking, transfers |
| **DUST** | ❌ No | Transaction fees only (auto-generated) |

## Commands

### Unshielded Transfer (Public, Fast)

```bash
midnight transfer unshielded <RECIPIENT> <AMOUNT> [OPTIONS]
```

**Options:**
- `--wallet <name>` | `-w` - Wallet to use
- `--profile <name>` | `-p` - Network (local, preprod, testnet, mainnet)
- `--dry-run` - Test without sending

**Example:**
```bash
midnight transfer unshielded mn_addr_preprod1... 1000000
```

### Shielded Transfer (Private, Slower)

```bash
midnight transfer shielded <SHIELDED_ADDRESS> <AMOUNT> [OPTIONS]
```

**Options:**
- `--wallet <name>` | `-w` - Wallet to use
- `--profile <name>` | `-p` - Network
- `--dry-run` - Test without sending

**Example:**
```bash
midnight transfer shielded <shielded_addr> 1000000
```

**Note:** Requires Node.js 22+ and Midnight wallet SDK

### Transfer Info

```bash
midnight transfer info
```

Shows token model and transfer types information.

## Comparison

| Feature | Unshielded | Shielded |
|---------|------------|----------|
| **Privacy** | Public | Private |
| **Speed** | ~2 seconds | ~30 seconds |
| **Requirements** | Python SDK | Python SDK + Node.js + Wallet SDK |
| **Fees** | Lower (~100-1000 DUST) | Higher (~1000-10000 DUST) |
| **Use Case** | Public transfers | Privacy-sensitive transfers |

## Common Workflows

### Check Balance Before Transfer

```bash
midnight wallet balance
midnight transfer unshielded <recipient> <amount>
midnight tx status <tx_hash>
```

### Dry Run First

```bash
midnight transfer unshielded <recipient> <amount> --dry-run
midnight transfer unshielded <recipient> <amount>
```

### Transfer with Specific Wallet

```bash
midnight wallet list
midnight transfer unshielded <recipient> <amount> --wallet my-wallet
```

## Error Prevention

❌ **Cannot transfer DUST**
```bash
# This will fail
midnight transfer unshielded <recipient> 1000000 --token DUST
```

✅ **Transfer NIGHT instead**
```bash
midnight transfer unshielded <recipient> 1000000 --token NIGHT
```

## Quick Troubleshooting

| Error | Solution |
|-------|----------|
| "Insufficient balance" | Check balance: `midnight wallet balance` |
| "DUST cannot be transferred" | Use `--token NIGHT` (default) |
| "Invalid address format" | Ensure address starts with `mn_addr_` |
| "No wallet specified" | Use `--wallet` or set default wallet |
| "SDK required" (shielded) | Install Node.js 22+ and run `npm install` |

## Amount Units

Midnight uses smallest units (like satoshis in Bitcoin):

| Display | Smallest Units | Command |
|---------|----------------|---------|
| 1 NIGHT | 1,000,000 | `1000000` |
| 0.5 NIGHT | 500,000 | `500000` |
| 10 NIGHT | 10,000,000 | `10000000` |

## More Information

- Full Guide: [TRANSFER_GUIDE.md](./TRANSFER_GUIDE.md)
- CLI Reference: [COMPLETE_CLI_REFERENCE.md](./COMPLETE_CLI_REFERENCE.md)
- Wallet Commands: [README.md](./README.md)
