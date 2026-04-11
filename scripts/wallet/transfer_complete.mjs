#!/usr/bin/env node
/**
 * Complete unshielded transfer using Midnight Wallet SDK
 * 
 * This implements the full transfer flow:
 * 1. Initialize WalletFacade with all three wallets
 * 2. Create transfer transaction recipe
 * 3. Sign recipe with unshielded keystore
 * 4. Finalize recipe (generate ZK proofs)
 * 5. Submit transaction to network
 * 
 * Environment variables:
 * - MNEMONIC: Sender's mnemonic phrase (required)
 * - NETWORK_ID: Network ID (preprod, testnet, mainnet, undeployed)
 * - RECIPIENT: Recipient's unshielded address (required)
 * - AMOUNT: Amount to transfer in smallest units (required)
 * - INDEXER_URL: Indexer HTTP URL (optional)
 * - INDEXER_WS: Indexer WebSocket URL (optional)
 * - NODE_URL: Node WebSocket URL (optional)
 * - PROOF_URL: Proof server URL (optional)
 */

import { WalletFacade } from "@midnight-ntwrk/wallet-sdk-facade";
import { DustWallet } from "@midnight-ntwrk/wallet-sdk-dust-wallet";
import { HDWallet, Roles } from "@midnight-ntwrk/wallet-sdk-hd";
import { ShieldedWallet } from "@midnight-ntwrk/wallet-sdk-shielded";
import {
  createKeystore,
  InMemoryTransactionHistoryStorage,
  PublicKey,
  UnshieldedWallet,
} from "@midnight-ntwrk/wallet-sdk-unshielded-wallet";
import { setNetworkId } from "@midnight-ntwrk/midnight-js-network-id";
import * as ledger from "@midnight-ntwrk/ledger-v8";
import { mnemonicToSeedSync } from "bip39";
import * as Rx from "rxjs";

// Get environment variables
const MNEMONIC = process.env.MNEMONIC;
const NETWORK = process.env.NETWORK_ID || "preprod";
const RECIPIENT = process.env.RECIPIENT;
const AMOUNT = process.env.AMOUNT;
const INDEXER_URL = process.env.INDEXER_URL || "https://indexer.preprod.midnight.network/api/v4/graphql";
const INDEXER_WS = process.env.INDEXER_WS || "wss://indexer.preprod.midnight.network/api/v4/graphql/ws";
const NODE_URL = process.env.NODE_URL || "wss://rpc.preprod.midnight.network";
const PROOF_URL = process.env.PROOF_URL || "https://lace-proof-pub.preprod.midnight.network";

// Validate inputs
if (!MNEMONIC) {
  console.error(JSON.stringify({ error: "MNEMONIC environment variable is required" }));
  process.exit(1);
}

if (!RECIPIENT) {
  console.error(JSON.stringify({ error: "RECIPIENT environment variable is required" }));
  process.exit(1);
}

if (!AMOUNT) {
  console.error(JSON.stringify({ error: "AMOUNT environment variable is required" }));
  process.exit(1);
}

const amount = BigInt(AMOUNT);
if (amount <= 0n) {
  console.error(JSON.stringify({ error: "AMOUNT must be a positive number" }));
  process.exit(1);
}

setNetworkId(NETWORK);

// Derive keys from mnemonic using BIP39
function deriveKeys(mnemonic) {
  const seed = mnemonicToSeedSync(mnemonic);
  const hdWallet = HDWallet.fromSeed(seed);
  
  if (hdWallet.type !== 'seedOk') {
    throw new Error('Invalid seed');
  }
  
  const result = hdWallet.hdWallet
    .selectAccount(0)
    .selectRoles([Roles.Zswap, Roles.NightExternal, Roles.Dust])
    .deriveKeysAt(0);
  
  if (result.type !== 'keysDerived') {
    throw new Error('Key derivation failed');
  }
  
  hdWallet.hdWallet.clear();
  return result.keys;
}

async function transfer() {
  try {
    console.error(`Initiating unshielded transfer on ${NETWORK}...`);
    console.error(`Recipient: ${RECIPIENT}`);
    console.error(`Amount: ${amount} STAR (${Number(amount) / 1_000_000} NIGHT)`);
    console.error("");
    
    // Derive keys
    console.error("Deriving keys from mnemonic...");
    const keys = deriveKeys(MNEMONIC);
    const shieldedSecretKeys = ledger.ZswapSecretKeys.fromSeed(keys[Roles.Zswap]);
    const dustSecretKey = ledger.DustSecretKey.fromSeed(keys[Roles.Dust]);
    const unshieldedKeystore = createKeystore(keys[Roles.NightExternal], NETWORK);
    
    const unshieldedAddressObj = unshieldedKeystore.getBech32Address();
    const senderAddress = typeof unshieldedAddressObj === 'string' 
      ? unshieldedAddressObj 
      : unshieldedAddressObj.toString();
    
    console.error(`Sender: ${senderAddress}`);
    console.error("");
    
    // Configuration
    const configuration = {
      networkId: NETWORK,
      costParameters: {
        feeBlocksMargin: 5,
      },
      relayURL: new URL(NODE_URL),
      provingServerUrl: new URL(PROOF_URL),
      indexerClientConnection: {
        indexerHttpUrl: INDEXER_URL,
        indexerWsUrl: INDEXER_WS,
      },
      txHistoryStorage: new InMemoryTransactionHistoryStorage(),
    };
    
    // Initialize wallet
    console.error("Initializing wallet...");
    const wallet = await WalletFacade.init({
      configuration,
      shielded: (cfg) => ShieldedWallet(cfg).startWithSecretKeys(shieldedSecretKeys),
      unshielded: (cfg) => UnshieldedWallet(cfg).startWithPublicKey(PublicKey.fromKeyStore(unshieldedKeystore)),
      dust: (cfg) => DustWallet(cfg).startWithSecretKey(dustSecretKey, ledger.LedgerParameters.initialParameters().dust),
    });
    
    await wallet.start(shieldedSecretKeys, dustSecretKey);
    console.error("Wallet started");
    console.error("");
    
    // Wait for wallet to sync (with longer timeout for DUST)
    console.error("Syncing wallet... (up to 5 minutes for full sync including DUST)");
    let state;
    try {
      state = await Rx.firstValueFrom(
        wallet.state().pipe(
          Rx.filter(s => s.isSynced),
          Rx.timeout(300000), // 5 minutes
        )
      );
      console.error("Wallet fully synced!");
    } catch {
      console.error("Sync timeout - using current state");
      state = await Rx.firstValueFrom(wallet.state());
    }
    console.error("");
    
    // Check balances and coins
    const unshieldedBalance = state.unshielded.balances[ledger.unshieldedToken().raw] ?? 0n;
    const dustBalance = state.dust.balance(new Date());
    const unshieldedCoins = state.unshielded.availableCoins || [];
    const dustCoins = state.dust.availableCoins || [];
    
    console.error(`Current balance: ${Number(unshieldedBalance) / 1_000_000} NIGHT (Unshielded)`);
    console.error(`Current DUST: ${Number(dustBalance) / 1_000_000_000_000_000} DUST`);
    console.error(`Available unshielded coins: ${unshieldedCoins.length}`);
    console.error(`Available DUST coins: ${dustCoins.length}`);
    console.error("");
    
    // Check if we have enough balance
    if (unshieldedBalance < amount) {
      throw new Error(`Insufficient balance: have ${Number(unshieldedBalance) / 1_000_000} NIGHT, need ${Number(amount) / 1_000_000} NIGHT`);
    }
    
    // Check if we have coins available
    if (unshieldedCoins.length === 0) {
      throw new Error("No unshielded coins available. Wallet may not be fully synced.");
    }
    
    // Check if we have DUST for fees
    if (dustBalance === 0n) {
      console.error("WARNING: No DUST available for transaction fees");
      console.error("Attempting transfer anyway - SDK may handle fee balancing");
      console.error("");
    }
    
    // Create transfer transaction
    console.error("Creating transfer transaction...");
    const recipe = await wallet.transferTransaction(
      [
        {
          type: 'unshielded',
          outputs: [
            {
              amount: amount,
              receiverAddress: RECIPIENT,
              type: ledger.unshieldedToken().raw,
            },
          ],
        },
      ],
      {
        shieldedSecretKeys,
        dustSecretKey,
      },
      {
        ttl: new Date(Date.now() + 30 * 60 * 1000), // 30 minutes
      }
    );
    console.error("Transaction recipe created");
    console.error("");
    
    // Sign recipe
    console.error("Signing transaction...");
    const signedRecipe = await wallet.signRecipe(recipe, (payload) => 
      unshieldedKeystore.signData(payload)
    );
    console.error("Transaction signed");
    console.error("");
    
    // Finalize recipe (generate ZK proofs)
    console.error("Finalizing transaction (generating proofs)...");
    const finalizedTx = await wallet.finalizeRecipe(signedRecipe);
    console.error("Transaction finalized");
    console.error("");
    
    // Submit transaction
    console.error("Submitting transaction to network...");
    const txHash = await wallet.submitTransaction(finalizedTx);
    console.error("Transaction submitted!");
    console.error("");
    
    // Output result as JSON for Python CLI to parse
    console.log(JSON.stringify({
      txHash: txHash,
      from: senderAddress,
      to: RECIPIENT,
      amount: amount.toString(),
      network: NETWORK,
      status: "submitted"
    }));
    
    // Stop wallet
    await wallet.stop();
    process.exit(0);
    
  } catch (error) {
    console.error("Error:", error.message);
    if (error.stack) {
      console.error(error.stack);
    }
    console.error(JSON.stringify({ 
      error: error.message,
      stack: error.stack 
    }));
    process.exit(1);
  }
}

transfer();
