#!/usr/bin/env python3
"""
Quick Transfer Test - Test transfer with existing wallet
=========================================================

This script tests the transfer functionality using your existing wallet
that already has funds.

Usage:
    python scripts/testing/quick_transfer_test.py
"""

import sys
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from midnight_sdk.wallet import WalletClient
from midnight_sdk.config import ConfigManager

console = Console()


def generate_random_address(wallet_client, network_id):
    """Generate a random recipient address"""
    import secrets
    
    # Generate a random mnemonic for recipient
    words = ["test", "wallet", "midnight", "network", "python", "sdk", "transfer", "balance",
            "address", "token", "night", "dust", "preprod", "testnet", "faucet", "random",
            "secure", "private", "public", "key", "signature", "transaction", "block", "chain"]
    recipient_mnemonic = " ".join(secrets.choice(words) for _ in range(24))
    
    try:
        addr_info = wallet_client.get_all_addresses(recipient_mnemonic, network_id)
        return addr_info['addresses']['unshielded']
    except Exception as e:
        console.print(f"[red]Error generating random address: {e}[/red]")
        # Fallback: use a test address
        return "mn_addr_preprod1test000000000000000000000000000000000000000000000000000"


def main():
    console.print(Panel.fit(
        "[bold cyan]Quick Transfer Test[/bold cyan]\n"
        "Testing transfer with existing wallet",
        border_style="cyan"
    ))
    
    # Load config
    config_mgr = ConfigManager()
    config_mgr.load()
    
    # Get active profile
    profile = config_mgr.get_profile("preprod")
    
    # Get default wallet
    if not config_mgr.config.default_wallet:
        console.print("[red]No default wallet set[/red]")
        console.print("Use: midnight wallet new <name>")
        sys.exit(1)
    
    wallet_name = config_mgr.config.default_wallet
    if wallet_name not in config_mgr.config.wallets:
        console.print(f"[red]Wallet '{wallet_name}' not found[/red]")
        sys.exit(1)
    
    wallet_path = Path(config_mgr.config.wallets[wallet_name])
    if not wallet_path.exists():
        console.print(f"[red]Wallet file not found: {wallet_path}[/red]")
        sys.exit(1)
    
    mnemonic = wallet_path.read_text().strip()
    
    console.print(f"\n[cyan]Using wallet:[/cyan] {wallet_name}")
    console.print(f"[cyan]Network:[/cyan] {profile.name} ({profile.network_id})")
    
    # Initialize wallet client
    wallet_client = WalletClient(profile.node_url)
    
    # Step 1: Check current balance
    console.print(Panel(
        "[bold cyan]Step 1: Check Current Balance[/bold cyan]",
        border_style="cyan"
    ))
    
    try:
        with console.status("[cyan]Querying balance...", spinner="dots"):
            balance_data = wallet_client.get_full_balance(
                mnemonic,
                profile.network_id,
                profile.indexer_url,
                profile.indexer_ws_url,
                profile.node_url,
                profile.proof_server_url
            )
        
        # Display balance
        table = Table(title="Current Balance")
        table.add_column("Token", style="cyan")
        table.add_column("Amount", style="green", justify="right")
        
        dust = int(balance_data['balances']['dust'])
        night_unshielded = int(balance_data['balances']['night_unshielded'])
        night_shielded = int(balance_data['balances']['night_shielded'])
        
        table.add_row("DUST", f"{dust / 1_000_000:.6f}")
        table.add_row("NIGHT (Unshielded)", f"{night_unshielded / 1_000_000:.6f}")
        table.add_row("NIGHT (Shielded)", f"{night_shielded / 1_000_000:.6f}")
        
        console.print(table)
        
        if night_unshielded == 0:
            console.print("\n[red]No unshielded NIGHT available for transfer[/red]")
            sys.exit(1)
        
        console.print(f"\n[green]✓[/green] Balance: {night_unshielded / 1_000_000:.6f} NIGHT (Unshielded)")
        
    except Exception as e:
        console.print(f"[red]Error checking balance: {e}[/red]")
        sys.exit(1)
    
    # Step 2: Generate random recipient
    console.print(Panel(
        "[bold cyan]Step 2: Generate Random Recipient[/bold cyan]",
        border_style="cyan"
    ))
    
    recipient = generate_random_address(wallet_client, profile.network_id)
    console.print(f"[green]✓[/green] Recipient: [cyan]{recipient}[/cyan]")
    
    # Step 3: Transfer tokens
    console.print(Panel(
        "[bold cyan]Step 3: Transfer Tokens[/bold cyan]",
        border_style="cyan"
    ))
    
    # Transfer 10% of balance or 1 NIGHT minimum
    transfer_amount = max(night_unshielded // 10, 1_000_000)
    console.print(f"\n[cyan]Amount:[/cyan] {transfer_amount / 1_000_000:.6f} NIGHT")
    console.print(f"[cyan]Recipient:[/cyan] {recipient[:50]}...")
    
    # Confirm
    confirm = input("\nProceed with transfer? (y/N): ")
    if confirm.lower() != 'y':
        console.print("[yellow]Transfer cancelled[/yellow]")
        sys.exit(0)
    
    try:
        with console.status("[cyan]Initiating transfer...", spinner="dots"):
            result = wallet_client.transfer_unshielded(
                recipient=recipient,
                amount=transfer_amount,
                mnemonic=mnemonic,
                network_id=profile.network_id
            )
        
        console.print(f"\n[green]✓[/green] Transfer successful!")
        console.print(f"[green]✓[/green] Transaction hash: [cyan]{result['tx_hash']}[/cyan]")
        console.print(f"[green]✓[/green] Status: {result['status']}")
        
        # Show explorer link
        if profile.explorer_url:
            explorer_link = f"{profile.explorer_url}/tx/{result['tx_hash']}"
            console.print(f"\n[cyan]Explorer:[/cyan] {explorer_link}")
        
    except Exception as e:
        console.print(f"\n[red]✗ Transfer failed: {e}[/red]")
        sys.exit(1)
    
    # Step 4: Verify transfer
    console.print(Panel(
        "[bold cyan]Step 4: Verify Transfer[/bold cyan]",
        border_style="cyan"
    ))
    
    console.print("\n[cyan]Waiting 10 seconds for transaction to propagate...[/cyan]")
    time.sleep(10)
    
    try:
        with console.status("[cyan]Checking new balance...", spinner="dots"):
            new_balance_data = wallet_client.get_full_balance(
                mnemonic,
                profile.network_id,
                profile.indexer_url,
                profile.indexer_ws_url,
                profile.node_url,
                profile.proof_server_url
            )
        
        new_night_unshielded = int(new_balance_data['balances']['night_unshielded'])
        
        # Display comparison
        table = Table(title="Balance Comparison")
        table.add_column("", style="cyan")
        table.add_column("Before", style="yellow", justify="right")
        table.add_column("After", style="green", justify="right")
        table.add_column("Change", style="red", justify="right")
        
        change = new_night_unshielded - night_unshielded
        
        table.add_row(
            "NIGHT (Unshielded)",
            f"{night_unshielded / 1_000_000:.6f}",
            f"{new_night_unshielded / 1_000_000:.6f}",
            f"{change / 1_000_000:.6f}"
        )
        
        console.print(table)
        
        if change < 0:
            console.print(f"\n[green]✓[/green] Balance decreased by {abs(change) / 1_000_000:.6f} NIGHT")
        else:
            console.print(f"\n[yellow]⚠[/yellow] Balance did not decrease (transaction may still be pending)")
        
    except Exception as e:
        console.print(f"[yellow]⚠ Could not verify: {e}[/yellow]")
    
    # Success!
    console.print(Panel.fit(
        "[bold green]✓ Transfer Test Complete![/bold green]\n\n"
        f"• Transferred: {transfer_amount / 1_000_000:.6f} NIGHT\n"
        f"• To: {recipient[:40]}...\n"
        f"• Transaction: {result['tx_hash'][:40]}...",
        border_style="green"
    ))


if __name__ == "__main__":
    main()
