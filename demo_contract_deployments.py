#!/usr/bin/env python3
"""
Live demonstration of contract deployments using Midnight SDK.
Shows practical examples with real contract files.
"""

import subprocess
import time
from pathlib import Path

def run_cli_command(cmd):
    """Run CLI command and return result"""
    try:
        print(f"🔧 Executing: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return result
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out")
        return None

def demo_hello_world_deployment():
    """Demonstrate Hello World contract deployment"""
    print("\n" + "="*60)
    print("🌟 DEMO: Hello World Contract Deployment")
    print("="*60)
    
    contract_path = "contracts/hello_world.compact"
    
    # Check if contract exists
    if not Path(contract_path).exists():
        print(f"❌ Contract file not found: {contract_path}")
        return
    
    print(f"📄 Contract: {contract_path}")
    print("📝 Description: Simple message storage contract")
    print("🎯 Circuits: storeMessage, getMessage")
    
    # Step 1: Compilation
    print("\n🔨 Step 1: Compiling contract...")
    result = run_cli_command(f"midnight contract compile {contract_path}")
    
    if result and result.returncode == 0:
        print("✅ Compilation successful!")
        print("📁 Output: contracts/managed/hello_world/")
    else:
        print("❌ Compilation failed")
        if result:
            print(f"Error: {result.stderr}")
        return
    
    # Step 2: Show what deployment would look like
    print("\n🚀 Step 2: Deployment command...")
    deployment_cmd = f"midnight contract deploy {contract_path} --wallet shielded-test --profile local"
    print(f"Command: {deployment_cmd}")
    
    print("\n📋 Expected deployment process:")
    print("   1. ✅ Load compiled contract from managed directory")
    print("   2. ✅ Derive private key from wallet mnemonic")
    print("   3. ✅ Create deployment transaction")
    print("   4. ✅ Sign transaction with private key")
    print("   5. ✅ Submit to local network")
    print("   6. ✅ Return contract address")
    
    # Step 3: Show interaction examples
    print("\n🔄 Step 3: Contract interaction examples...")
    print("After deployment, you can interact with the contract:")
    
    contract_addr = "0x1234567890abcdef"  # Example address
    
    interactions = [
        ("Store message", f"midnight contract call {contract_addr} storeMessage --args '{{\"newMessage\": \"Hello Midnight!\"}}'"),
        ("Get message", f"midnight contract query {contract_addr} getMessage"),
        ("List contracts", "midnight contract list --profile local"),
        ("Contract info", f"midnight contract info {contract_addr}"),
        ("Monitor events", f"midnight contract events {contract_addr} --follow")
    ]
    
    for description, command in interactions:
        print(f"\n   📝 {description}:")
        print(f"      {command}")

def demo_counter_deployment():
    """Demonstrate Counter contract deployment"""
    print("\n" + "="*60)
    print("🔢 DEMO: Counter Contract Deployment")
    print("="*60)
    
    contract_path = "contracts/counter.compact"
    
    print(f"📄 Contract: {contract_path}")
    print("📝 Description: Increment/decrement counter with state")
    print("🎯 Circuits: increment, getCount")
    
    # Compilation
    print("\n🔨 Compiling counter contract...")
    result = run_cli_command(f"midnight contract compile {contract_path}")
    
    if result and result.returncode == 0:
        print("✅ Counter contract compiled successfully!")
    else:
        print("❌ Compilation failed")
        return
    
    # Show deployment workflow
    print("\n🚀 Deployment workflow:")
    print("   1. Compile: ✅ Done")
    print("   2. Deploy: midnight contract deploy contracts/counter.compact --wallet shielded-test --profile local")
    print("   3. Interact: Call increment circuit to increase counter")
    print("   4. Query: Get current counter value")
    
    # Example interactions
    print("\n🔄 Example interactions:")
    example_addr = "0xabcdef1234567890"
    
    print(f"   # Increment counter")
    print(f"   midnight contract call {example_addr} increment")
    print(f"   ")
    print(f"   # Get current count")
    print(f"   midnight contract query {example_addr} getCount")
    print(f"   # Output: {{\"count\": 1}}")

def demo_bulletin_board_deployment():
    """Demonstrate Bulletin Board contract deployment"""
    print("\n" + "="*60)
    print("📢 DEMO: Bulletin Board Contract Deployment")
    print("="*60)
    
    contract_path = "contracts/bulletin_board.compact"
    
    print(f"📄 Contract: {contract_path}")
    print("📝 Description: Anonymous message posting system")
    print("🎯 Circuits: post, getMessages")
    print("🔒 Privacy: Anonymous message posting")
    
    # Compilation
    print("\n🔨 Compiling bulletin board...")
    result = run_cli_command(f"midnight contract compile {contract_path}")
    
    if result and result.returncode == 0:
        print("✅ Bulletin board compiled successfully!")
    else:
        print("❌ Compilation failed")
        return
    
    # Privacy features
    print("\n🔒 Privacy features:")
    print("   • Anonymous message posting")
    print("   • No sender identification")
    print("   • Message content verification")
    print("   • ZK proof of valid posting")
    
    # Usage example
    print("\n📝 Usage example:")
    example_addr = "0xfedcba0987654321"
    
    print(f"   # Post anonymous message")
    print(f"   midnight contract call {example_addr} post \\")
    print(f"     --args '{{\"message\": \"Hello anonymous world!\"}}'")
    print(f"   ")
    print(f"   # Read all messages")
    print(f"   midnight contract query {example_addr} getMessages")

def demo_ai_inference_deployment():
    """Demonstrate AI Inference contract deployment"""
    print("\n" + "="*60)
    print("🤖 DEMO: AI Inference Contract Deployment")
    print("="*60)
    
    contract_path = "contracts/ai_inference.compact"
    
    print(f"📄 Contract: {contract_path}")
    print("📝 Description: Private machine learning inference")
    print("🎯 Circuits: submitInferenceResult")
    print("🔒 Privacy: Private ML with ZK proofs")
    
    # Compilation
    print("\n🔨 Compiling AI inference contract...")
    result = run_cli_command(f"midnight contract compile {contract_path}")
    
    if result and result.returncode == 0:
        print("✅ AI inference contract compiled successfully!")
    else:
        print("❌ Compilation failed")
        return
    
    # AI/ML features
    print("\n🤖 AI/ML features:")
    print("   • Private inference execution")
    print("   • ZK proof of computation")
    print("   • Model privacy preservation")
    print("   • Result verification")
    
    # Usage example
    print("\n🧠 Usage example:")
    example_addr = "0x1122334455667788"
    
    print(f"   # Submit inference result")
    print(f"   midnight contract call {example_addr} submitInferenceResult \\")
    print(f"     --args '{{")
    print(f"       \"features\": [1.0, 2.0, 3.0, 4.0],")
    print(f"       \"prediction\": 0,")
    print(f"       \"confidence\": 0.95")
    print(f"     }}'")

def demo_private_vote_deployment():
    """Demonstrate Private Vote contract deployment"""
    print("\n" + "="*60)
    print("🗳️  DEMO: Private Vote Contract Deployment")
    print("="*60)
    
    contract_path = "contracts/private_vote.compact"
    
    print(f"📄 Contract: {contract_path}")
    print("📝 Description: Anonymous voting with ZK proofs")
    print("🎯 Circuits: voteYes, voteNo, getResults")
    print("🔒 Privacy: Anonymous voting system")
    
    # Compilation
    print("\n🔨 Compiling private vote contract...")
    result = run_cli_command(f"midnight contract compile {contract_path}")
    
    if result and result.returncode == 0:
        print("✅ Private vote contract compiled successfully!")
    else:
        print("❌ Compilation failed")
        return
    
    # Voting features
    print("\n🗳️  Voting features:")
    print("   • Anonymous vote casting")
    print("   • ZK proof of eligibility")
    print("   • Vote privacy preservation")
    print("   • Verifiable results")
    
    # Usage example
    print("\n📊 Usage example:")
    example_addr = "0x9988776655443322"
    
    print(f"   # Cast YES vote")
    print(f"   midnight contract call {example_addr} voteYes")
    print(f"   ")
    print(f"   # Cast NO vote")
    print(f"   midnight contract call {example_addr} voteNo")
    print(f"   ")
    print(f"   # Get results (without revealing individual votes)")
    print(f"   midnight contract query {example_addr} getResults")
    print(f"   # Output: {{\"yes\": 15, \"no\": 8, \"total\": 23}}")

def show_deployment_summary():
    """Show summary of all deployment examples"""
    print("\n" + "="*80)
    print("📊 CONTRACT DEPLOYMENT SUMMARY")
    print("="*80)
    
    contracts = [
        {
            "name": "Hello World",
            "file": "hello_world.compact",
            "complexity": "Beginner",
            "circuits": ["storeMessage", "getMessage"],
            "use_case": "Basic state management"
        },
        {
            "name": "Counter",
            "file": "counter.compact", 
            "complexity": "Intermediate",
            "circuits": ["increment", "getCount"],
            "use_case": "State persistence"
        },
        {
            "name": "Bulletin Board",
            "file": "bulletin_board.compact",
            "complexity": "Advanced", 
            "circuits": ["post", "getMessages"],
            "use_case": "Anonymous messaging"
        },
        {
            "name": "AI Inference",
            "file": "ai_inference.compact",
            "complexity": "Expert",
            "circuits": ["submitInferenceResult"],
            "use_case": "Private ML"
        },
        {
            "name": "Private Vote",
            "file": "private_vote.compact",
            "complexity": "Expert",
            "circuits": ["voteYes", "voteNo", "getResults"],
            "use_case": "Anonymous voting"
        }
    ]
    
    print("\n📋 Available Contracts:")
    for contract in contracts:
        print(f"\n🔹 {contract['name']}")
        print(f"   File: {contract['file']}")
        print(f"   Complexity: {contract['complexity']}")
        print(f"   Circuits: {', '.join(contract['circuits'])}")
        print(f"   Use Case: {contract['use_case']}")
    
    print("\n🚀 Deployment Commands:")
    print("   1. Compile: midnight contract compile contracts/<contract>.compact")
    print("   2. Deploy:  midnight contract deploy contracts/<contract>.compact --wallet <name> --profile <network>")
    print("   3. Call:    midnight contract call <address> <circuit> --args '<json>'")
    print("   4. Query:   midnight contract query <address> <method>")
    
    print("\n🌐 Network Options:")
    print("   • local:   Fast development (Docker required)")
    print("   • preprod: Testing with testnet tokens")
    print("   • mainnet: Production with real tokens")
    
    print("\n💡 Best Practices:")
    print("   ✅ Always compile before deploying")
    print("   ✅ Test on local network first")
    print("   ✅ Verify sufficient DUST balance")
    print("   ✅ Save contract addresses")
    print("   ✅ Monitor deployment transactions")

def main():
    """Run all contract deployment demonstrations"""
    print("🚀 MIDNIGHT CONTRACT DEPLOYMENT DEMONSTRATIONS")
    print("=" * 80)
    
    # Check prerequisites
    print("\n🔍 Checking prerequisites...")
    
    # Check if contracts exist
    contracts_dir = Path("contracts")
    if not contracts_dir.exists():
        print("❌ Contracts directory not found")
        return
    
    contract_files = list(contracts_dir.glob("*.compact"))
    print(f"✅ Found {len(contract_files)} contract files")
    
    # Check system status
    result = run_cli_command("midnight system status --profile local")
    if result and result.returncode == 0:
        print("✅ Local services are online")
    else:
        print("⚠️  Local services may not be available")
    
    # Run demonstrations
    demos = [
        ("Hello World Contract", demo_hello_world_deployment),
        ("Counter Contract", demo_counter_deployment),
        ("Bulletin Board Contract", demo_bulletin_board_deployment),
        ("AI Inference Contract", demo_ai_inference_deployment),
        ("Private Vote Contract", demo_private_vote_deployment),
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"❌ Error in {name}: {e}")
    
    # Show summary
    show_deployment_summary()
    
    print("\n" + "="*80)
    print("🎉 CONTRACT DEPLOYMENT DEMONSTRATIONS COMPLETE!")
    print("="*80)
    
    print("\n📚 Next Steps:")
    print("   1. Try deploying contracts to local network")
    print("   2. Interact with deployed contracts using CLI")
    print("   3. Monitor contract events and transactions")
    print("   4. Build applications using the Python SDK")
    print("   5. Deploy to preprod for testing")

if __name__ == "__main__":
    main()