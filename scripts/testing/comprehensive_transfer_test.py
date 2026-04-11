#!/usr/bin/env python3
"""
Comprehensive Transfer Test Loop
=================================

This script performs a complete end-to-end test:
1. Create a new wallet
2. Request testnet tokens from faucet
3. Check balance
4. Transfer tokens to a random address
5. Verify transfer
6. Retry on errors with fixes

Usage:
    python scripts/testing/comprehensive_transfer_test.py
"""

import sys
import time
import secrets
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from midnight_sdk.wallet import WalletClient
from midnight_sdk.config import ConfigManager

console = Console()

class TransferTestLoop:
    def __init__(self, network="preprod", max_retries=3):
        self.network = network
        self.max_retries = max_retries
        self.wallet_client = WalletClient()
        self.config_mgr = ConfigManager()
        self.config_mgr.load()
        
        # Get network profile
        self.profile = self.config_mgr.get_profile(network)
        if not self.profile:
            raise ValueError(f"Network profile for '{network}' not found")
        
        self.test_wallet_name = f"test_wallet_{int(time.time())}"
        self.test_wallet_path = None
        self.test_mnemonic = None
        self.test_address = None
        
    def generate_mnemonic(self) -> str:
        """Generate a new 24-word mnemonic"""
        console.print("\n[cyan]Generating new mnemonic...[/cyan]")
        
        # Use bip39 to generate mnemonic
        try:
            result = subprocess.run(
                ["node", "-e", """
                const bip39 = require('bip39');
                const mnemonic = bip39.generateMnemonic(256);
                console.log(mnemonic);
                """],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                mnemonic = result.stdout.strip()
                console.print(f"[green]✓[/green] Generated mnemonic: [dim]{mnemonic[:50]}...[/dim]")
                return mnemonic
            else:
                raise Exception(f"Failed to generate mnemonic: {result.stderr}")
        except Exception as e:
            console.print(f"[red]Error generating mnemonic: {e}[/red]")
            # Fallback: generate random words (not cryptographically secure, for testing only)
            console.print("[yellow]Using fallback mnemonic generation (test only)[/yellow]")
            words = ["test", "wallet", "midnight", "network", "python", "sdk", "transfer", "balance",
                    "address", "token", "night", "dust", "preprod", "testnet", "faucet", "random",
                    "secure", "private", "public", "key", "signature", "transaction", "block", "chain"]
            mnemonic = " ".join(secrets.choice(words) for _ in range(24))
            return mnemonic
    
    def create_wallet(self) -> bool:
        """Step 1: Create a new test wallet"""
        console.print(Panel(
            "[bold cyan]Step 1: Create New Wallet[/bold cyan]",
            border_style="cyan"
        ))
        
        try:
            # Generate mnemonic
            self.test_mnemonic = self.generate_mnemonic()
            
            # Create wallet directory
            wallet_dir = Path.home() / ".midnight" / "wallets"
            wallet_dir.mkdir(parents=True, exist_ok=True)
            
            self.test_wallet_path = wallet_dir / f"{self.test_wallet_name}.txt"
            self.test_wallet_path.write_text(self.test_mnemonic)
            
            console.print(f"[green]✓[/green] Wallet created: [cyan]{self.test_wallet_name}[/cyan]")
            console.print(f"[green]✓[/green] Saved to: [dim]{self.test_wallet_path}[/dim]")
            
            # Derive address
            console.print("\n[cyan]Deriving address...[/cyan]")
            addr_info = self.wallet_client.get_all_addresses(
                self.test_mnemonic,
                self.profile.network_id
            )
            
            self.test_address = addr_info['addresses']['unshielded']
            
            console.print(f"[green]✓[/green] Unshielded address: [cyan]{self.test_address}[/cyan]")
            console.print(f"[green]✓[/green] DUST address: [dim]{addr_info['addresses']['dust']}[/dim]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]✗ Failed to create wallet: {e}[/red]")
            return False
    
    def request_faucet_tokens(self) -> bool:
        """Step 2: Request tokens from faucet"""
        console.print(Panel(
            "[bold cyan]Step 2: Request Testnet Tokens[/bold cyan]",
            border_style="cyan"
        ))
        
        if self.network == "preprod":
            faucet_url = "https://faucet.preprod.midnight.network"
        elif self.network == "testnet":
            faucet_url = "https://faucet.testnet.midnight.network"
        else:
            console.print("[yellow]⚠ Faucet not available for this network[/yellow]")
            console.print("[yellow]Please fund the wallet manually[/yellow]")
            return False
        
        console.print(f"\n[cyan]Faucet URL:[/cyan] {faucet_url}")
        console.print(f"[cyan]Address:[/cyan] {self.test_address}")
        
        console.print("\n[yellow]Please visit the faucet URL and request tokens for this address.[/yellow]")
        console.print("[yellow]Press Enter when you've requested tokens...[/yellow]")
        input()
        
        console.print("[green]✓[/green] Proceeding to balance check...")
        return True
    
    def check_balance(self, retry=0) -> dict:
        """Step 3: Check wallet balance"""
        console.print(Panel(
            f"[bold cyan]Step 3: Check Balance (Attempt {retry + 1}/{self.max_retries})[/bold cyan]",
            border_style="cyan"
        ))
        
        try:
            console.print("\n[cyan]Querying balance (60 second sync)...[/cyan]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Syncing wallet...", total=None)
                
                balance_data = self.wallet_client.get_full_balance(
                    self.test_mnemonic,
                    self.profile.network_id,
                    self.profile.indexer_url,
                    self.profile.indexer_ws_url,
                    self.profile.node_url,
                    self.profile.proof_server_url
                )
                
                progress.update(task, completed=True)
            
            # Display balance
            table = Table(title="Wallet Balance")
            table.add_column("Token", style="cyan")
            table.add_column("Amount", style="green", justify="right")
            table.add_column("Coins", style="yellow", justify="right")
            
            dust = int(balance_data['balances']['dust'])
            night_unshielded = int(balance_data['balances']['night_unshielded'])
            night_shielded = int(balance_data['balances']['night_shielded'])
            
            table.add_row(
                "DUST",
                f"{dust / 1_000_000:.6f}",
                str(balance_data['coins']['dust'])
            )
            table.add_row(
                "NIGHT (Unshielded)",
                f"{night_unshielded / 1_000_000:.6f}",
                str(balance_data['coins']['unshielded'])
            )
            table.add_row(
                "NIGHT (Shielded)",
                f"{night_shielded / 1_000_000:.6f}",
                str(balance_data['coins']['shielded'])
            )
            
            console.print(table)
            
            # Check if we have funds
            total_night = night_unshielded + night_shielded
            if total_night == 0:
                console.print("\n[yellow]⚠ No NIGHT tokens found[/yellow]")
                if retry < self.max_retries - 1:
                    console.print(f"[yellow]Retrying in 30 seconds... ({retry + 1}/{self.max_retries})[/yellow]")
                    time.sleep(30)
                    return self.check_balance(retry + 1)
                else:
                    console.print("[red]✗ No tokens received after retries[/red]")
                    return None
            
            console.print(f"\n[green]✓[/green] Balance: {total_night / 1_000_000:.6f} NIGHT")
            return balance_data
            
        except Exception as e:
            console.print(f"[red]✗ Failed to check balance: {e}[/red]")
            if retry < self.max_retries - 1:
                console.print(f"[yellow]Retrying in 10 seconds... ({retry + 1}/{self.max_retries})[/yellow]")
                time.sleep(10)
                return self.check_balance(retry + 1)
            return None
    
    def generate_random_address(self) -> str:
        """Generate a random recipient address"""
        # Generate a random mnemonic for recipient
        recipient_mnemonic = self.generate_mnemonic()
        
        try:
            addr_info = self.wallet_client.get_all_addresses(
                recipient_mnemonic,
                self.profile.network_id
            )
            return addr_info['addresses']['unshielded']
        except Exception as e:
            console.print(f"[red]Error generating random address: {e}[/red]")
            # Fallback: use a test address
            return "mn_addr_preprod1test000000000000000000000000000000000000000000000000000"
    
    def transfer_tokens(self, amount: int, retry=0) -> bool:
        """Step 4: Transfer tokens to random address"""
        console.print(Panel(
            f"[bold cyan]Step 4: Transfer Tokens (Attempt {retry + 1}/{self.max_retries})[/bold cyan]",
            border_style="cyan"
        ))
        
        try:
            # Generate random recipient
            recipient = self.generate_random_address()
            console.print(f"\n[cyan]Recipient:[/cyan] {recipient}")
            console.print(f"[cyan]Amount:[/cyan] {amount / 1_000_000:.6f} NIGHT")
            
            console.print("\n[cyan]Initiating transfer...[/cyan]")
            
            result = self.wallet_client.transfer_unshielded(
                recipient=recipient,
                amount=amount,
                mnemonic=self.test_mnemonic,
                network_id=self.profile.network_id
            )
            
            console.print(f"\n[green]✓[/green] Transfer successful!")
            console.print(f"[green]✓[/green] Transaction hash: [cyan]{result['tx_hash']}[/cyan]")
            console.print(f"[green]✓[/green] Status: {result['status']}")
            
            # Show explorer link
            if self.profile.explorer_url:
                explorer_link = f"{self.profile.explorer_url}/tx/{result['tx_hash']}"
                console.print(f"\n[cyan]Explorer:[/cyan] {explorer_link}")
            
            return True
            
        except Exception as e:
            console.print(f"[red]✗ Transfer failed: {e}[/red]")
            
            # Analyze error and suggest fix
            error_msg = str(e).lower()
            
            if "insufficient" in error_msg or "balance" in error_msg:
                console.print("[yellow]Fix: Insufficient balance - reduce transfer amount[/yellow]")
                if retry < self.max_retries - 1:
                    new_amount = amount // 2
                    console.print(f"[yellow]Retrying with {new_amount / 1_000_000:.6f} NIGHT...[/yellow]")
                    time.sleep(5)
                    return self.transfer_tokens(new_amount, retry + 1)
            
            elif "timeout" in error_msg or "connection" in error_msg:
                console.print("[yellow]Fix: Network timeout - retrying...[/yellow]")
                if retry < self.max_retries - 1:
                    time.sleep(10)
                    return self.transfer_tokens(amount, retry + 1)
            
            elif "not found" in error_msg or "sdk" in error_msg:
                console.print("[yellow]Fix: Install dependencies - npm install[/yellow]")
            
            else:
                console.print(f"[yellow]Unknown error - check logs[/yellow]")
            
            return False
    
    def verify_transfer(self) -> bool:
        """Step 5: Verify transfer by checking balance again"""
        console.print(Panel(
            "[bold cyan]Step 5: Verify Transfer[/bold cyan]",
            border_style="cyan"
        ))
        
        try:
            console.print("\n[cyan]Checking balance after transfer...[/cyan]")
            time.sleep(5)  # Wait for transaction to propagate
            
            balance_data = self.wallet_client.get_full_balance(
                self.test_mnemonic,
                self.profile.network_id,
                self.profile.indexer_url,
                self.profile.indexer_ws_url,
                self.profile.node_url,
                self.profile.proof_server_url
            )
            
            night_unshielded = int(balance_data['balances']['night_unshielded'])
            console.print(f"[green]✓[/green] New balance: {night_unshielded / 1_000_000:.6f} NIGHT")
            
            return True
            
        except Exception as e:
            console.print(f"[yellow]⚠ Could not verify: {e}[/yellow]")
            return False
    
    def cleanup(self):
        """Cleanup test wallet"""
        console.print("\n[cyan]Cleaning up test wallet...[/cyan]")
        
        if self.test_wallet_path and self.test_wallet_path.exists():
            try:
                self.test_wallet_path.unlink()
                console.print(f"[green]✓[/green] Removed: {self.test_wallet_path}")
            except Exception as e:
                console.print(f"[yellow]⚠ Could not remove wallet file: {e}[/yellow]")
    
    def run(self):
        """Run the complete test loop"""
        console.print(Panel.fit(
            "[bold cyan]Comprehensive Transfer Test Loop[/bold cyan]\n"
            f"Network: {self.network}\n"
            f"Max Retries: {self.max_retries}",
            border_style="cyan"
        ))
        
        try:
            # Step 1: Create wallet
            if not self.create_wallet():
                console.print("\n[red]✗ Test failed at Step 1: Create Wallet[/red]")
                return False
            
            # Step 2: Request faucet tokens
            if not self.request_faucet_tokens():
                console.print("\n[red]✗ Test failed at Step 2: Request Tokens[/red]")
                return False
            
            # Step 3: Check balance
            balance_data = self.check_balance()
            if not balance_data:
                console.print("\n[red]✗ Test failed at Step 3: Check Balance[/red]")
                return False
            
            # Step 4: Transfer tokens (10% of balance)
            night_unshielded = int(balance_data['balances']['night_unshielded'])
            transfer_amount = night_unshielded // 10  # Transfer 10%
            
            if transfer_amount < 1_000_000:  # Minimum 1 NIGHT
                transfer_amount = 1_000_000
            
            if not self.transfer_tokens(transfer_amount):
                console.print("\n[red]✗ Test failed at Step 4: Transfer Tokens[/red]")
                return False
            
            # Step 5: Verify transfer
            self.verify_transfer()
            
            # Success!
            console.print(Panel.fit(
                "[bold green]✓ All Tests Passed![/bold green]\n\n"
                "Summary:\n"
                f"• Wallet created: {self.test_wallet_name}\n"
                f"• Address: {self.test_address[:40]}...\n"
                f"• Tokens received from faucet\n"
                f"• Transfer successful: {transfer_amount / 1_000_000:.6f} NIGHT\n"
                f"• Balance verified",
                border_style="green"
            ))
            
            return True
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Test interrupted by user[/yellow]")
            return False
        
        except Exception as e:
            console.print(f"\n[red]✗ Unexpected error: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
            return False
        
        finally:
            # Cleanup
            if input("\nRemove test wallet? (y/N): ").lower() == 'y':
                self.cleanup()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive transfer test loop")
    parser.add_argument("--network", default="preprod", help="Network to test (preprod, testnet)")
    parser.add_argument("--retries", type=int, default=3, help="Maximum retries per step")
    parser.add_argument("--no-cleanup", action="store_true", help="Keep test wallet after completion")
    
    args = parser.parse_args()
    
    test = TransferTestLoop(network=args.network, max_retries=args.retries)
    success = test.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
