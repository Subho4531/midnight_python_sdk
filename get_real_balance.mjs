#!/usr/bin/env node
/**
 * Get real wallet balance using official Midnight SDK
 * 
 * This script properly reads shielded NIGHT balances that the indexer cannot see.
 * 
 * Usage:
 *   MNEMONIC="your 24 words" NETWORK=preprod node get_real_balance.mjs
 * 
 * Output (JSON):
 *   {"night": 1000, "dust": 19410900000, "address": "mn_addr_preprod1..."}
 */

import { WalletFacade } from "@midnight-ntwrk/wallet-sdk-facade";
import { DustWallet } from "@midnight-ntwrk/wallet-sdk-dust-wallet";
import { HDWallet, Roles } from "@midnight-ntwrk/wallet-sdk-hd";
import { ShieldedWallet } from "@midnight-ntwrk/wallet-sdk-shielded";
import { createKeystore, InMemoryTransactionHistoryStorage, PublicKey, UnshieldedWallet } from "@midnight-ntwrk/wallet-sdk-unshielded-wallet";
import { setNetworkId } from "@midnight-ntwrk/midnight-js-network-id";
import * as ledger from "@midnight-ntwrk/ledger-v8";
import { mnemonicToSeedSync } from "bip39";

const MNEMONIC = process.env.MNEMONIC;
const NETWORK = process.env.NETWORK || "preprod";

if (!MNEMONIC) {
  console.error(JSON.stringify({
    error: "MNEMONIC environment variable not set",
    night: 0,
    dust: 0
  }));
  process.exit(1);
}

setNetworkId(NETWORK);

const NETWORK_CONFIGS = {
  preprod: {
    indexer: "https://indexer.preprod.midnight.network/api/v4/graphql",
    indexerWS: "wss://indexer.preprod.midnight.network/api/v4/graphql/ws",
    proofServer: "https://proof-server.preprod.midnight.network",
    node: "wss://rpc.preprod.midnight.network",
  },
  testnet: {
    indexer: "https://indexer.testnet-02.midnight.network/api/v4/graphql",
    indexerWS: "wss://indexer.testnet-02.midnight.network/api/v4/graphql/ws",
    proofServer: "https://proof-server.testnet-02.midnight.network",
    node: "wss://rpc.testnet-02.midnight.network",
  },
  mainnet: {
    indexer: "https://indexer.midnight.network/api/v4/graphql",
    indexerWS: "wss://indexer.midnight.network/api/v4/graphql/ws",
    proofServer: "https://proof-server.midnight.network",
    node: "wss://rpc.midnight.network",
  },
};

const config = NETWORK_CONFIGS[NETWORK];

if (!config) {
  console.error(JSON.stringify({
    error: `Unknown network: ${NETWORK}`,
    night: 0,
    dust: 0
  }));
  process.exit(1);
}

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
  const keys = deriveKeys(MNEMONIC);
  const shieldedSecretKeys = ledger.ZswapSecretKeys.fromSeed(keys[Roles.Zswap]);
  const dustSecretKey = ledger.DustSecretKey.fromSeed(keys[Roles.Dust]);
  const unshieldedKeystore = createKeystore(keys[Roles.NightExternal], NETWORK);
  
  const address = unshieldedKeystore.getBech32Address();
  
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
  
  const wallet = await WalletFacade.init({
    configuration,
    shielded: (cfg) => ShieldedWallet(cfg).startWithSecretKeys(shieldedSecretKeys),
    unshielded: (cfg) => UnshieldedWallet(cfg).startWithPublicKey(PublicKey.fromKeyStore(unshieldedKeystore)),
    dust: (cfg) => DustWallet(cfg).startWithSecretKey(dustSecretKey, ledger.LedgerParameters.initialParameters().dust),
  });
  
  await wallet.start(shieldedSecretKeys, dustSecretKey);
  
  // Wait for sync with timeout
  const syncPromise = wallet.waitForSyncedState();
  const timeoutPromise = new Promise((_, reject) => 
    setTimeout(() => reject(new Error('Sync timeout after 45 seconds')), 45000)
  );
  
  const state = await Promise.race([syncPromise, timeoutPromise]);
  
  const nightBalance = state.shielded.balances[ledger.shieldedToken().raw] ?? 0n;
  const unshieldedBalance = state.unshielded.balances[ledger.unshieldedToken().raw] ?? 0n;
  const dustBalance = state.dust.walletBalance(new Date());
  
  // Output JSON for Python to parse
  console.log(JSON.stringify({
    address: address,
    night: Number(nightBalance),
    unshielded: Number(unshieldedBalance),
    dust: Number(dustBalance),
    synced: state.isSynced,
    network: NETWORK
  }));
  
  await wallet.stop();
  
} catch (error) {
  console.error(JSON.stringify({
    error: error.message,
    night: 0,
    dust: 0
  }));
  process.exit(1);
}
