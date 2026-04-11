#!/usr/bin/env python3
"""
Deploy contract using Python SDK with proper key handling
"""

from midnight_sdk import MidnightClient
from midnight_sdk.wallet import WalletClient
from midnight_sdk.config import ConfigManager

def deploy_hello_world():
    # Load config
    config_mgr = ConfigManager()
    config_mgr.load()
    
    # Get local profile
    profile = config_mgr.get_profile("local")
    
    # Get wallet mnemonic
    wallet_file = config_mgr.config.wallets.get("shielded-test")
    with open(wallet_file, 'r') as f:
        mnemonic = f.read().strip()
    
    # Get private key
    wallet_client = WalletClient(profile.node_url)
    keys = wallet_client.get_private_keys(mnemonic)
    private_key = keys['nightExternal']
    
    print(f"🚀 Deploying hello_world.compact...")
    print(f"📡 Network: {profile.name}")
    print(f"💼 Wallet: shielded-test")
    
    # Initialize client
    client = MidnightClient(network="local")
    
    # Deploy contract
    contract = client.contracts.deploy(
        "contracts/hello_world.compact",
        private_key=private_key,
        sign_transaction=True
    )
    
    print(f"✅ Contract deployed!")
    print(f"📍 Address: {contract.address}")
    print(f"🔧 Circuits: {contract.circuit_ids}")
    
    return contract

if __name__ == "__main__":
    try:
        contract = deploy_hello_world()
        
        # Test interaction
        print(f"\n🔄 Testing contract interaction...")
        result = contract.call(
            circuit_name="storeMessage",
            args={"newMessage": "Hello from Python!"},
            private_key=contract._private_key,
            sign_transaction=True
        )
        print(f"📝 Message stored! TX: {result.tx_hash}")
        
    except Exception as e:
        print(f"❌ Error: {e}")