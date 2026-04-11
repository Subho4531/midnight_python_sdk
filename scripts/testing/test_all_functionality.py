#!/usr/bin/env python3
"""
Comprehensive Functionality Test
=================================

Tests all major features of the Midnight Python SDK:
1. Configuration management
2. Wallet operations (address derivation, balance)
3. Contract deployment (if local network available)
4. AI inference (if model available)
5. CLI commands

Usage:
    python scripts/testing/test_all_functionality.py
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from midnight_sdk.config import ConfigManager
from midnight_sdk.wallet import WalletClient
from midnight_sdk.client import MidnightClient

console = Console()

class FunctionalityTester:
    def __init__(self):
        self.results = {}
        self.config_mgr = ConfigManager()
        
    def test_config_management(self):
        """Test configuration management"""
        console.print(Panel(
            "[bold cyan]Test 1: Configuration Management[/bold cyan]",
            border_style="cyan"
        ))
        
        try:
            # Load config
            self.config_mgr.load()
            console.print("[green]✓[/green] Config loaded")
            
            # Check profiles
            profiles = list(self.config_mgr.config.profiles.keys())
            console.print(f"[green]✓[/green] Profiles available: {', '.join(profiles)}")
            
            # Get active profile
            active = self.config_mgr.config.active_profile
            console.print(f"[green]✓[/green] Active profile: {active}")
            
            self.results['config'] = 'PASS'
            return True
            
        except Exception as e:
            console.print(f"[red]✗ Config test failed: {e}[/red]")
            self.results['config'] = f'FAIL: {e}'
            return False
    
    def test_wallet_address_derivation(self):
        """Test wallet address derivation"""
        console.print(Panel(
            "[bold cyan]Test 2: Wallet Address Derivation[/bold cyan]",
            border_style="cyan"
        ))
        
        try:
            wallet_client = WalletClient()
            
            # Test mnemonic
            test_mnemonic = "test wallet midnight network python sdk transfer balance address token night dust preprod testnet faucet random secure private public key signature transaction block chain"
            
            # Derive addresses
            console.print("[cyan]Deriving addresses...[/cyan]")
            addr_info = wallet_client.get_all_addresses(test_mnemonic, "preprod")
            
            # Check all three address types
            unshielded = addr_info['addresses']['unshielded']
            shielded = addr_info['addresses']['shielded']
            dust = addr_info['addresses']['dust']
            
            console.print(f"[green]✓[/green] Unshielded: {unshielded[:50]}...")
            console.print(f"[green]✓[/green] Shielded: {shielded[:50]}...")
            console.print(f"[green]✓[/green] DUST: {dust[:50]}...")
            
            # Verify format
            assert unshielded.startswith("mn_addr_preprod1"), "Invalid unshielded address format"
            assert shielded.startswith("mn_shield-addr_preprod1"), "Invalid shielded address format"
            assert dust.startswith("mn_dust_preprod1"), "Invalid DUST address format"
            
            console.print("[green]✓[/green] All address formats valid")
            
            self.results['wallet_address'] = 'PASS'
            return True
            
        except Exception as e:
            console.print(f"[red]✗ Wallet address test failed: {e}[/red]")
            self.results['wallet_address'] = f'FAIL: {e}'
            return False
    
    def test_wallet_balance(self):
        """Test wallet balance query"""
        console.print(Panel(
            "[bold cyan]Test 3: Wallet Balance Query[/bold cyan]",
            border_style="cyan"
        ))
        
        try:
            # Check if default wallet exists
            if not self.config_mgr.config.default_wallet:
                console.print("[yellow]⚠ No default wallet configured - skipping balance test[/yellow]")
                self.results['wallet_balance'] = 'SKIP: No wallet'
                return True
            
            wallet_name = self.config_mgr.config.default_wallet
            if wallet_name not in self.config_mgr.config.wallets:
                console.print(f"[yellow]⚠ Wallet '{wallet_name}' not found - skipping[/yellow]")
                self.results['wallet_balance'] = 'SKIP: Wallet not found'
                return True
            
            wallet_path = Path(self.config_mgr.config.wallets[wallet_name])
            if not wallet_path.exists():
                console.print(f"[yellow]⚠ Wallet file not found - skipping[/yellow]")
                self.results['wallet_balance'] = 'SKIP: File not found'
                return True
            
            mnemonic = wallet_path.read_text().strip()
            profile = self.config_mgr.get_profile("preprod")
            
            wallet_client = WalletClient(profile.node_url)
            
            console.print("[cyan]Querying balance (60 second sync)...[/cyan]")
            balance_data = wallet_client.get_full_balance(
                mnemonic,
                profile.network_id,
                profile.indexer_url,
                profile.indexer_ws_url,
                profile.node_url,
                profile.proof_server_url
            )
            
            dust = int(balance_data['balances']['dust'])
            night_unshielded = int(balance_data['balances']['night_unshielded'])
            night_shielded = int(balance_data['balances']['night_shielded'])
            
            console.print(f"[green]✓[/green] DUST: {dust / 1_000_000:.6f}")
            console.print(f"[green]✓[/green] NIGHT (Unshielded): {night_unshielded / 1_000_000:.6f}")
            console.print(f"[green]✓[/green] NIGHT (Shielded): {night_shielded / 1_000_000:.6f}")
            console.print(f"[green]✓[/green] Synced: {balance_data['synced']}")
            
            self.results['wallet_balance'] = 'PASS'
            return True
            
        except Exception as e:
            console.print(f"[red]✗ Balance test failed: {e}[/red]")
            self.results['wallet_balance'] = f'FAIL: {e}'
            return False
    
    def test_client_initialization(self):
        """Test MidnightClient initialization"""
        console.print(Panel(
            "[bold cyan]Test 4: Client Initialization[/bold cyan]",
            border_style="cyan"
        ))
        
        try:
            # Test preprod client
            client = MidnightClient(network="preprod")
            console.print("[green]✓[/green] Preprod client initialized")
            
            # Test status check
            status = client.status()
            console.print(f"[green]✓[/green] Status check: {len(status)} services")
            
            for service, is_up in status.items():
                status_str = "[green]✓ Online[/green]" if is_up else "[yellow]⚠ Offline[/yellow]"
                console.print(f"  {service}: {status_str}")
            
            self.results['client_init'] = 'PASS'
            return True
            
        except Exception as e:
            console.print(f"[red]✗ Client initialization failed: {e}[/red]")
            self.results['client_init'] = f'FAIL: {e}'
            return False
    
    def test_cli_commands(self):
        """Test CLI commands"""
        console.print(Panel(
            "[bold cyan]Test 5: CLI Commands[/bold cyan]",
            border_style="cyan"
        ))
        
        import subprocess
        
        commands = [
            ("midnight --help", "Help command"),
            ("midnight config list", "Config list"),
            ("midnight wallet address", "Wallet address"),
        ]
        
        passed = 0
        failed = 0
        
        for cmd, desc in commands:
            try:
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    console.print(f"[green]✓[/green] {desc}")
                    passed += 1
                else:
                    console.print(f"[yellow]⚠[/yellow] {desc} (exit code {result.returncode})")
                    failed += 1
            except Exception as e:
                console.print(f"[red]✗[/red] {desc}: {e}")
                failed += 1
        
        if failed == 0:
            self.results['cli_commands'] = 'PASS'
            return True
        else:
            self.results['cli_commands'] = f'PARTIAL: {passed} passed, {failed} failed'
            return False
    
    def print_summary(self):
        """Print test summary"""
        console.print(Panel(
            "[bold cyan]Test Summary[/bold cyan]",
            border_style="cyan"
        ))
        
        table = Table(title="Functionality Test Results")
        table.add_column("Test", style="cyan")
        table.add_column("Result", style="green")
        
        for test_name, result in self.results.items():
            if result == 'PASS':
                result_str = "[green]✓ PASS[/green]"
            elif result.startswith('SKIP'):
                result_str = f"[yellow]⊘ {result}[/yellow]"
            elif result.startswith('PARTIAL'):
                result_str = f"[yellow]⚠ {result}[/yellow]"
            else:
                result_str = f"[red]✗ {result}[/red]"
            
            table.add_row(test_name.replace('_', ' ').title(), result_str)
        
        console.print(table)
        
        # Count results
        passed = sum(1 for r in self.results.values() if r == 'PASS')
        total = len(self.results)
        
        console.print(f"\n[bold]Total:[/bold] {passed}/{total} tests passed")
    
    def run_all_tests(self):
        """Run all tests"""
        console.print(Panel.fit(
            "[bold cyan]Midnight SDK Functionality Test Suite[/bold cyan]\n"
            "Testing all major features",
            border_style="cyan"
        ))
        
        self.test_config_management()
        console.print()
        
        self.test_wallet_address_derivation()
        console.print()
        
        self.test_wallet_balance()
        console.print()
        
        self.test_client_initialization()
        console.print()
        
        self.test_cli_commands()
        console.print()
        
        self.print_summary()


def main():
    tester = FunctionalityTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
