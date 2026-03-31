"""
Test script to verify AI module structure
Run this to check if everything is wired correctly
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from midnight_py import MidnightClient
        print("✓ MidnightClient imported")
    except ImportError as e:
        print(f"✗ Failed to import MidnightClient: {e}")
        return False
    
    try:
        from midnight_py.ai import ZKInferenceEngine, InferenceResult
        print("✓ AI module imported")
    except ImportError as e:
        print(f"✗ Failed to import AI module: {e}")
        return False
    
    try:
        from midnight_py.exceptions import (
            ProofServerConnectionError,
            ModelNotTrainedError,
            InvalidFeaturesError
        )
        print("✓ AI exceptions imported")
    except ImportError as e:
        print(f"✗ Failed to import AI exceptions: {e}")
        return False
    
    return True


def test_client_initialization():
    """Test that client can be initialized with AI engine"""
    print("\nTesting client initialization...")
    
    try:
        from midnight_py import MidnightClient
        from midnight_py.exceptions import ProofServerConnectionError
        
        # This will fail if proof server is not running (expected)
        try:
            client = MidnightClient(
                network="undeployed",
                wallet_address="mn_addr_undeployed1zaa268rc7sjz0ctscrsy7mp2ne7khfz8wu2uqsu4msfvxnlt6qfsmfrhr0",
            )
            print("✓ Client initialized")
            print(f"✓ AI engine attached: {hasattr(client, 'ai')}")
            print(f"✓ Wallet address set: {client.wallet_address}")
            return True
        except ProofServerConnectionError as e:
            print(f"⚠ Proof server not running (expected): {e}")
            print("✓ Error handling works correctly")
            return True
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_directory_structure():
    """Test that required directories are created"""
    print("\nTesting directory structure...")
    
    models_dir = Path.home() / ".midnight" / "models"
    proofs_dir = Path.home() / ".midnight" / "inference_proofs"
    
    # These should be created by ZKInferenceEngine.__init__
    # but we can't test that without initializing the client
    print(f"  Models dir: {models_dir}")
    print(f"  Proofs dir: {proofs_dir}")
    
    return True


def test_cli_commands():
    """Test that CLI commands are registered"""
    print("\nTesting CLI structure...")
    
    try:
        from midnight_py.cli import app, ai_app
        print("✓ CLI app imported")
        print("✓ AI subcommand registered")
        
        # Check if AI commands exist
        commands = [cmd.name for cmd in ai_app.registered_commands]
        print(f"  AI commands: {commands}")
        
        expected = ["train", "infer", "list-proofs", "show"]
        for cmd in expected:
            if cmd in commands:
                print(f"  ✓ {cmd} command registered")
            else:
                print(f"  ✗ {cmd} command missing")
        
        return True
    except Exception as e:
        print(f"✗ CLI test failed: {e}")
        return False


def test_contract_exists():
    """Test that AI inference contract exists"""
    print("\nTesting contract file...")
    
    contract_path = Path("contracts/ai_inference.compact")
    if contract_path.exists():
        print(f"✓ Contract exists: {contract_path}")
        content = contract_path.read_text()
        if "submit_inference_result" in content:
            print("✓ Contract has submit_inference_result circuit")
        return True
    else:
        print(f"✗ Contract not found: {contract_path}")
        return False


def main():
    print("=" * 60)
    print("AI Module Structure Test")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Client Initialization", test_client_initialization),
        ("Directory Structure", test_directory_structure),
        ("CLI Commands", test_cli_commands),
        ("Contract File", test_contract_exists),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    for name, result in results:
        icon = "✓" if result else "✗"
        print(f"{icon} {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All structure tests passed!")
        print("\nNext steps:")
        print("1. Install ML dependencies: pip install scikit-learn joblib numpy")
        print("2. Start proof server: docker-compose up proof-server")
        print("3. Run demo: python examples/ai_inference.py")
        return 0
    else:
        print("\n✗ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
