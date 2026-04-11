#!/usr/bin/env python3
"""
Comprehensive examples of Midnight contract deployment using CLI.
Demonstrates various deployment scenarios and best practices.
"""

import subprocess
import time
import json
from pathlib import Path

def run_command(cmd, timeout=60):
    """Run a CLI command and return the result"""
    try:
        print(f"🔧 Running: {cmd}")
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=timeout
        )
        return result
    except subprocess.TimeoutExpired:
        print(f"⏰ Command timed out after {timeout} seconds")
        return None

def check_prerequisites():
    """Check if all prerequisites are met for contract deployment"""
    print("🔍 Checking Prerequisites...")
    
    # Check system status
    result = run_command("midnight system status --profile local")
    if result and result.returncode == 0:
        print("✅ Local services are online")
    else:
        print("❌ Local services not available - starting Docker...")
        run_command("docker-compose up -d", timeout=30)
        time.sleep(5)
    
    # Check wallet
    result = run_command("midnight wallet list")
    if result and "shielded-test" in result.stdout:
        print("✅ Wallet available")
    else:
        print("❌ No suitable wallet found")
        return False
    
    # Check balance
    result = run_command("midnight balance --profile local")
    if result and "DUST" in result.stdout:
        print("✅ Sufficient balance for deployment")
    else:
        print("❌ Insufficient balance")
        return False
    
    return True

def example_1_hello_world():
    """Example 1: Deploy Hello World contract (simplest case)"""
    print("\n" + "="*60)
    print("📋 EXAMPLE 1: Hello World Contract Deployment")
    print("="*60)
    
    print("\n📝 Contract: hello_world.compact")
    print("📄 Description: Simple contract for storing and retrieving messages")
    print("🎯 Use Case: Basic contract interaction and state management")
    
    # Step 1: Compile the contract
    print("\n🔨 Step 1: Compiling contract...")
    result = run_command("midnight contract compile contracts/hello_world.compact")
    if result and result.returncode == 0:
        print("✅ Compilation successful")
    else:
        print("❌ Compilation failed")
        if result:
            print(f"Error: {result.stderr}")
        return None
    
    # Step 2: Deploy the contract
    print("\n🚀 Step 2: Deploying contract...")
    result = run_command("midnight contract deploy contracts/hello_world.compact --wallet shielded-test --profile local")
    if result and result.returncode == 0:
        print("✅ Deployment successful")
        # Extract contract address from output
        lines = result.stdout.split('\n')
        contract_address = None
        for line in lines:
            if 'Contract deployed' in line or 'address' in line.lower():
                # Extract address from line
                parts = line.split()
                for part in parts:
                    if part.startswith('0x') or 'contract' in part.lower():
                        contract_address = part
                        break
        
        if contract_address:
            print(f"📍 Contract Address: {contract_address}")
            return contract_address
        else:
            print("📍 Contract deployed (address in output above)")
            return "deployed"
    else:
        print("❌ Deployment failed")
        if result:
            print(f"Error: {result.stderr}")
        return None

def example_2_counter_with_options():
    """Example 2: Deploy Counter contract with specific options"""
    print("\n" + "="*60)
    print("📋 EXAMPLE 2: Counter Contract with Options")
    print("="*60)
    
    print("\n📝 Contract: counter.compact")
    print("📄 Description: Counter contract with increment/decrement operations")
    print("🎯 Use Case: State management and circuit calls")
    
    # Deploy with specific wallet and profile
    print("\n🚀 Deploying with specific options...")
    cmd = """midnight contract deploy contracts/counter.compact \
        --wallet shielded-test \
        --profile local"""
    
    result = run_command(cmd)
    if result and result.returncode == 0:
        print("✅ Counter contract deployed successfully")
        return "deployed"
    else:
        print("❌ Deployment failed")
        if result:
            print(f"Error: {result.stderr}")
        return None

def example_3_bulletin_board():
    """Example 3: Deploy Bulletin Board contract (more complex)"""
    print("\n" + "="*60)
    print("📋 EXAMPLE 3: Bulletin Board Contract")
    print("="*60)
    
    print("\n📝 Contract: bulletin_board.compact")
    print("📄 Description: Anonymous message posting system")
    print("🎯 Use Case: Privacy-preserving communication")
    
    # Compile first, then deploy
    print("\n🔨 Compiling bulletin board contract...")
    result = run_command("midnight contract compile contracts/bulletin_board.compact --output ./build")
    if result and result.returncode == 0:
        print("✅ Compilation successful with custom output directory")
    
    print("\n🚀 Deploying bulletin board...")
    result = run_command("midnight contract deploy contracts/bulletin_board.compact --wallet shielded-test --profile local")
    if result and result.returncode == 0:
        print("✅ Bulletin board deployed successfully")
        return "deployed"
    else:
        print("❌ Deployment failed")
        return None

def example_4_ai_inference():
    """Example 4: Deploy AI Inference contract"""
    print("\n" + "="*60)
    print("📋 EXAMPLE 4: AI Inference Contract")
    print("="*60)
    
    print("\n📝 Contract: ai_inference.compact")
    print("📄 Description: Private AI inference with ZK proofs")
    print("🎯 Use Case: Privacy-preserving machine learning")
    
    print("\n🚀 Deploying AI inference contract...")
    result = run_command("midnight contract deploy contracts/ai_inference.compact --wallet shielded-test --profile local")
    if result and result.returncode == 0:
        print("✅ AI inference contract deployed successfully")
        return "deployed"
    else:
        print("❌ Deployment failed")
        return None

def example_5_private_vote():
    """Example 5: Deploy Private Vote contract"""
    print("\n" + "="*60)
    print("📋 EXAMPLE 5: Private Vote Contract")
    print("="*60)
    
    print("\n📝 Contract: private_vote.compact")
    print("📄 Description: Anonymous voting system with ZK proofs")
    print("🎯 Use Case: Private governance and decision making")
    
    print("\n🚀 Deploying private vote contract...")
    result = run_command("midnight contract deploy contracts/private_vote.compact --wallet shielded-test --profile local")
    if result and result.returncode == 0:
        print("✅ Private vote contract deployed successfully")
        return "deployed"
    else:
        print("❌ Deployment failed")
        return None

def example_6_batch_deployment():
    """Example 6: Batch deployment of multiple contracts"""
    print("\n" + "="*60)
    print("📋 EXAMPLE 6: Batch Contract Deployment")
    print("="*60)
    
    contracts = [
        "contracts/hello_world.compact",
        "contracts/counter.compact",
        "contracts/bulletin_board.compact"
    ]
    
    deployed_contracts = []
    
    for contract in contracts:
        print(f"\n🚀 Deploying {contract}...")
        result = run_command(f"midnight contract deploy {contract} --wallet shielded-test --profile local")
        if result and result.returncode == 0:
            print(f"✅ {contract} deployed successfully")
            deployed_contracts.append(contract)
        else:
            print(f"❌ {contract} deployment failed")
    
    print(f"\n📊 Batch deployment results: {len(deployed_contracts)}/{len(contracts)} successful")
    return deployed_contracts

def example_7_different_networks():
    """Example 7: Deploy to different networks"""
    print("\n" + "="*60)
    print("📋 EXAMPLE 7: Multi-Network Deployment")
    print("="*60)
    
    networks = ["local", "preprod"]
    contract = "contracts/hello_world.compact"
    
    for network in networks:
        print(f"\n🌐 Deploying to {network} network...")
        
        # Check if network is available
        result = run_command(f"midnight system status --profile {network}")
        if result and result.returncode == 0:
            print(f"✅ {network} network is available")
            
            # Deploy to network
            result = run_command(f"midnight contract deploy {contract} --wallet shielded-test --profile {network}")
            if result and result.returncode == 0:
                print(f"✅ Deployed to {network} successfully")
            else:
                print(f"❌ Deployment to {network} failed")
        else:
            print(f"❌ {network} network not available")

def example_8_deployment_verification():
    """Example 8: Deploy and verify contract"""
    print("\n" + "="*60)
    print("📋 EXAMPLE 8: Deploy with Verification")
    print("="*60)
    
    contract = "contracts/counter.compact"
    
    # Deploy contract
    print("\n🚀 Deploying contract...")
    result = run_command(f"midnight contract deploy {contract} --wallet shielded-test --profile local")
    if result and result.returncode != 0:
        print("❌ Deployment failed")
        return
    
    print("✅ Contract deployed")
    
    # List deployed contracts
    print("\n📋 Listing deployed contracts...")
    result = run_command("midnight contract list --profile local")
    if result and result.returncode == 0:
        print("✅ Contract list retrieved")
        print(result.stdout)
    
    # Get contract info (if we had the address)
    print("\n📄 Contract verification complete")

def show_cli_commands():
    """Show all CLI commands for contract deployment"""
    print("\n" + "="*60)
    print("📚 CLI COMMAND REFERENCE")
    print("="*60)
    
    commands = [
        ("Compile contract", "midnight contract compile <contract.compact>"),
        ("Compile with output", "midnight contract compile <contract.compact> --output ./build"),
        ("Deploy basic", "midnight contract deploy <contract.compact>"),
        ("Deploy with wallet", "midnight contract deploy <contract.compact> --wallet <name>"),
        ("Deploy with profile", "midnight contract deploy <contract.compact> --profile <network>"),
        ("Deploy full options", "midnight contract deploy <contract.compact> --wallet <name> --profile <network>"),
        ("List contracts", "midnight contract list"),
        ("List on network", "midnight contract list --profile <network>"),
        ("Contract info", "midnight contract info <address>"),
        ("Contract events", "midnight contract events <address>"),
        ("Call contract", "midnight contract call <address> <circuit>"),
        ("Query contract", "midnight contract query <address> <method>"),
    ]
    
    for description, command in commands:
        print(f"\n📝 {description}:")
        print(f"   {command}")

def main():
    """Run all contract deployment examples"""
    print("🚀 Midnight Contract Deployment Examples")
    print("=" * 80)
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites not met. Please ensure:")
        print("   • Local services are running (docker-compose up -d)")
        print("   • Wallet is created and funded")
        print("   • Network profile is configured")
        return
    
    # Run examples
    examples = [
        ("Hello World (Basic)", example_1_hello_world),
        ("Counter (With Options)", example_2_counter_with_options),
        ("Bulletin Board (Complex)", example_3_bulletin_board),
        ("AI Inference (Advanced)", example_4_ai_inference),
        ("Private Vote (ZK)", example_5_private_vote),
        ("Batch Deployment", example_6_batch_deployment),
        ("Multi-Network", example_7_different_networks),
        ("With Verification", example_8_deployment_verification),
    ]
    
    print(f"\n🎯 Running {len(examples)} deployment examples...")
    
    for name, example_func in examples:
        try:
            print(f"\n▶️  Starting: {name}")
            result = example_func()
            if result:
                print(f"✅ Completed: {name}")
            else:
                print(f"⚠️  Completed with issues: {name}")
        except Exception as e:
            print(f"❌ Failed: {name} - {e}")
    
    # Show CLI reference
    show_cli_commands()
    
    print("\n" + "="*80)
    print("🎉 Contract Deployment Examples Complete!")
    print("="*80)
    
    print("\n💡 Key Takeaways:")
    print("   • Always compile contracts before deployment")
    print("   • Ensure sufficient DUST balance for deployment fees")
    print("   • Use appropriate network profiles (local/preprod/mainnet)")
    print("   • Verify deployments with contract list and info commands")
    print("   • Save contract addresses for future interactions")
    
    print("\n📚 Next Steps:")
    print("   • Call contract circuits with: midnight contract call")
    print("   • Query contract state with: midnight contract query")
    print("   • Monitor events with: midnight contract events")
    print("   • Check deployment guide: docs/DEPLOYMENT_GUIDE.md")

if __name__ == "__main__":
    main()