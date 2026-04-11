# Test Transfer with 1AM Wallet

Since the SDK is having issues with DUST synchronization, let's test the transfer using the 1AM wallet UI directly.

## Current Status

- **Balance**: 980 NIGHT (Unshielded) - decreased from 1000, so something happened!
- **DUST**: 0 DUST in SDK, but 110 tDUST in 1AM wallet
- **Coins**: 1 unshielded coin available, 0 DUST coins

## The Problem

The Wallet SDK shows 0 DUST coins even though you have 110 tDUST in 1AM. This causes the transfer to fail with:
```
Error: Cannot read properties of undefined (reading 'toString')
```

This error occurs because the SDK expects DUST coins to be available for fee calculation, but they're not synced.

## Why Balance Changed

Your balance went from 1000 → 980 NIGHT. This suggests:
1. A previous transfer attempt may have partially succeeded
2. Or fees were deducted
3. Or the wallet state is showing a different snapshot

## Recommended Approach

### Option 1: Use 1AM Wallet UI (Easiest)

1. Open 1AM wallet
2. Go to Send tab
3. Enter recipient address
4. Enter amount (e.g., 1 NIGHT)
5. Click Send
6. Confirm transaction

This will work because 1AM has proper DUST sync.

### Option 2: Wait for SDK DUST Sync

The SDK needs to sync DUST coins properly. This might require:
- Waiting longer (10+ minutes)
- Restarting the wallet
- Or a different sync strategy

### Option 3: Register NIGHT for DUST

Even though you have DUST in 1AM, the SDK might need explicit registration:

```bash
# Create a script to register NIGHT for DUST generation
node scripts/wallet/register_dust.mjs
```

## What We Learned

1. ✓ Wallet SDK can connect and sync
2. ✓ Balance queries work (shows 980 NIGHT)
3. ✓ Unshielded coins are available (1 coin)
4. ✗ DUST coins not syncing (0 coins despite 110 tDUST in 1AM)
5. ✗ Transfer fails due to missing DUST coin metadata

## Next Steps

For immediate testing:
1. **Use 1AM wallet UI** to complete the transfer
2. Verify transaction on explorer
3. Check if balance updates correctly

For SDK fix:
1. Investigate why DUST coins aren't syncing
2. Check if DUST needs explicit designation
3. Try longer sync times or different sync strategies
