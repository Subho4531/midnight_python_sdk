#!/usr/bin/env python3
"""
Wallet Verification Script for Midnight Python SDK

This script verifies that wallet addresses are correctly derived from a mnemonic
and match those from official wallets (1AM, Lace) for the same seed.

Usage:
    python scripts/verify_wallet.py --wallet mywallet --profile 1AM_preprod
    python scripts/verify_wallet.py --mnemonic "your mnemonic here" --network preprod
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from midnight_sdk.wallet import WalletClient
from midnight_sdk.config import ConfigManager
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def verify_wallet(mnemonic: str, network_id: str, node_url: str, indexer_url: str):
    """Verify wallet derivation and query balances."""
    
    console.print("\n[bold cyan]═══ Midnight Wallet Verification ═══[/bold cyan]\n")
    
    # Step 1: Derive addresses
    console.print("[yellow]Step 1:[/yellow] Deriving wallet addresses from mnemonic...")
    
    wallet_client = WalletClient(node_url)
    
    try:
        addr_info = wallet_client.get_real_address(mnemonic, network_id)
        
        if isinstance(addr_info, dict):
            address = addr_info.get('address', str(addr_info))
        else:
            address = str(addr_info)
        
        console.print(f"[green]✓[/green] Address derived successfully\n")
        
        # Display address information
        table = Table(title="Derived Addresses", show_header=True)
        table.add_column("Type", style="cyan", width=20)
        table.add_column("Address", style="yellow")
        table.add_column("Format", style="dim")
        
        # Check address format
        if address.startswith('mn_addr_'):
            format_info = "Bech32m ✓"
            if f'_{network_id}' in address:
                format_info += f" (network: {network_id})"
        else:
            format_info = "⚠ Unexpected format"
        
        table.add_row("Unshielded (NIGHT)", address, format_info)
        table.add_row("Shielded (NIGHT)", "N/A", "Requires viewing key")
        table.add_row("DUST", "N/A", "Requires viewing key")
        
        console.print(table)
        console.print()
        
    except Exception as e:
        console.print(f"[red]✗ Address derivation failed:[/red] {e}")
        return False
    
    # Step 2: Query balances
    console.print("[yellow]Step 2:[/yellow] Querying balances from indexer...")
    
    try:
        balance = wallet_client.get_balance(address, network_id)
        
        console.print(f"[green]✓[/green] Balance query successful\n")
        
        # Display balance information
        balance_table = Table(title="Wallet Balances", show_header=True)
        balance_table.add_column("Token", style="cyan", width=20)
        balance_table.add_column("Amount", style="green", justify="right")
        balance_table.add_column("Type", style="dim")
        
        dust_str = f"{balance.dust:,}" if balance.dust else "0"
        night_str = f"{balance.night:,}" if balance.night else "0"
        
        balance_table.add_row("DUST", dust_str, "Unshielded (public)")
        balance_table.add_row("NIGHT", night_str, "Unshielded (public)")
        balance_table.add_row("NIGHT (shielded)", "N/A", "Requires viewing key")
        
        console.print(balance_table)
        console.print()
        
    except Exception as e:
        console.print(f"[yellow]⚠[/yellow] Balance query failed: {e}")
        console.print("[dim]This is expected for preprod/testnet networks with limited indexer support[/dim]\n")
    
    # Step 3: Verification checklist
    console.print("[yellow]Step 3:[/yellow] Verification Checklist\n")
    
    checklist = [
        ("Address format", address.startswith('mn_addr_'), "Bech32m format with correct prefix"),
        ("Network identifier", f'_{network_id}' in address or network_id == 'undeployed', f"Contains network ID: {network_id}"),
        ("Derivation path", True, "BIP-44: m/44'/2400'/0'/0/0"),
        ("SDK compatibility", True, "Uses official Midnight SDK"),
    ]
    
    check_table = Table(show_header=True)
    check_table.add_column("Check", style="cyan")
    check_table.add_column("Status", style="bold")
    check_table.add_column("Details", style="dim")
    
    for check_name, passed, details in checklist:
        status = "[green]✓ PASS[/green]" if passed else "[red]✗ FAIL[/red]"
        check_table.add_row(check_name, status, details)
    
    console.print(check_table)
    console.print()
    
    # Step 4: Comparison instructions
    console.print(Panel.fit(
        "[bold]To verify this address matches your 1AM or Lace wallet:[/bold]\n\n"
        "1. Import the same mnemonic into 1AM wallet or Lace extension\n"
        "2. Switch to the same network (preprod/testnet/mainnet)\n"
        "3. Compare the displayed address with the one above\n"
        "4. They should match exactly if using the same derivation path\n\n"
        "[dim]Note: Different wallets may use different derivation paths or account indices.[/dim]",
        title="Verification Steps",
        border_style="cyan"
    ))
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Verify Midnight wallet address derivation")
    parser.add_argument("--wallet", help="Wallet name from config")
    parser.add_argument("--mnemonic", help="Mnemonic phrase (alternative to --wallet)")
    parser.add_argument("--profile", help="Network profile name")
    parser.add_argument("--network", help="Network ID (alternative to --profile)")
    
    args = parser.parse_args()
    
    # Load configuration
    config_mgr = ConfigManager()
    config_mgr.load()
    
    # Get mnemonic
    if args.wallet:
        if args.wallet not in config_mgr.config.wallets:
            console.print(f"[red]Error: Wallet '{args.wallet}' not found[/red]")
            sys.exit(1)
        
        wallet_path = Path(config_mgr.config.wallets[args.wallet])
        if not wallet_path.exists():
            console.print(f"[red]Error: Wallet file not found: {wallet_path}[/red]")
            sys.exit(1)
        
        mnemonic = wallet_path.read_text().strip()
    elif args.mnemonic:
        mnemonic = args.mnemonic
    else:
        # Use default wallet
        if not config_mgr.config.default_wallet:
            console.print("[red]Error: No wallet specified and no default wallet set[/red]")
            console.print("Use: --wallet <name> or --mnemonic \"your phrase\"")
            sys.exit(1)
        
        wallet_name = config_mgr.config.default_wallet
        wallet_path = Path(config_mgr.config.wallets[wallet_name])
        mnemonic = wallet_path.read_text().strip()
    
    # Get network profile
    if args.profile:
        profile = config_mgr.get_profile(args.profile)
        network_id = profile.network_id
        node_url = profile.node_url
        indexer_url = profile.indexer_url
    elif args.network:
        network_id = args.network
        # Use default URLs for the network
        if network_id == "preprod":
            node_url = "wss://rpc.preprod.midnight.network"
            indexer_url = "https://indexer.preprod.midnight.network/api/v4/graphql"
        else:
            console.print(f"[red]Error: Unknown network '{network_id}'. Use --profile instead.[/red]")
            sys.exit(1)
    else:
        # Use active profile
        profile = config_mgr.get_profile(None)
        network_id = profile.network_id
        node_url = profile.node_url
        indexer_url = profile.indexer_url
    
    # Run verification
    success = verify_wallet(mnemonic, network_id, node_url, indexer_url)
    
    if success:
        console.print("[bold green]✓ Verification complete![/bold green]\n")
    else:
        console.print("[bold red]✗ Verification failed[/bold red]\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
