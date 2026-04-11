#!/usr/bin/env node
/**
 * Derive all three wallet address types from mnemonic
 * Uses the official Midnight SDK
 */

import { HDWallet, Roles } from "@midnight-ntwrk/wallet-sdk-hd";
import { createKeystore } from "@midnight-ntwrk/wallet-sdk-unshielded-wallet";
import { setNetworkId } from "@midnight-ntwrk/midnight-js-network-id";
import { MidnightBech32m, UnshieldedAddress, ShieldedAddress, DustAddress, ShieldedCoinPublicKey, ShieldedEncryptionPublicKey } from "@midnight-ntwrk/wallet-sdk-address-format";
import * as ledger from "@midnight-ntwrk/ledger-v8";
import { mnemonicToSeedSync } from "bip39";

const MNEMONIC = process.env.MNEMONIC;
const NETWORK_ID = process.env.NETWORK_ID || "undeployed";

if (!MNEMONIC) {
  console.error(JSON.stringify({ error: "MNEMONIC environment variable is required" }));
  process.exit(1);
}

setNetworkId(NETWORK_ID);

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

async function main() {
  try {
    const keys = deriveKeys(MNEMONIC);
    
    // 1. Unshielded address (NIGHT) - use keystore method
    const unshieldedKeystore = createKeystore(keys[Roles.NightExternal], NETWORK_ID);
    let unshieldedAddress = unshieldedKeystore.getBech32Address();
    
    // Handle if it returns an object - convert to string
    if (typeof unshieldedAddress !== 'string') {
      if (unshieldedAddress && typeof unshieldedAddress.toString === 'function') {
        unshieldedAddress = unshieldedAddress.toString();
      } else {
        unshieldedAddress = JSON.stringify(unshieldedAddress);
      }
    }
    
    // 2. Shielded address (NIGHT)
    const shieldedSecretKeys = ledger.ZswapSecretKeys.fromSeed(keys[Roles.Zswap]);
    const shieldedAddr = new ShieldedAddress(
      new ShieldedCoinPublicKey(Buffer.from(shieldedSecretKeys.coinPublicKey, 'hex')),
      new ShieldedEncryptionPublicKey(Buffer.from(shieldedSecretKeys.encryptionPublicKey, 'hex'))
    );
    const shieldedAddress = MidnightBech32m.encode(NETWORK_ID, shieldedAddr).toString();
    
    // 3. DUST address
    const dustSecretKey = ledger.DustSecretKey.fromSeed(keys[Roles.Dust]);
    const dustAddr = new DustAddress(dustSecretKey.publicKey);
    const dustAddress = MidnightBech32m.encode(NETWORK_ID, dustAddr).toString();
    
    console.log(JSON.stringify({
      network: NETWORK_ID,
      addresses: {
        unshielded: unshieldedAddress,
        shielded: shieldedAddress,
        dust: dustAddress
      }
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
