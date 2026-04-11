# Midnight Transfer Scripts

Node.js scripts for performing token transfers on the Midnight blockchain.

## Scripts

### `transfer_unshielded.mjs`

Performs unshielded (public) NIGHT token transfers.

**Usage:**
```bash
MNEMONIC="word1 word2 ... word24" \
NETWORK_ID="undeployed" \
RECIPIENT="mn_addr_undeployed1..." \
AMOUNT="1000000" \
node transfer_unshielded.mjs
```

**Environment Variables:**
- `MNEMONIC` - Sender's 24-word mnemonic phrase (required)
- `NETWORK_ID` - Network ID: undeployed, preprod, testnet, mainnet (default: undeployed)
- `RECIPIENT` - Recipient's address starting with `mn_addr_` (required)
- `AMOUNT` - Amount in smallest units (required)

**Output:**
JSON object with transfer details:
```json
{
  "txHash": "0x...",
  "from": "mn_addr_undeployed1...",
  "to": "mn_addr_undeployed1...",
  "amount": 1000000,
  "network": "undeployed",
  "status": "submitted"
}
```

### `transfer_shielded.mjs`

Performs shielded (private) token transfers with ZK proofs.

**Usage:**
```bash
MNEMONIC="word1 word2 ... word24" \
NETWORK_ID="undeployed" \
RECIPIENT="<shielded_address>" \
AMOUNT="1000000" \
TOKEN="NIGHT" \
node transfer_shielded.mjs
```

**Environment Variables:**
- `MNEMONIC` - Sender's 24-word mnemonic phrase (required)
- `NETWORK_ID` - Network ID: undeployed, preprod, testnet, mainnet (default: undeployed)
- `RECIPIENT` - Recipient's shielded address (required)
- `AMOUNT` - Amount in smallest units (required)
- `TOKEN` - Token type: NIGHT or custom (default: NIGHT)

**Output:**
JSON object with transfer details:
```json
{
  "txHash": "0x...",
  "recipient": "<shielded_address>",
  "amount": "1000000",
  "token": "NIGHT",
  "network": "undeployed",
  "status": "submitted"
}
```

**Note:** Shielded transfers require:
- Wallet SDK packages installed (`npm install`)
- Proof server running
- Indexer accessible
- Takes 10-30 seconds for ZK proof generation

## Requirements

- Node.js 22+
- Midnight wallet SDK packages:
  - `@midnight-ntwrk/wallet-sdk-facade`
  - `@midnight-ntwrk/wallet-sdk-hd`
  - `@midnight-ntwrk/wallet-sdk-dust-wallet`
  - `@midnight-ntwrk/wallet-sdk-shielded`
  - `@midnight-ntwrk/wallet-sdk-unshielded-wallet`
  - `@midnight-ntwrk/midnight-js-network-id`
  - `@midnight-ntwrk/ledger-v8`

## Installation

```bash
# Install Node.js 22+ from https://nodejs.org

# Install wallet SDK packages
npm install

# Verify installation
node --version  # Should be 22+
```

## Network Configurations

### Undeployed (Local)
- Node: `http://127.0.0.1:9944`
- Indexer: `http://127.0.0.1:8088/api/v4/graphql`
- Proof Server: `http://127.0.0.1:6300`

### Preprod
- Node: `https://rpc.preprod.midnight.network`
- Indexer: `https://indexer.preprod.midnight.network/api/v4/graphql`
- Proof Server: `https://proof-server.preprod.midnight.network`

### Testnet
- Node: `https://rpc.testnet-02.midnight.network`
- Indexer: `https://indexer.testnet-02.midnight.network/api/v4/graphql`
- Proof Server: `https://proof-server.testnet-02.midnight.network`

## Examples

### Unshielded Transfer (Local Network)

```bash
# Set environment variables
export MNEMONIC="abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
export NETWORK_ID="undeployed"
export RECIPIENT="mn_addr_undeployed1x2w98jvk0wxppn3a3mlfw3ep736tdn7k2rhj7kjv292tcl6a0hyq3g5xa0"
export AMOUNT="1000000"

# Run transfer
node transfer_unshielded.mjs
```

### Shielded Transfer (Local Network)

```bash
# Set environment variables
export MNEMONIC="abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
export NETWORK_ID="undeployed"
export RECIPIENT="<shielded_address>"
export AMOUNT="1000000"
export TOKEN="NIGHT"

# Run transfer (takes 10-30 seconds)
node transfer_shielded.mjs
```

### Unshielded Transfer (Preprod)

```bash
export MNEMONIC="your real mnemonic here"
export NETWORK_ID="preprod"
export RECIPIENT="mn_addr_preprod1..."
export AMOUNT="1000000"

node transfer_unshielded.mjs
```

## Error Handling

Both scripts provide clear error messages:

- Missing environment variables
- Invalid amounts (must be positive)
- Insufficient balance
- Network connection issues
- Transaction submission failures

Errors are written to stderr, while the JSON result is written to stdout.

## Integration with Python CLI

These scripts are called by the Python CLI:

```bash
# Python CLI calls these scripts internally
midnight transfer unshielded mn_addr_preprod1... 1000000
midnight transfer shielded <shielded_addr> 1000000
```

The Python CLI:
1. Sets environment variables
2. Calls the appropriate Node.js script
3. Parses the JSON output
4. Displays results to the user

## Security Notes

- Never commit mnemonics to version control
- Store mnemonics securely (hardware wallets recommended)
- Use environment variables for sensitive data
- Verify recipient addresses before transferring
- Test with small amounts first

## Troubleshooting

### "MNEMONIC environment variable is required"
Set the MNEMONIC variable with your 24-word phrase.

### "Error: Invalid seed"
Check that your mnemonic is valid and properly formatted.

### "Cannot connect to node"
Ensure the network is running:
- Local: `docker-compose up -d`
- Remote: Check network status

### "Insufficient shielded balance"
You need to shield NIGHT tokens first before making shielded transfers.

### "Module not found"
Install wallet SDK packages: `npm install`

### Shielded transfer timeout
ZK proof generation can take 30+ seconds. Ensure:
- Good network connection
- Proof server is accessible
- Sufficient system resources

## Additional Resources

- [Midnight Documentation](https://docs.midnight.network)
- [Wallet SDK Documentation](https://docs.midnight.network/develop/wallet-sdk)
- [Python CLI Transfer Guide](../../docs/cli/TRANSFER_GUIDE.md)
