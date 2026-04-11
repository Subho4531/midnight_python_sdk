# Midnight Token Model - Clarification

This document clarifies the Midnight blockchain's dual-token model based on the actual implementation.

## Token Overview

| Token | Transferable | Visibility | Primary Use |
|-------|--------------|------------|-------------|
| **NIGHT** | ✅ Yes | Unshielded OR Shielded | Governance, staking, transfers |
| **DUST** | ❌ No | Unshielded (public) | Transaction fees only |

## NIGHT Token

NIGHT is Midnight's native token with dual forms:

### Unshielded NIGHT
- **Public**: Amounts visible on-chain
- **Queryable**: Can be queried from indexer
- **Fast transfers**: ~2 seconds
- **Use case**: Public transactions, governance

### Shielded NIGHT
- **Private**: Amounts encrypted on-chain
- **Requires viewing key**: Cannot be queried without viewing key
- **Slower transfers**: ~30 seconds (ZK proof generation)
- **Use case**: Privacy-sensitive transactions

### Key Properties
- ✅ Transferable between wallets
- ✅ Can be converted between unshielded and shielded forms
- ✅ Used for governance and staking
- ✅ Generates DUST automatically when held

## DUST Token

DUST is a resource token for transaction fees:

### Properties
- ❌ **Non-transferable**: Cannot be sent between wallets
- ✅ **Unshielded (public)**: Queryable from indexer
- ✅ **Auto-generated**: Created from NIGHT holdings
- ✅ **Fee payment**: Used exclusively for transaction fees

### Generation
DUST is generated automatically based on:
- Amount of NIGHT held
- Time held
- Network parameters

### Visibility
Unlike shielded NIGHT, DUST balances are:
- ✅ Public and visible on-chain
- ✅ Queryable from the indexer
- ✅ Shown in balance queries

## Balance Queries

When you query a wallet balance:

```bash
midnight wallet balance
```

You see:
- ✅ **DUST**: Full balance (unshielded, public)
- ✅ **NIGHT (unshielded)**: Public NIGHT balance
- ❌ **NIGHT (shielded)**: Requires viewing key (not shown)

Example output:
```
Balance for mn_addr_undeploy...
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Token             ┃                Amount ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ DUST              │     1,000,000,000,000 │
│ NIGHT (unshielded)│             5,000,000 │
└───────────────────┴───────────────────────┘

Note: This shows unshielded balances only.
For shielded NIGHT balance, use the Midnight wallet SDK with viewing keys.
```

## Transfer Capabilities

### What Can Be Transferred

✅ **NIGHT (Unshielded)**
```bash
midnight transfer unshielded mn_addr_preprod1... 1000000
```
- Public transfer
- Fast (~2 seconds)
- Amounts visible on-chain

✅ **NIGHT (Shielded)**
```bash
midnight transfer shielded <shielded_addr> 1000000
```
- Private transfer
- Slower (~30 seconds)
- Amounts encrypted on-chain
- Requires ZK proof generation

### What Cannot Be Transferred

❌ **DUST**
```bash
# This will fail with error
midnight transfer unshielded mn_addr_preprod1... 1000000 --token DUST
```
Error: "DUST cannot be transferred - it's non-transferable"

## Common Misconceptions

### ❌ Misconception 1: "DUST is shielded"
**Reality**: DUST is unshielded (public) and queryable from the indexer.

### ❌ Misconception 2: "NIGHT is always public"
**Reality**: NIGHT exists in both unshielded (public) and shielded (private) forms.

### ❌ Misconception 3: "You can transfer DUST"
**Reality**: DUST is non-transferable. It's generated automatically from NIGHT holdings.

### ❌ Misconception 4: "Shielded balances are hidden from everyone"
**Reality**: Shielded balances are encrypted but can be viewed with the appropriate viewing key.

## Privacy Model

### Public (Unshielded)
- DUST balances: Always public
- Unshielded NIGHT: Public by choice
- Transaction amounts: Visible on-chain
- Sender/recipient: Visible on-chain

### Private (Shielded)
- Shielded NIGHT: Private by choice
- Transaction amounts: Encrypted on-chain
- Sender: Encrypted on-chain
- Recipient: Encrypted on-chain
- Requires viewing key to see balances

## Use Cases

### When to Use Unshielded NIGHT
- Public transactions (no privacy needed)
- Fast transfers
- Governance voting
- Staking
- When transparency is desired

### When to Use Shielded NIGHT
- Privacy-sensitive transactions
- Confidential business transfers
- Personal financial privacy
- Compliance with privacy regulations
- When confidentiality is required

### DUST Usage
- Paying transaction fees (automatic)
- Contract execution fees (automatic)
- Cannot be manually transferred
- Generated automatically from NIGHT

## Technical Details

### Shielding/Unshielding
NIGHT can be converted between forms:
- **Shield**: Convert unshielded NIGHT → shielded NIGHT
- **Unshield**: Convert shielded NIGHT → unshielded NIGHT

### Viewing Keys
To see shielded NIGHT balances:
1. Generate viewing key from wallet
2. Establish session with indexer
3. Query shielded balance with session ID

### ZK Proofs
Shielded transfers use zero-knowledge proofs to:
- Prove transaction validity
- Hide transaction amounts
- Hide sender/recipient identities
- Maintain privacy while ensuring correctness

## CLI Commands Summary

### Check Balance
```bash
# Shows DUST and unshielded NIGHT
midnight wallet balance

# Shows for specific address
midnight wallet balance mn_addr_preprod1...
```

### Transfer Unshielded NIGHT
```bash
# Public transfer
midnight transfer unshielded <recipient> <amount>
```

### Transfer Shielded NIGHT
```bash
# Private transfer
midnight transfer shielded <shielded_recipient> <amount>
```

### View Token Info
```bash
# Display token model information
midnight transfer info
```

## FAQ

**Q: Is DUST shielded?**
A: No, DUST is unshielded (public) and queryable from the indexer.

**Q: Can I transfer DUST?**
A: No, DUST is non-transferable. It's generated automatically from NIGHT holdings.

**Q: Is NIGHT always public?**
A: No, NIGHT exists in both unshielded (public) and shielded (private) forms.

**Q: Why can't I see my shielded NIGHT balance?**
A: Shielded balances require a viewing key. Use the Midnight wallet SDK with your viewing key.

**Q: How do I get DUST?**
A: DUST is generated automatically when you hold NIGHT tokens.

**Q: Can I convert between unshielded and shielded NIGHT?**
A: Yes, through shielding and unshielding operations (requires wallet SDK).

**Q: Which is more private, DUST or NIGHT?**
A: NIGHT can be shielded for privacy. DUST is always public.

**Q: Do shielded transfers cost more?**
A: Yes, shielded transfers require more DUST due to ZK proof generation.

## References

- [Transfer Guide](./cli/TRANSFER_GUIDE.md)
- [CLI Reference](./cli/COMPLETE_CLI_REFERENCE.md)
- [Midnight Documentation](https://docs.midnight.network)
