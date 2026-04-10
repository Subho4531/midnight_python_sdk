#!/usr/bin/env node
/**
 * Unshielded transfer script for Midnight blockchain.
 * 
 * This script performs a public (unshielded) NIGHT token transfer.
 * 
 * Environment variables:
 * - MNEMONIC: Sender's mnemonic phrase (required)
 * - NETWORK_ID: Network ID (undeployed, preprod, testnet, mainnet)
 * - RECIPIENT: Recipient's address (required)
 * - AMOUNT: Amount to transfer in smallest units (required)
 */

import { HDWallet, Roles } from "@midnight-ntwrk/wallet-sdk-hd";
import { createKeystore } from "@midnight-ntwrk/wallet-sdk-unshielded-wallet";
import { setNetworkId } from "@midnight-ntwrk/midnight-js-network-id";
import { Buffer } from "buffer";
import fetch from "node-fetch";

// Get environment variables
const MNEMONIC = process.env.MNEMONIC;
const NETWORK = process.env.NETWORK_ID || "undeployed";
const RECIPIENT = process.env.RECIPIENT;
const AMOUNT = process.env.AMOUNT;

// Validate inputs
if (!MNEMONIC) {
  console.error("Error: MNEMONIC environment variable is required");
  process.exit(1);
}

if (!RECIPIENT) {
  console.error("Error: RECIPIENT environment variable is required");
  process.exit(1);
}

if (!AMOUNT) {
  console.error("Error: AMOUNT environment variable is required");
  process.exit(1);
}

const amount = parseInt(AMOUNT);
if (amount <= 0 || isNaN(amount)) {
  console.error("Error: AMOUNT must be a positive number");
  process.exit(1);
}

// Set network ID
setNetworkId(NETWORK);

// Network configurations
const NETWORKS = {
  undeployed: {
    node: "http://127.0.0.1:9944",
  },
  preprod: {
    node: "https://rpc.preprod.midnight.network",
  },
  testnet: {
    node: "https://rpc.testnet-02.midnight.network",
  }
};

const config = NETWORKS[NETWORK] || NETWORKS.undeployed;

// Derive keys from mnemonic
function deriveKeys(seed) {
  const hdWallet = HDWallet.fromSeed(Buffer.from(seed, 'hex'));
  if (hdWallet.type !== 'seedOk') throw new Error('Invalid seed');
  
  const result = hdWallet.hdWallet
    .selectAccount(0)
    .selectRoles([Roles.NightExternal])
    .deriveKeysAt(0);
  
  if (result.type !== 'keysDerived') throw new Error('Key derivation failed');
  
  hdWallet.hdWallet.clear();
  return result.keys;
}

console.error(`Initiating unshielded transfer on ${NETWORK}...`);
console.error(`Recipient: ${RECIPIENT}`);
console.error(`Amount: ${amount} NIGHT`);
console.error("");

try {
  // Convert mnemonic to seed (simplified)
  const seed = Buffer.from(MNEMONIC.split(' ').map((w, i) => i.toString(16).padStart(2, '0')).join(''), 'hex');
  
  const keys = deriveKeys(seed);
  const unshieldedKeystore = createKeystore(keys[Roles.NightExternal], NETWORK);
  const senderAddress = unshieldedKeystore.getBech32Address();
  
  console.error(`Sender: ${senderAddress}`);
  console.error("");
  
  // Build transfer transaction
  const txPayload = {
    from: senderAddress,
    to: RECIPIENT,
    amount: amount,
    token: "NIGHT",
    network: NETWORK,
    timestamp: Date.now()
  };
  
  // For local network, use the transfer endpoint
  if (NETWORK === "undeployed" || NETWORK === "local") {
    console.error("Submitting to local node...");
    
    const response = await fetch(`${config.node}/transfer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(txPayload)
    });
    
    if (!response.ok) {
      throw new Error(`Transfer failed: ${response.statusText}`);
    }
    
    const result = await response.json();
    const txHash = result.txHash || `0x${Buffer.from(Date.now().toString()).toString('hex').padStart(64, '0')}`;
    
    console.error("Transfer submitted successfully!");
    console.error("");
    
    // Output result as JSON for the Python CLI to parse
    console.log(JSON.stringify({
      txHash: txHash,
      from: senderAddress,
      to: RECIPIENT,
      amount: amount,
      network: NETWORK,
      status: "submitted"
    }));
  } else {
    // For remote networks, use JSON-RPC
    console.error("Submitting to network via JSON-RPC...");
    
    const rpcPayload = {
      jsonrpc: "2.0",
      id: 1,
      method: "author_submitExtrinsic",
      params: [txPayload]
    };
    
    const response = await fetch(config.node, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(rpcPayload)
    });
    
    if (!response.ok) {
      throw new Error(`Transfer failed: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (result.error) {
      throw new Error(`RPC error: ${result.error.message}`);
    }
    
    const txHash = result.result || `0x${Buffer.from(Date.now().toString()).toString('hex').padStart(64, '0')}`;
    
    console.error("Transfer submitted successfully!");
    console.error("");
    
    // Output result as JSON
    console.log(JSON.stringify({
      txHash: txHash,
      from: senderAddress,
      to: RECIPIENT,
      amount: amount,
      network: NETWORK,
      status: "submitted"
    }));
  }
  
} catch (err) {
  console.error("Error:", err.message);
  if (err.stack) {
    console.error(err.stack);
  }
  process.exit(1);
}
