#!/usr/bin/env node
/**
 * Get full wallet balance (shielded + unshielded + DUST)
 * Uses the official Midnight Wallet SDK
 */

import { WalletFacade } from "@midnight-ntwrk/wallet-sdk-facade";
import { DustWallet } from "@midnight-ntwrk/wallet-sdk-dust-wallet";
import { HDWallet, Roles } from "@midnight-ntwrk/wallet-sdk-hd";
import { ShieldedWallet } from "@midnight-ntwrk/wallet-sdk-shielded";
import { createKeystore, InMemoryTransactionHistoryStorage, PublicKey, UnshieldedWallet } from "@midnight-ntwrk/wallet-sdk-unshielded-wallet";
import { MidnightBech32m, DustAddress, ShieldedAddress, ShieldedCoinPublicKey, ShieldedEncryptionPublicKey } from "@midnight-ntwrk/wallet-sdk-address-format";
import { setNetworkId } from "@midnight-ntwrk/midnight-js-network-id";
import * as ledger from "@midnight-ntwrk/ledger-v8";
import { mnemonicToSeedSync } from "bip39";
import * as Rx from "rxjs";

const MNEMONIC = process.env.MNEMONIC;
const NETWORK = process.env.NETWORK_ID || "undeployed";
const INDEXER_URL = process.env.INDEXER_URL || "https://indexer.preprod.midnight.network/api/v4/graphql";
const INDEXER_WS = process.env.INDEXER_WS || "wss://indexer.preprod.midnight.network/api/v4/graphql/ws";
const NODE_URL = process.env.NODE_URL || "wss://rpc.preprod.midnight.network";
const PROOF_URL = process.env.PROOF_URL || "https://lace-proof-pub.preprod.midnight.network";

if (!MNEMONIC) {
  console.error(JSON.stringify({ error: "MNEMONIC environment variable is required" }));
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

async function getFullBalance() {
  try {
    // Derive keys
    const keys = deriveKeys(MNEMONIC);
    const shieldedSecretKeys = ledger.ZswapSecretKeys.fromSeed(keys[Roles.Zswap]);
    const dustSecretKey = ledger.DustSecretKey.fromSeed(keys[Roles.Dust]);
    const unshieldedKeystore = createKeystore(keys[Roles.NightExternal], NETWORK);
    
    const unshieldedAddressObj = unshieldedKeystore.getBech32Address();
    // SDK v2.1.0 returns a string, v3+ returns an object - handle both
    const unshieldedAddress = typeof unshieldedAddressObj === 'string' 
      ? unshieldedAddressObj 
      : unshieldedAddressObj.toString();
    
    // Get shielded address (encode to Bech32m)
    const shieldedAddressObj = new ShieldedAddress(
      new ShieldedCoinPublicKey(Buffer.from(shieldedSecretKeys.coinPublicKey, 'hex')),
      new ShieldedEncryptionPublicKey(Buffer.from(shieldedSecretKeys.encryptionPublicKey, 'hex'))
    );
    const shieldedAddress = MidnightBech32m.encode(NETWORK, shieldedAddressObj).toString();
    
    // Get DUST address (encode to Bech32m)
    const dustAddressObj = new DustAddress(dustSecretKey.publicKey);
    const dustAddress = MidnightBech32m.encode(NETWORK, dustAddressObj).toString();
    
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
    const wallet = await WalletFacade.init({
      configuration,
      shielded: (cfg) => ShieldedWallet(cfg).startWithSecretKeys(shieldedSecretKeys),
      unshielded: (cfg) => UnshieldedWallet(cfg).startWithPublicKey(PublicKey.fromKeyStore(unshieldedKeystore)),
      dust: (cfg) => DustWallet(cfg).startWithSecretKey(dustSecretKey, ledger.LedgerParameters.initialParameters().dust),
    });
    
    await wallet.start(shieldedSecretKeys, dustSecretKey);
    
    // Wait for synced state, fall back to best available state after 60s
    console.error("Syncing wallet... (this may take up to 60 seconds)");
    let state;
    try {
      state = await Rx.firstValueFrom(
        wallet.state().pipe(
          Rx.filter(s => s.isSynced),
          Rx.timeout(60000),
        )
      );
      console.error("Wallet fully synced!");
    } catch {
      // Timeout — return whatever state we have
      console.error("Sync timeout - returning current state");
      state = await Rx.firstValueFrom(wallet.state());
    }
    
    // Get balances
    const shieldedNight = state.shielded.balances[ledger.shieldedToken().raw] ?? 0n;
    const unshieldedNight = state.unshielded.balances[ledger.unshieldedToken().raw] ?? 0n;
    const dust = state.dust.balance(new Date());
    
    // Output as JSON
    console.log(JSON.stringify({
      addresses: {
        unshielded: unshieldedAddress,
        shielded: shieldedAddress,
        dust: dustAddress
      },
      network: NETWORK,
      balances: {
        dust: dust.toString(),
        night_unshielded: unshieldedNight.toString(),
        night_shielded: shieldedNight.toString()
      },
      coins: {
        shielded: state.shielded.availableCoins.length,
        unshielded: state.unshielded.availableCoins.length,
        dust: state.dust.availableCoins.length
      },
      synced: state.isSynced
    }));
    
    await wallet.stop();
    process.exit(0);
    
  } catch (error) {
    console.error(JSON.stringify({ 
      error: error.message,
      stack: error.stack 
    }));
    process.exit(1);
  }
}

getFullBalance();
