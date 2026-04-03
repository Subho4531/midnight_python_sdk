#!/usr/bin/env node
/**
 * Deploy Midnight contracts to real networks (preprod, testnet) using official SDK
 * 
 * Usage:
 *   MNEMONIC="your 24 words" NETWORK=preprod node deploy_contract_real.mjs contracts/hello_world.compact
 */

import { readFileSync, existsSync } from 'fs';
import { resolve, dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { WebSocket } from 'ws';
import * as Rx from 'rxjs';
import { Buffer } from 'buffer';

// Midnight SDK imports
import { httpClientProofProvider } from '@midnight-ntwrk/midnight-js-http-client-proof-provider';
import { indexerPublicDataProvider } from '@midnight-ntwrk/midnight-js-indexer-public-data-provider';
import { levelPrivateStateProvider } from '@midnight-ntwrk/midnight-js-level-private-state-provider';
import { NodeZkConfigProvider } from '@midnight-ntwrk/midnight-js-node-zk-config-provider';
import { setNetworkId, getNetworkId } from '@midnight-ntwrk/midnight-js-network-id';
import { deployContract } from '@midnight-ntwrk/midnight-js-contracts';
import * as ledger from '@midnight-ntwrk/ledger-v8';
import { WalletFacade } from '@midnight-ntwrk/wallet-sdk-facade';
import { DustWallet } from '@midnight-ntwrk/wallet-sdk-dust-wallet';
import { HDWallet, Roles } from '@midnight-ntwrk/wallet-sdk-hd';
import { ShieldedWallet } from '@midnight-ntwrk/wallet-sdk-shielded';
import { createKeystore, InMemoryTransactionHistoryStorage, PublicKey, UnshieldedWallet } from '@midnight-ntwrk/wallet-sdk-unshielded-wallet';
import { CompiledContract } from '@midnight-ntwrk/compact-js';

// Enable WebSocket for GraphQL subscriptions
globalThis.WebSocket = WebSocket;

const __dirname = dirname(fileURLToPath(import.meta.url));

// Get environment variables
const MNEMONIC = process.env.MNEMONIC;
const NETWORK = process.env.NETWORK || 'preprod';
const CONTRACT_PATH = process.argv[2];

if (!MNEMONIC) {
  console.error('❌ MNEMONIC environment variable not set');
  console.error('Usage: MNEMONIC="your 24 words" NETWORK=preprod node deploy_contract_real.mjs <contract.compact>');
  process.exit(1);
}

if (!CONTRACT_PATH) {
  console.error('❌ Contract path not provided');
  console.error('Usage: MNEMONIC="your 24 words" NETWORK=preprod node deploy_contract_real.mjs <contract.compact>');
  process.exit(1);
}

// Network configurations
const NETWORKS = {
  preprod: {
    indexer: 'https://indexer.preprod.midnight.network/api/v4/graphql',
    indexerWS: 'wss://indexer.preprod.midnight.network/api/v4/graphql/ws',
    node: 'https://rpc.preprod.midnight.network',
    proofServer: 'https://proof-server.preprod.midnight.network',
    networkId: 'preprod',
    explorer: 'https://explorer.preprod.midnight.network',
  },
  testnet: {
    indexer: 'https://indexer.testnet-02.midnight.network/api/v4/graphql',
    indexerWS: 'wss://indexer.testnet-02.midnight.network/api/v4/graphql/ws',
    node: 'https://rpc.testnet-02.midnight.network',
    proofServer: 'https://proof-server.testnet-02.midnight.network',
    networkId: 'testnet-02',
    explorer: 'https://explorer.testnet-02.midnight.network',
  },
  undeployed: {
    indexer: 'http://127.0.0.1:8088/api/v4/graphql',
    indexerWS: 'ws://127.0.0.1:8088/api/v4/graphql/ws',
    node: 'http://127.0.0.1:9944',
    proofServer: 'http://127.0.0.1:6300',
    networkId: 'undeployed',
    explorer: 'http://localhost:8088',
  },
};

const CONFIG = NETWORKS[NETWORK];
if (!CONFIG) {
  console.error(`❌ Unknown network: ${NETWORK}`);
  console.error(`Available networks: ${Object.keys(NETWORKS).join(', ')}`);
  process.exit(1);
}

setNetworkId(CONFIG.networkId);

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

// Create wallet
async function createWallet(seed) {
  const keys = deriveKeys(seed);
  const networkId = getNetworkId();
  
  // Derive secret keys for different wallet components
  const shieldedSecretKeys = ledger.ZswapSecretKeys.fromSeed(keys[Roles.Zswap]);
  const dustSecretKey = ledger.DustSecretKey.fromSeed(keys[Roles.Dust]);
  const unshieldedKeystore = createKeystore(keys[Roles.NightExternal], networkId);
  
  const walletConfig = {
    networkId,
    indexerClientConnection: {
      indexerHttpUrl: CONFIG.indexer,
      indexerWsUrl: CONFIG.indexerWS
    },
    provingServerUrl: new URL(CONFIG.proofServer),
    relayURL: new URL(CONFIG.node.replace(/^http/, 'ws')),
  };
  
  // Initialize wallet components
  const shieldedWallet = ShieldedWallet(walletConfig)
    .startWithSecretKeys(shieldedSecretKeys);
  
  const unshieldedWallet = UnshieldedWallet({
    networkId,
    indexerClientConnection: walletConfig.indexerClientConnection,
    txHistoryStorage: new InMemoryTransactionHistoryStorage(),
  }).startWithPublicKey(PublicKey.fromKeyStore(unshieldedKeystore));
  
  const dustWallet = DustWallet({
    ...walletConfig,
    costParameters: {
      additionalFeeOverhead: 300_000_000_000_000n,
      feeBlocksMargin: 5
    },
  }).startWithSecretKey(dustSecretKey, ledger.LedgerParameters.initialParameters().dust);
  
  const wallet = new WalletFacade(shieldedWallet, unshieldedWallet, dustWallet);
  await wallet.start(shieldedSecretKeys, dustSecretKey);
  
  return { wallet, shieldedSecretKeys, dustSecretKey, unshieldedKeystore };
}

// Sign transaction intents
function signTransactionIntents(tx, signFn, proofMarker) {
  if (!tx.intents || tx.intents.size === 0) return;
  
  for (const segment of tx.intents.keys()) {
    const intent = tx.intents.get(segment);
    if (!intent) continue;
    
    const cloned = ledger.Intent.deserialize(
      'signature',
      proofMarker,
      'pre-binding',
      intent.serialize()
    );
    
    const sigData = cloned.signatureData(segment);
    const signature = signFn(sigData);
    
    if (cloned.fallibleUnshieldedOffer) {
      const sigs = cloned.fallibleUnshieldedOffer.inputs.map(
        (_, i) => cloned.fallibleUnshieldedOffer.signatures.at(i) ?? signature
      );
      cloned.fallibleUnshieldedOffer = cloned.fallibleUnshieldedOffer.addSignatures(sigs);
    }
    
    if (cloned.guaranteedUnshieldedOffer) {
      const sigs = cloned.guaranteedUnshieldedOffer.inputs.map(
        (_, i) => cloned.guaranteedUnshieldedOffer.signatures.at(i) ?? signature
      );
      cloned.guaranteedUnshieldedOffer = cloned.guaranteedUnshieldedOffer.addSignatures(sigs);
    }
    
    tx.intents.set(segment, cloned);
  }
}

// Create providers
async function createProviders(walletCtx, zkConfigPath) {
  const state = await Rx.firstValueFrom(
    walletCtx.wallet.state().pipe(Rx.filter((s) => s.isSynced))
  );
  
  const walletProvider = {
    getCoinPublicKey: () => state.shielded.coinPublicKey.toHexString(),
    getEncryptionPublicKey: () => state.shielded.encryptionPublicKey.toHexString(),
    async balanceTx(tx, ttl) {
      const recipe = await walletCtx.wallet.balanceUnboundTransaction(
        tx,
        {
          shieldedSecretKeys: walletCtx.shieldedSecretKeys,
          dustSecretKey: walletCtx.dustSecretKey
        },
        { ttl: ttl ?? new Date(Date.now() + 30 * 60 * 1000) },
      );
      
      const signFn = (payload) => walletCtx.unshieldedKeystore.signData(payload);
      
      signTransactionIntents(recipe.baseTransaction, signFn, 'proof');
      if (recipe.balancingTransaction) {
        signTransactionIntents(recipe.balancingTransaction, signFn, 'pre-proof');
      }
      
      return walletCtx.wallet.finalizeRecipe(recipe);
    },
    submitTx: (tx) => walletCtx.wallet.submitTransaction(tx),
  };
  
  const zkConfigProvider = new NodeZkConfigProvider(zkConfigPath);
  
  return {
    privateStateProvider: levelPrivateStateProvider({
      privateStateStoreName: 'contract-private-state',
      walletProvider
    }),
    publicDataProvider: indexerPublicDataProvider(CONFIG.indexer, CONFIG.indexerWS),
    zkConfigProvider,
    proofProvider: httpClientProofProvider(CONFIG.proofServer, zkConfigProvider),
    walletProvider,
    midnightProvider: walletProvider,
  };
}

// Main deployment function
async function main() {
  console.log('\n╔══════════════════════════════════════════════════════════════╗');
  console.log('║        Deploy Contract to Midnight Network                   ║');
  console.log('╚══════════════════════════════════════════════════════════════╝\n');
  
  console.log(`  Network: ${NETWORK} (${CONFIG.networkId})`);
  console.log(`  Contract: ${CONTRACT_PATH}`);
  console.log(`  Explorer: ${CONFIG.explorer}\n`);
  
  // Check if contract is compiled
  const contractName = CONTRACT_PATH.replace(/^contracts\//, '').replace(/\.compact$/, '');
  const zkConfigPath = resolve(__dirname, 'contracts', 'managed', contractName);
  const contractIndexPath = join(zkConfigPath, 'contract', 'index.js');
  
  if (!existsSync(contractIndexPath)) {
    console.error(`❌ Contract not compiled: ${contractName}`);
    console.error(`   Run: npx compact compile ${CONTRACT_PATH} ${zkConfigPath}`);
    process.exit(1);
  }
  
  console.log('─── Step 1: Load Compiled Contract ────────────────────────────\n');
  
  // Load compiled contract
  const ContractModule = await import(`file://${contractIndexPath}`);
  const compiledContract = CompiledContract.make(contractName, ContractModule.Contract).pipe(
    CompiledContract.withVacantWitnesses,
    CompiledContract.withCompiledFileAssets(zkConfigPath),
  );
  
  console.log(`  ✓ Loaded contract: ${contractName}\n`);
  
  // Convert mnemonic to seed
  console.log('─── Step 2: Initialize Wallet ──────────────────────────────────\n');
  
  // For simplicity, we'll use the mnemonic as hex seed
  // In production, you'd use proper BIP39 mnemonic to seed conversion
  const seed = Buffer.from(MNEMONIC.split(' ').map((w, i) => i.toString(16).padStart(2, '0')).join(''), 'hex');
  
  console.log('  Creating wallet...');
  const walletCtx = await createWallet(seed);
  
  console.log('  Syncing with network...');
  const state = await Rx.firstValueFrom(
    walletCtx.wallet.state().pipe(
      Rx.throttleTime(5000),
      Rx.filter((s) => s.isSynced)
    )
  );
  
  const address = walletCtx.unshieldedKeystore.getBech32Address();
  const balance = state.unshielded.balances[ledger.unshieldedToken().raw] ?? 0n;
  const dustBalance = state.dust.walletBalance(new Date());
  
  console.log(`\n  Wallet Address: ${address}`);
  console.log(`  Balance: ${balance.toLocaleString()} tNight`);
  console.log(`  DUST: ${dustBalance.toLocaleString()}\n`);
  
  if (balance === 0n) {
    console.error('❌ Wallet has no funds');
    console.error(`   Visit: https://faucet.${NETWORK}.midnight.network/`);
    console.error(`   Address: ${address}`);
    await walletCtx.wallet.stop();
    process.exit(1);
  }
  
  if (dustBalance === 0n) {
    console.error('❌ Wallet has no DUST');
    console.error('   Register your NIGHT tokens for DUST generation first');
    await walletCtx.wallet.stop();
    process.exit(1);
  }
  
  console.log('─── Step 3: Deploy Contract ────────────────────────────────────\n');
  
  console.log('  Setting up providers...');
  const providers = await createProviders(walletCtx, zkConfigPath);
  
  console.log('  Deploying contract (this may take 30-60 seconds)...\n');
  
  try {
    const deployed = await deployContract(providers, {
      compiledContract,
      privateStateId: 'contractState',
      initialPrivateState: {},
    });
    
    const contractAddress = deployed.deployTxData.public.contractAddress;
    const txId = deployed.deployTxData.public.txId;
    const blockHeight = deployed.deployTxData.public.blockHeight;
    
    console.log('  ✅ Contract deployed successfully!\n');
    console.log(`  Contract Address: ${contractAddress}`);
    console.log(`  Transaction ID: ${txId}`);
    console.log(`  Block Height: ${blockHeight}`);
    console.log(`\n  🔍 View on Explorer:`);
    console.log(`     ${CONFIG.explorer}/tx/${txId}\n`);
    
    await walletCtx.wallet.stop();
    
    console.log('─── Deployment Complete! ───────────────────────────────────────\n');
    
  } catch (error) {
    console.error('\n❌ Deployment failed:', error.message);
    if (error.cause) {
      console.error('   Cause:', error.cause);
    }
    await walletCtx.wallet.stop();
    process.exit(1);
  }
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
