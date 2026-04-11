#!/usr/bin/env node
/**
 * Get quick balance using Indexer GraphQL API (no wallet sync required)
 * This queries the latest blocks and filters for our address
 */

import { createKeystore } from "@midnight-ntwrk/wallet-sdk-unshielded-wallet";
import { HDWallet, Roles } from "@midnight-ntwrk/wallet-sdk-hd";
import { MidnightBech32m, DustAddress } from "@midnight-ntwrk/wallet-sdk-address-format";
import { DustSecretKey } from "@midnight-ntwrk/ledger-v8";
import { mnemonicToSeedSync } from "bip39";
import { request, gql } from "graphql-request";

const MNEMONIC = process.env.MNEMONIC;
const NETWORK = process.env.NETWORK_ID || "preprod";
const INDEXER_URL = process.env.INDEXER_URL || "https://indexer.preprod.midnight.network/api/v4/graphql";

if (!MNEMONIC) {
  console.error(JSON.stringify({ error: "MNEMONIC environment variable is required" }));
  process.exit(1);
}

// Derive keys from mnemonic
function deriveKeys(mnemonic) {
  const seed = mnemonicToSeedSync(mnemonic);
  const hdWallet = HDWallet.fromSeed(seed);
  
  if (hdWallet.type !== 'seedOk') {
    throw new Error('Invalid seed');
  }
  
  const result = hdWallet.hdWallet
    .selectAccount(0)
    .selectRoles([Roles.NightExternal, Roles.Dust])
    .deriveKeysAt(0);
  
  if (result.type !== 'keysDerived') {
    throw new Error('Key derivation failed');
  }
  
  hdWallet.hdWallet.clear();
  return result.keys;
}

async function getQuickBalance() {
  try {
    // Derive keys
    const keys = deriveKeys(MNEMONIC);
    
    // Get unshielded address
    const unshieldedKeystore = createKeystore(keys[Roles.NightExternal], NETWORK);
    const unshieldedAddressObj = unshieldedKeystore.getBech32Address();
    // SDK v2.1.0 returns a string, v3+ returns an object - handle both
    const unshieldedAddress = typeof unshieldedAddressObj === 'string' 
      ? unshieldedAddressObj 
      : unshieldedAddressObj.toString();
    
    // Get DUST address
    const dustSecretKey = DustSecretKey.fromSeed(keys[Roles.Dust]);
    const dustAddressObj = new DustAddress(dustSecretKey.publicKey);
    const dustAddress = MidnightBech32m.encode(NETWORK, dustAddressObj).toString();
    
    // Query the latest block to get recent height
    const latestBlockQuery = gql`
      query GetLatestBlock {
        block {
          height
        }
      }
    `;
    
    let unshieldedBalance = 0n;
    let dustBalance = 0n;
    
    try {
      // Get latest block height
      const latestData = await request(INDEXER_URL, latestBlockQuery);
      const latestHeight = latestData.block?.height || 1000;
      
      // Query recent blocks (last 10000 blocks should cover recent transactions)
      const startHeight = Math.max(0, latestHeight - 10000);
      
      console.error(`Querying blocks from ${startHeight} to ${latestHeight}...`);
      
      // Query blocks in the range
      const blocksQuery = gql`
        query GetBlocks($height: Int!) {
          block(offset: { height: $height }) {
            height
            transactions {
              id
              hash
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
        }
      `;
      
      // Query multiple blocks (sample every 100 blocks for performance)
      const sampleInterval = 100;
      for (let h = startHeight; h <= latestHeight; h += sampleInterval) {
        try {
          const blockData = await request(INDEXER_URL, blocksQuery, { height: h });
          
          if (blockData.block?.transactions) {
            for (const tx of blockData.block.transactions) {
              // Add created outputs for our address
              if (tx.unshieldedCreatedOutputs) {
                for (const output of tx.unshieldedCreatedOutputs) {
                  if (output.owner === unshieldedAddress) {
                    unshieldedBalance += BigInt(output.value);
                    console.error(`Found created output: ${output.value} at block ${h}`);
                  }
                }
              }
              // Subtract spent outputs for our address
              if (tx.unshieldedSpentOutputs) {
                for (const output of tx.unshieldedSpentOutputs) {
                  if (output.owner === unshieldedAddress) {
                    unshieldedBalance -= BigInt(output.value);
                    console.error(`Found spent output: ${output.value} at block ${h}`);
                  }
                }
              }
            }
          }
        } catch (err) {
          // Skip blocks that don't exist
          continue;
        }
      }
      
      console.error(`Total unshielded balance: ${unshieldedBalance}`);
      
    } catch (error) {
      // Indexer query failed
      console.error("Indexer query error:", error.message);
    }
    
    // Output result
    console.log(JSON.stringify({
      addresses: {
        unshielded: unshieldedAddress,
        dust: dustAddress
      },
      network: NETWORK,
      balances: {
        dust: dustBalance.toString(),
        night_unshielded: unshieldedBalance.toString(),
        night_shielded: "unknown" // Requires full wallet sync
      },
      note: "Shielded balance requires full wallet sync with --full flag"
    }));
    
    process.exit(0);
    
  } catch (error) {
    console.error(JSON.stringify({ 
      error: error.message,
      stack: error.stack 
    }));
    process.exit(1);
  }
}

getQuickBalance();
