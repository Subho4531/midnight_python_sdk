"""
Midnight SDK CLI - Production-ready command-line interface.

A comprehensive CLI for the Midnight blockchain with command groups:
  wallet    - Key management
  config    - Profile/network configuration
  contract  - Contract lifecycle
  tx        - Transaction management
  proof     - ZK proof operations
  ai        - AI inference
  explorer  - Explorer integration
  system    - Service health
  events    - Event subscription
  node      - Raw RPC interaction
  console   - Interactive REPL
"""

import typer
from rich.console import Console
from pathlib import Path

from .commands import (
    wallet,
    config,
    contract,
    tx,
    proof,
    ai,
    explorer,
    system,
    node,
    events,
    console as console_cmd,
    transfer,
)

# Main app
app = typer.Typer(
    name="midnight",
    help="Production-ready CLI for Midnight blockchain",
    no_args_is_help=True,
)

# Global options callback
console = Console()


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print("[cyan]Midnight SDK CLI v0.1.0[/cyan]")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
    config_file: Path = typer.Option(
        None,
        "--config",
        "-c",
        help="Config file path",
        envvar="MIDNIGHT_CONFIG",
    ),
    profile: str = typer.Option(
        None,
        "--profile",
        "-p",
        help="Profile to use",
        envvar="MIDNIGHT_PROFILE",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Verbose output",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress output",
    ),
):
    """
    Midnight SDK CLI - Production-ready blockchain toolkit.
    
    Use command groups to interact with the Midnight network:
    
      midnight wallet new my-wallet
      midnight config use preprod
      midnight contract deploy my_contract.compact
      midnight tx status <hash>
      midnight system status
    
    For help on any command:
      midnight <command> --help
    """
    # Store global options in context
    ctx.ensure_object(dict)
    ctx.obj["config_file"] = config_file
    ctx.obj["profile"] = profile
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet


# Register command groups
app.add_typer(wallet.app, name="wallet")
app.add_typer(config.app, name="config")
app.add_typer(contract.app, name="contract")
app.add_typer(tx.app, name="tx")
app.add_typer(proof.app, name="proof")
app.add_typer(ai.app, name="ai")
app.add_typer(explorer.app, name="explorer")
app.add_typer(system.app, name="system")
app.add_typer(node.app, name="node")
app.add_typer(events.app, name="events")
app.add_typer(console_cmd.app, name="console")
app.add_typer(transfer.app, name="transfer")


# Quick status command at root level
@app.command()
def status(profile: str = typer.Option(None, "--profile", "-p", help="Network profile")):
    """Quick service health check."""
    from midnight_sdk.client import MidnightClient
    from midnight_sdk.config import ConfigManager
    from rich.table import Table
    
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    console.print(f"[cyan]Checking services on {profile_obj.name}...[/cyan]\n")
    
    try:
        client = MidnightClient(network=profile_obj.name)
        status_data = client.status()
        
        table = Table(title="Service Status")
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("URL", style="dim")
        
        services = [
            ("Node", status_data["node"], profile_obj.node_url),
            ("Indexer", status_data["indexer"], profile_obj.indexer_url),
            ("Proof Server", status_data["prover"], profile_obj.proof_server_url),
        ]
        
        for name, is_alive, url in services:
            status_str = "[green]✓ Online[/green]" if is_alive else "[red]✗ Offline[/red]"
            table.add_row(name, status_str, url)
        
        console.print(table)
        
        all_online = all(s[1] for s in services)
        if not all_online:
            console.print("\n[yellow]⚠ Some services are offline[/yellow]")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def balance(
    address: str = typer.Argument(None, help="Address to check (default: active wallet)"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
    full: bool = typer.Option(False, "--full", help="Show full balance including shielded NIGHT (requires 5-10 min sync)"),
):
    """Check wallet balance (shortcut for 'wallet balance')."""
    from midnight_sdk.wallet import WalletClient
    from midnight_sdk.config import ConfigManager
    from rich.table import Table
    from rich.panel import Panel
    from pathlib import Path
    
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    # Get mnemonic if using full balance
    mnemonic = None
    
    # Get address
    if not address:
        if not config_mgr.config.default_wallet:
            console.print("[red]No default wallet set[/red]")
            console.print("Use: midnight wallet new <name>")
            raise typer.Exit(1)
        
        wallet_name = config_mgr.config.default_wallet
        if wallet_name not in config_mgr.config.wallets:
            console.print(f"[red]Wallet '{wallet_name}' not found[/red]")
            raise typer.Exit(1)
        
        wallet_path = Path(config_mgr.config.wallets[wallet_name])
        if not wallet_path.exists():
            console.print(f"[red]Wallet file not found: {wallet_path}[/red]")
            raise typer.Exit(1)
        
        mnemonic = wallet_path.read_text().strip()
    
    wallet_client = WalletClient(profile_obj.node_url)
    
    if not mnemonic:
        console.print("[red]Balance query requires a wallet[/red]")
        console.print("[yellow]Use without address argument to query your default wallet[/yellow]")
        raise typer.Exit(1)
    
    # For local networks, use simple node balance endpoint (faster and works with airdrop)
    if profile_obj.network_id in ["undeployed", "local"]:
        console.print(Panel(
            "[cyan]Querying local node balance...[/cyan]\n\n"
            "Checking balance from local node endpoint",
            title="Wallet Balance Query",
            border_style="cyan"
        ))
        
        try:
            # Get address first
            addr_info = wallet_client.get_real_address(mnemonic, profile_obj.network_id)
            address = addr_info.get('address')
            
            # Query balance from node
            balance = wallet_client.get_balance(address, profile_obj.network_id)
            
            # Display address
            console.print(f"\n[cyan]Address:[/cyan] {address}")
            console.print()
            
            # Display balance
            table = Table(title="Wallet Balance")
            table.add_column("Token", style="cyan", width=20)
            table.add_column("Amount", style="green", justify="right")
            
            dust_str = f"{balance.dust / 1_000_000:.6f} DUST"
            night_str = f"{balance.night / 1_000_000:.6f} NIGHT"
            
            table.add_row("DUST", dust_str)
            table.add_row("NIGHT (Unshielded)", night_str)
            
            console.print(table)
            console.print(f"\n[dim]Network: {profile_obj.network_id}[/dim]")
            console.print(f"[dim]Note: Local node balance (from airdrop)[/dim]")
            
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            console.print("\n[yellow]Troubleshooting:[/yellow]")
            console.print("  • Make sure local node is running: docker-compose up -d")
            console.print("  • Check if airdrop was successful")
            raise typer.Exit(1)
    else:
        # For remote networks, use full balance query with Wallet SDK
        console.print(Panel(
            "[cyan]Querying wallet balance...[/cyan]\n\n"
            "This will:\n"
            "• Connect to the Midnight network\n"
            "• Sync your wallet history (up to 60 seconds)\n"
            "• Query DUST, unshielded NIGHT, and shielded NIGHT balances\n\n"
            "[dim]Note: Returns best available state after 60 seconds.[/dim]",
            title="Wallet Balance Query",
            border_style="cyan"
        ))
        
        try:
            with console.status("[cyan]Syncing wallet... (up to 60 seconds)...", spinner="dots"):
                balance_data = wallet_client.get_full_balance(
                    mnemonic,
                    profile_obj.network_id,
                    profile_obj.indexer_url,
                    profile_obj.indexer_ws_url,
                    profile_obj.node_url,
                    profile_obj.proof_server_url
                )
            
            # Display addresses
            addr_table = Table(title="Wallet Addresses")
            addr_table.add_column("Type", style="cyan", width=15)
            addr_table.add_column("Address", style="yellow")
            
            addr_table.add_row("Unshielded", balance_data['addresses']['unshielded'])
            addr_table.add_row("Shielded", balance_data['addresses']['shielded'][:60] + "...")
            addr_table.add_row("DUST", balance_data['addresses']['dust'])
            
            console.print(addr_table)
            console.print()
            
            # Display balances
            table = Table(title="Wallet Balance")
            table.add_column("Token", style="cyan", width=20)
            table.add_column("Amount", style="green", justify="right")
            table.add_column("Coins", style="yellow", justify="right")
            
            dust_val = int(balance_data['balances']['dust'])
            night_unshielded_val = int(balance_data['balances']['night_unshielded'])
            night_shielded_val = int(balance_data['balances']['night_shielded'])
            
            dust_str = f"{dust_val / 1_000_000:.6f} DUST"
            night_unshielded_str = f"{night_unshielded_val / 1_000_000:.6f} NIGHT"
            night_shielded_str = f"{night_shielded_val / 1_000_000:.6f} NIGHT"
            
            table.add_row("DUST", dust_str, str(balance_data['coins']['dust']))
            table.add_row("NIGHT (Unshielded)", night_unshielded_str, str(balance_data['coins']['unshielded']))
            table.add_row("NIGHT (Shielded)", night_shielded_str, str(balance_data['coins']['shielded']))
            
            console.print(table)
            
            # Show total NIGHT
            total_night = (night_unshielded_val + night_shielded_val) / 1_000_000
            console.print(f"\n[bold]Total NIGHT:[/bold] [green]{total_night:.6f}[/green]")
            
            console.print(f"\n[dim]Synced: {'✓' if balance_data['synced'] else '✗'}[/dim]")
            console.print(f"[dim]Network: {profile_obj.network_id}[/dim]")
            
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            console.print("\n[yellow]Troubleshooting:[/yellow]")
            console.print("  • Make sure you have a stable internet connection")
            console.print("  • The preprod network may be slow or overloaded")
            console.print("  • Try again in a few minutes")
            console.print("\n[cyan]Alternative - Check balance at:[/cyan]")
            console.print("  https://1am.xyz (import your mnemonic)")
            raise typer.Exit(1)


def cli_main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    cli_main()
