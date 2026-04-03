import { WalletFacade } from "@midnight-ntwrk/wallet-sdk-facade";
import { DustWallet } from "@midnight-ntwrk/wallet-sdk-dust-wallet";
import { HDWallet, Roles } from "@midnight-ntwrk/wallet-sdk-hd";
import { ShieldedWallet } from "@midnight-ntwrk/wallet-sdk-shielded";
import { createKeystore, InMemoryTransactionHistoryStorage, PublicKey, UnshieldedWallet } from "@midnight-ntwrk/wallet-sdk-unshielded-wallet";
import { setNetworkId } from "@midnight-ntwrk/midnight-js-network-id";
import * as ledger from "@midnight-ntwrk/ledger-v8";
import { Buffer } from "buffer";

const MNEMONIC = process.env.MNEMONIC;
const NETWORK = process.env.NETWORK || "undeployed";

if (!MNEMONIC) {
  console.error("Set MNEMONIC env variable first");
  process.exit(1);
}

setNetworkId(NETWORK);

// Network configurations
const NETWORKS = {
  undeployed: {
    indexer:     "http://127.0.0.1:8088/api/v4/graphql",
    indexerWS:   "ws://127.0.0.1:8088/api/v4/graphql/ws",
    proofServer: "http://127.0.0.1:6300",
    node:        "ws://127.0.0.1:9944",
  },
  preprod: {
    indexer:     "https://indexer.preprod.midnight.network/api/v4/graphql",
    indexerWS:   "wss://indexer.preprod.midnight.network/api/v4/graphql/ws",
    proofServer: "https://proof-server.preprod.midnight.network",
    node:        "wss://rpc.preprod.midnight.network",
  },
  testnet: {
    indexer:     "https://indexer.testnet-02.midnight.network/api/v4/graphql",
    indexerWS:   "wss://indexer.testnet-02.midnight.network/api/v4/graphql/ws",
    proofServer: "https://proof-server.testnet-02.midnight.network",
    node:        "wss://rpc.testnet-02.midnight.network",
  }
};

const config = NETWORKS[NETWORK] || NETWORKS.undeployed;

// Derive keys from mnemonic
function deriveKeys(seed) {
  const hdWallet = HDWallet.fromSeed(Buffer.from(seed, 'hex'));
  if (hdWallet.type !== 'seedOk') throw new Error('Invalid seed');
  
  const result = hdWallet.hdWallet
    .selectAccount(0)
    .selectRoles([Roles.Zswap, Roles.NightExternal, Roles.Dust])
    .deriveKeysAt(0);
  
  if (result.type !== 'keysDerived') throw new Error('Key derivation failed');
  
  hdWallet.hdWallet.clear();
  return result.keys;
}

console.log(`Connecting to wallet on ${NETWORK}...`);
try {
  // Convert mnemonic to seed (simplified - in production use proper BIP39)
  const seed = Buffer.from(MNEMONIC.split(' ').map((w, i) => i.toString(16).padStart(2, '0')).join(''), 'hex');
  
  const keys = deriveKeys(seed);
  const shieldedSecretKeys = ledger.ZswapSecretKeys.fromSeed(keys[Roles.Zswap]);
  const dustSecretKey = ledger.DustSecretKey.fromSeed(keys[Roles.Dust]);
  const unshieldedKeystore = createKeystore(keys[Roles.NightExternal], NETWORK);
  
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
  
  console.log("Syncing... (this takes 10-30 seconds)");
  
  const state = await wallet.waitForSyncedState();
  
  const address = unshieldedKeystore.getBech32Address();
  const nightBalance = state.shielded.balances[ledger.shieldedToken().raw] ?? 0n;
  const dustBalance = state.dust.walletBalance(new Date());
  
  console.log("Address:", address);
  console.log("NIGHT:  ", nightBalance.toString());
  console.log("DUST:   ", dustBalance.toString());
  
  await wallet.stop();
} catch (err) {
  console.error("Error:", err.message);
  if (err.stack) {
    console.error(err.stack);
  }
  process.exit(1);
}
