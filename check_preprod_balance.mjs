#!/usr/bin/env node
/**
 * Simple preprod balance checker using official Midnight SDK
 */

import { WalletFacade } from "@midnight-ntwrk/wallet-sdk-facade";
import { DustWallet } from "@midnight-ntwrk/wallet-sdk-dust-wallet";
import { HDWallet, Roles } from "@midnight-ntwrk/wallet-sdk-hd";
import { ShieldedWallet } from "@midnight-ntwrk/wallet-sdk-shielded";
import { createKeystore, InMemoryTransactionHistoryStorage, PublicKey, UnshieldedWallet } from "@midnight-ntwrk/wallet-sdk-unshielded-wallet";
import { setNetworkId } from "@midnight-ntwrk/midnight-js-network-id";
import * as ledger from "@midnight-ntwrk/ledger-v8";
import { mnemonicToSeedSync } from "bip39";
import { Buffer } from "buffer";

const MNEMONIC = "naive shadow firm problem eternal suit album absurd ski finish beauty aware husband hedgehog tuna guess achieve special assume skill grid gravity side income";
const NETWORK = "preprod";

setNetworkId(NETWORK);

const config = {
  indexer:     "https://indexer.preprod.midnight.network/api/v4/graphql",
  indexerWS:   "wss://indexer.preprod.midnight.network/api/v4/graphql/ws",
  proofServer: "https://proof-server.preprod.midnight.network",
  node:        "wss://rpc.preprod.midnight.network",
};

console.log('\n╔══════════════════════════════════════════════════════════════╗');
console.log('║        Preprod Balance Check - Official SDK                  ║');
console.log('╚══════════════════════════════════════════════════════════════╝\n');

console.log(`  Network: ${NETWORK}`);
console.log(`  Indexer: ${config.indexer}`);
console.log(`  Node: ${config.node}\n`);

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

try {
  console.log('─── Step 1: Derive Keys ────────────────────────────────────────\n');
  
  const keys = deriveKeys(MNEMONIC);
  const shieldedSecretKeys = ledger.ZswapSecretKeys.fromSeed(keys[Roles.Zswap]);
  const dustSecretKey = ledger.DustSecretKey.fromSeed(keys[Roles.Dust]);
  const unshieldedKeystore = createKeystore(keys[Roles.NightExternal], NETWORK);
  
  const address = unshieldedKeystore.getBech32Address();
  console.log(`  ✓ Wallet Address: ${address}\n`);
  
  console.log('─── Step 2: Initialize Wallet ──────────────────────────────────\n');
  
  const configuration = {
    networkId: NETWORK,
    costParameters: {
      feeBlocksMargin: 5,
    },
    relayURL: new URL(config.node),
    provingServerUrl: new URL(config.proofServer),
    indexerClientConnection: {
      indexerHttpUrl: config.indexer,
      indexerWsUrl: config.indexerWS,
    },
    txHistoryStorage: new InMemoryTransactionHistoryStorage(),
  };
  
  console.log('  Creating wallet facade...');
  
  const wallet = await WalletFacade.init({
    configuration,
    shielded: (cfg) => ShieldedWallet(cfg).startWithSecretKeys(shieldedSecretKeys),
    unshielded: (cfg) => UnshieldedWallet(cfg).startWithPublicKey(PublicKey.fromKeyStore(unshieldedKeystore)),
    dust: (cfg) => DustWallet(cfg).startWithSecretKey(dustSecretKey, ledger.LedgerParameters.initialParameters().dust),
  });
  
  console.log('  Starting wallet...');
  await wallet.start(shieldedSecretKeys, dustSecretKey);
  
  console.log('  Syncing with network (this takes 10-30 seconds)...\n');
  
  // Wait for sync with timeout
  const syncPromise = wallet.waitForSyncedState();
  const timeoutPromise = new Promise((_, reject) => 
    setTimeout(() => reject(new Error('Sync timeout after 45 seconds')), 45000)
  );
  
  const state = await Promise.race([syncPromise, timeoutPromise]);
  
  console.log('─── Step 3: Balance ─────────────────────────────────────────────\n');
  
  const nightBalance = state.shielded.balances[ledger.shieldedToken().raw] ?? 0n;
  const unshieldedBalance = state.unshielded.balances[ledger.unshieldedToken().raw] ?? 0n;
  const dustBalance = state.dust.walletBalance(new Date());
  
  console.log(`  Address: ${address}`);
  console.log(`  NIGHT (shielded):   ${nightBalance.toLocaleString()}`);
  console.log(`  NIGHT (unshielded): ${unshieldedBalance.toLocaleString()}`);
  console.log(`  DUST:               ${dustBalance.toLocaleString()}\n`);
  
  console.log('─── Step 4: Wallet Details ──────────────────────────────────────\n');
  
  console.log(`  Shielded coins: ${state.shielded.availableCoins.length}`);
  console.log(`  Unshielded UTXOs: ${state.unshielded.availableCoins.length}`);
  console.log(`  DUST coins: ${state.dust.availableCoins.length}`);
  console.log(`  Synced: ${state.isSynced ? '✓' : '✗'}\n`);
  
  await wallet.stop();
  
  console.log('─── Complete! ───────────────────────────────────────────────────\n');
  
  if (nightBalance > 0n || unshieldedBalance > 0n) {
    console.log('  ✅ Wallet is funded and ready for deployment!\n');
  } else {
    console.log('  ⚠️  Wallet has no funds. Visit:');
    console.log('     https://faucet.preprod.midnight.network/\n');
  }
  
} catch (error) {
  console.error('\n❌ Error:', error.message);
  if (error.stack) {
    console.error('\nStack trace:');
    console.error(error.stack);
  }
  process.exit(1);
}
