// Get wallet addresses for all Midnight networks
import { HDWallet } from "@midnight-ntwrk/wallet-sdk-hd";
import { setNetworkId } from "@midnight-ntwrk/midnight-js-network-id";
import { readFileSync } from "fs";

// Read mnemonic from file
let MNEMONIC;
try {
  const mnemonicContent = readFileSync("mnemonic.txt.example", "utf-8");
  const lines = mnemonicContent.split('\n').filter(line => line.trim() && !line.trim().startsWith('#'));
  MNEMONIC = lines[lines.length - 1].trim();
} catch (err) {
  console.error("Error reading mnemonic:", err.message);
  process.exit(1);
}

const networks = [
  { id: "undeployed", name: "Local Undeployed" },
  { id: "testnet-02", name: "Testnet-02" },
  { id: "preprod", name: "Preprod" },
  { id: "devnet", name: "Devnet" },
  { id: "mainnet", name: "Mainnet" }
];

console.log("\n" + "=".repeat(70));
console.log("  Wallet Addresses for All Networks");
console.log("=".repeat(70) + "\n");

for (const network of networks) {
  try {
    setNetworkId(network.id);
    
    // Note: Full address derivation requires the complete wallet SDK
    // For now, we'll show the network ID and explain
    console.log(`${network.name} (${network.id}):`);
    console.log(`  Network ID: ${network.id}`);
    console.log(`  Address prefix: mn_addr_${network.id}1...`);
    console.log(`  Status: Requires full wallet SDK for address derivation`);
    console.log();
  } catch (err) {
    console.log(`${network.name}: Error - ${err.message}`);
    console.log();
  }
}

console.log("=".repeat(70));
console.log("\nYour current address is for 'undeployed' network (local).");
console.log("To use real Midnight networks (preprod/devnet), you need:");
console.log("  1. Run the official Midnight wallet");
console.log("  2. Get your address for that specific network");
console.log("  3. Fund it from a faucet or transfer");
console.log("\nThe local 'undeployed' network IS creating real transactions,");
console.log("but they're on your local blockchain, not the public Midnight chain.");
console.log("=".repeat(70) + "\n");
