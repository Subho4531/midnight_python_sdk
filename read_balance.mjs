import { WalletBuilder } from "@midnight-ntwrk/wallet-sdk-facade";
import { setNetworkId } from "@midnight-ntwrk/midnight-js-network-id";

setNetworkId("undeployed");

const MNEMONIC = process.env.MNEMONIC;
if (!MNEMONIC) {
  console.error("Set MNEMONIC env variable first");
  process.exit(1);
}

const config = {
  indexer:     "http://127.0.0.1:8088/api/v3/graphql",
  indexerWS:   "ws://127.0.0.1:8088/api/v3/graphql/ws",
  proofServer: "http://127.0.0.1:6300",
  node:        "http://127.0.0.1:9944",
};

console.log("Connecting to wallet...");
try {
  const wallet = await WalletBuilder.restore(
    config.indexer,
    config.indexerWS,
    config.proofServer,
    config.node,
    MNEMONIC,
    "undeployed"
  );

  await wallet.start();
  console.log("Syncing... (this takes 10-30 seconds)");

  await new Promise(resolve => setTimeout(resolve, 15000));

  const state = await new Promise(resolve => {
    wallet.state().subscribe(s => resolve(s));
  });

  console.log("Address:", state.address);
  console.log("NIGHT:  ", state.balances?.night?.toString() ?? "0");
  console.log("DUST:   ", state.balances?.dust?.toString()  ?? "0");

  await wallet.close();
} catch (err) {
  console.error("Error:", err.message);
}
