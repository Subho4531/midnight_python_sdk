#!/usr/bin/env node
/**
 * Query balance directly from indexer without wallet sync
 * Uses GraphQL subscriptions to get UTXO data
 */

import { HDWallet, Roles } from "@midnight-ntwrk/wallet-sdk-hd";
import { createKeystore } from "@midnight-ntwrk/wallet-sdk-unshielded-wallet";
import { setNetworkId } from "@midnight-ntwrk/midnight-js-network-id";
import { mnemonicToSeedSync } from "bip39";
import fetch from 'node-fetch';

const MNEMONIC = process.env.MNEMONIC;
const NETWORK_ID = process.env.NETWORK_ID || "preprod";
const INDEXER_URL = process.env.INDEXER_URL || "https://indexer.preprod.midnight.network/api/v4/graphql";

if (!MNEMONIC) {
  console.error(JSON.stringify({ error: "MNEMONIC environment variable is required" }));
  process.exit(1);
}

setNetworkId(NETWORK_ID);

// Derive keys from mnemonic
function deriveKeys(mnemonic) {
  const seed = mnemonicToSeedSync(mnemonic);
  const hdWallet = HDWallet.fromSeed(seed);
  
  if (hdWallet.type !== 'seedOk') {
    throw new Error('Invalid seed');
  }
  
  const result = hdWallet.hdWallet
    .selectAccount(0)
    .selectRoles([Roles.NightExternal])
    .deriveKeysAt(0);
  
  if (result.type !== 'keysDerived') {
    throw new Error('Key derivation failed');
  }
  
  hdWallet.hdWallet.clear();
  return result.keys;
}

async function queryBalance(address) {
  // Query unshielded transactions to calculate balance
  const query = `
    query GetTransactions($address: UnshieldedAddress!) {
      transactions(offset: { identifier: "0x00" }) {
        unshieldedCreatedOutputs {
          owner
          value
          tokenType
        }
        unshieldedSpentOutputs {
          owner
          value
          tokenType
        }
      }
    }
  `;
  
  try {
    const response = await fetch(INDEXER_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        variables: { address }
      })
    });
    
    const result = await response.json();
    
    if (result.errors) {
      throw new Error(`GraphQL errors: ${JSON.stringify(result.errors)}`);
    }
    
    // Calculate balance from UTXOs
    let nightBalance = 0n;
    let dustBalance = 0n;
    
    if (result.data && result.data.transactions) {
      for (const tx of result.data.transactions) {
        // Add created outputs
        for (const output of tx.unshieldedCreatedOutputs || []) {
          if (output.owner === address) {
            const value = BigInt(output.value);
            // Assuming tokenType 0x00 is NIGHT, 0x01 is DUST (adjust as needed)
            if (output.tokenType === "0x00" || output.tokenType === "00") {
              nightBalance += value;
            } else {
              dustBalance += value;
            }
          }
        }
        
        // Subtract spent outputs
        for (const output of tx.unshieldedSpentOutputs || []) {
          if (output.owner === address) {
            const value = BigInt(output.value);
            if (output.tokenType === "0x00" || output.tokenType === "00") {
              nightBalance -= value;
            } else {
              dustBalance -= value;
            }
          }
        }
      }
    }
    
    return {
      night: nightBalance.toString(),
      dust: dustBalance.toString()
    };
    
  } catch (error) {
    throw new Error(`Indexer query failed: ${error.message}`);
  }
}

async function main() {
  try {
    const keys = deriveKeys(MNEMONIC);
    const unshieldedKeystore = createKeystore(keys[Roles.NightExternal], NETWORK_ID);
    const address = unshieldedKeystore.getBech32Address();
    
    const balance = await queryBalance(address);
    
    console.log(JSON.stringify({
      address,
      network: NETWORK_ID,
      balances: {
        night_unshielded: balance.night,
        dust: balance.dust,
        night_shielded: "0"  // Cannot query without wallet sync
      },
      note: "Shielded balance requires full wallet sync"
    }));
    
    process.exit(0);
  } catch (err) {
    console.error(JSON.stringify({
      error: err.message,
      stack: err.stack
    }));
    process.exit(1);
  }
}

main();
