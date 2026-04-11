// get_wallet_address.mjs
// Derives wallet address from mnemonic using official Midnight SDK
import { HDWallet, Roles } from "@midnight-ntwrk/wallet-sdk-hd";
import { createKeystore } from "@midnight-ntwrk/wallet-sdk-unshielded-wallet";
import { setNetworkId } from "@midnight-ntwrk/midnight-js-network-id";
import { mnemonicToSeedSync } from "bip39";

const MNEMONIC = process.env.MNEMONIC;
const NETWORK_ID = process.env.NETWORK_ID || "undeployed";

if (!MNEMONIC) {
  console.error("Error: MNEMONIC environment variable is required");
  process.exit(1);
}

// Derive keys from mnemonic using proper BIP39
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

async function main() {
  try {
    setNetworkId(NETWORK_ID);
    
    const keys = deriveKeys(MNEMONIC);
    
    // Create keystore and get address - this should return a Bech32m string
    const unshieldedKeystore = createKeystore(keys[Roles.NightExternal], NETWORK_ID);
    const address = unshieldedKeystore.getBech32Address();
    
    // Handle both string and object returns
    let addressStr;
    if (typeof address === 'string') {
      addressStr = address;
    } else if (address && typeof address.toString === 'function') {
      addressStr = address.toString();
    } else {
      // If it's still an object, stringify for debugging
      addressStr = JSON.stringify(address);
    }
    
    console.log(JSON.stringify({
      address: addressStr,
      network: NETWORK_ID
    }));

    process.exit(0);
  } catch (err) {
    console.error("Error:", err.message);
    if (err.stack) {
      console.error(err.stack);
    }
    process.exit(1);
  }
}

main();
