"""Token transfer commands for Midnight dual-token model."""

import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json

from ...client import MidnightClient
from ...config import ConfigManager
from ...wallet import WalletClient

app = typer.Typer(help="Transfer NIGHT tokens (unshielded or shielded)")
console = Console()


@app.command("unshielded")
def transfer_unshielded(
    recipient: str = typer.Argument(..., help="Recipient address (mn_addr_...)"),
    amount: int = typer.Argument(..., help="Amount to transfer (in smallest units)"),
    token: str = typer.Option("NIGHT", "--token", "-t", help="Token type (NIGHT only)"),
    wallet: str = typer.Option(None, "--wallet", "-w", help="Wallet name"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate without sending"),
):
    """
    Transfer unshielded (public) NIGHT tokens.
    
    NIGHT is the native transferable token on Midnight.
    DUST cannot be transferred - it's generated automatically from NIGHT holdings.
    
    Examples:
      midnight transfer unshielded mn_addr_preprod1... 1000000
      midnight transfer unshielded mn_addr_preprod1... 5000000 --wallet my-wallet
    """
    # Validate token type
    if token.upper() not in ["NIGHT"]:
        console.print("[red]Error: Only NIGHT tokens can be transferred[/red]")
        console.print("[yellow]DUST is non-transferable and generated automatically from NIGHT holdings[/yellow]")
        raise typer.Exit(1)
    
    # Validate recipient address format
    if not recipient.startswith("mn_addr_"):
        console.print(f"[red]Error: Invalid recipient address format[/red]")
        console.print(f"[yellow]Expected format: mn_addr_<network>1...[/yellow]")
        raise typer.Exit(1)
    
    # Validate amount
    if amount <= 0:
        console.print("[red]Error: Amount must be positive[/red]")
        raise typer.Exit(1)
    
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    # Get wallet
    wallet_name = wallet or config_mgr.config.default_wallet
    if not wallet_name:
        console.print("[red]No wallet specified[/red]")
        console.print("Use --wallet or set default: midnight config set default_wallet <name>")
        raise typer.Exit(1)
    
    if wallet_name not in config_mgr.config.wallets:
        console.print(f"[red]Wallet '{wallet_name}' not found[/red]")
        raise typer.Exit(1)
    
    wallet_path = Path(config_mgr.config.wallets[wallet_name])
    if not wallet_path.exists():
        console.print(f"[red]Wallet file not found: {wallet_path}[/red]")
        raise typer.Exit(1)
    
    mnemonic = wallet_path.read_text().strip()
    
    # Get sender address
    try:
        with console.status("[cyan]Deriving sender address..."):
            wallet_client = WalletClient(profile_obj.node_url)
            addr_info = wallet_client.get_real_address(mnemonic, profile_obj.network_id)
            sender_address = addr_info.get("address")
            
            if not sender_address:
                console.print("[red]Failed to derive sender address[/red]")
                raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error deriving address: {e}[/red]")
        raise typer.Exit(1)
    
    # Check sender balance
    try:
        with console.status("[cyan]Checking balance..."):
            balance = wallet_client.get_balance(sender_address, profile_obj.network_id)
        
        if balance.night < amount:
            console.print(f"[red]Insufficient balance[/red]")
            console.print(f"Available: {balance.night:,} NIGHT")
            console.print(f"Required:  {amount:,} NIGHT")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not check balance: {e}[/yellow]")
    
    # Display transfer details
    console.print("\n[cyan]Transfer Details:[/cyan]")
    table = Table(show_header=False)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="yellow")
    
    table.add_row("From", sender_address[:40] + "...")
    table.add_row("To", recipient[:40] + "...")
    table.add_row("Amount", f"{amount:,} {token}")
    table.add_row("Network", profile_obj.name)
    table.add_row("Type", "Unshielded (Public)")
    
    console.print(table)
    
    if dry_run:
        console.print("\n[yellow]Dry run - no transaction sent[/yellow]")
        return
    
    # Confirm transfer
    console.print()
    confirmed = typer.confirm("Proceed with transfer?")
    if not confirmed:
        console.print("[yellow]Transfer cancelled[/yellow]")
        raise typer.Exit(0)
    
    # Execute transfer
    try:
        with console.status("[cyan]Sending transaction..."):
            client = MidnightClient(network=profile_obj.name)
            
            # Build and send transfer transaction
            result = client.wallet.transfer_unshielded(
                recipient=recipient,
                amount=amount,
                mnemonic=mnemonic,
                network_id=profile_obj.network_id
            )
        
        console.print(f"\n[green]✓[/green] Transfer submitted successfully")
        console.print(f"[cyan]TX Hash:[/cyan] {result.get('tx_hash', 'N/A')}")
        
        if result.get('tx_hash'):
            console.print(f"\n[dim]Track status: midnight tx status {result['tx_hash']}[/dim]")
    
    except Exception as e:
        console.print(f"\n[red]Transfer failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("shielded")
def transfer_shielded(
    recipient: str = typer.Argument(..., help="Recipient shielded address"),
    amount: int = typer.Argument(..., help="Amount to transfer (in smallest units)"),
    token: str = typer.Option("NIGHT", "--token", "-t", help="Token type (NIGHT or custom)"),
    wallet: str = typer.Option(None, "--wallet", "-w", help="Wallet name"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate without sending"),
):
    """
    Transfer shielded (private) tokens.
    
    Shielded transfers provide privacy - amounts and participants are encrypted.
    Requires the Midnight wallet SDK for ZK proof generation.
    
    Note: DUST cannot be transferred. Only NIGHT and other shielded tokens.
    
    Examples:
      midnight transfer shielded <shielded_addr> 1000000
      midnight transfer shielded <shielded_addr> 5000000 --wallet my-wallet
    """
    # Validate token type
    if token.upper() == "DUST":
        console.print("[red]Error: DUST cannot be transferred[/red]")
        console.print("[yellow]DUST is non-transferable and generated automatically from NIGHT holdings[/yellow]")
        raise typer.Exit(1)
    
    # Validate amount
    if amount <= 0:
        console.print("[red]Error: Amount must be positive[/red]")
        raise typer.Exit(1)
    
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    # Get wallet
    wallet_name = wallet or config_mgr.config.default_wallet
    if not wallet_name:
        console.print("[red]No wallet specified[/red]")
        console.print("Use --wallet or set default: midnight config set default_wallet <name>")
        raise typer.Exit(1)
    
    if wallet_name not in config_mgr.config.wallets:
        console.print(f"[red]Wallet '{wallet_name}' not found[/red]")
        raise typer.Exit(1)
    
    wallet_path = Path(config_mgr.config.wallets[wallet_name])
    if not wallet_path.exists():
        console.print(f"[red]Wallet file not found: {wallet_path}[/red]")
        raise typer.Exit(1)
    
    mnemonic = wallet_path.read_text().strip()
    
    # Display transfer details
    console.print("\n[cyan]Shielded Transfer Details:[/cyan]")
    table = Table(show_header=False)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="yellow")
    
    table.add_row("To", recipient[:40] + "..." if len(recipient) > 40 else recipient)
    table.add_row("Amount", f"{amount:,} {token}")
    table.add_row("Network", profile_obj.name)
    table.add_row("Type", "Shielded (Private)")
    table.add_row("Privacy", "✓ Amount and sender encrypted")
    
    console.print(table)
    
    if dry_run:
        console.print("\n[yellow]Dry run - no transaction sent[/yellow]")
        return
    
    # Confirm transfer
    console.print()
    confirmed = typer.confirm("Proceed with shielded transfer?")
    if not confirmed:
        console.print("[yellow]Transfer cancelled[/yellow]")
        raise typer.Exit(0)
    
    # Execute shielded transfer
    try:
        console.print("\n[cyan]Preparing shielded transfer...[/cyan]")
        console.print("[dim]This requires the Midnight wallet SDK and may take 10-30 seconds[/dim]\n")
        
        with console.status("[cyan]Generating ZK proof and sending transaction..."):
            client = MidnightClient(network=profile_obj.name)
            
            # Build and send shielded transfer transaction
            result = client.wallet.transfer_shielded(
                recipient=recipient,
                amount=amount,
                token=token,
                mnemonic=mnemonic,
                network_id=profile_obj.network_id
            )
        
        console.print(f"[green]✓[/green] Shielded transfer submitted successfully")
        console.print(f"[cyan]TX Hash:[/cyan] {result.get('tx_hash', 'N/A')}")
        
        if result.get('tx_hash'):
            console.print(f"\n[dim]Track status: midnight tx status {result['tx_hash']}[/dim]")
    
    except NotImplementedError:
        console.print(f"[red]Shielded transfers require the Midnight wallet SDK[/red]")
        console.print(f"[yellow]This feature uses the Node.js wallet SDK for ZK proof generation[/yellow]")
        console.print(f"\n[dim]To enable shielded transfers:[/dim]")
        console.print(f"[dim]1. Install Node.js 22+[/dim]")
        console.print(f"[dim]2. Run: npm install (in repo root)[/dim]")
        console.print(f"[dim]3. Ensure wallet SDK packages are installed[/dim]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]Shielded transfer failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("info")
def transfer_info():
    """
    Show information about Midnight's dual-token model and transfers.
    """
    console.print("\n[bold cyan]Midnight Dual-Token Model[/bold cyan]\n")
    
    # NIGHT token info
    night_table = Table(title="NIGHT Token", show_header=False)
    night_table.add_column("Property", style="cyan")
    night_table.add_column("Value", style="yellow")
    
    night_table.add_row("Type", "Native, Unshielded (Public)")
    night_table.add_row("Transferable", "✓ Yes")
    night_table.add_row("Use Cases", "Governance, Staking, Generating DUST")
    night_table.add_row("Privacy", "Public (amounts visible on-chain)")
    night_table.add_row("Shielded Version", "Available (private transfers)")
    
    console.print(night_table)
    console.print()
    
    # DUST token info
    dust_table = Table(title="DUST Token", show_header=False)
    dust_table.add_column("Property", style="cyan")
    dust_table.add_column("Value", style="yellow")
    
    dust_table.add_row("Type", "Shielded Resource")
    dust_table.add_row("Transferable", "✗ No - Non-transferable")
    dust_table.add_row("Generation", "Automatic from NIGHT holdings")
    dust_table.add_row("Use Cases", "Transaction fees, Contract execution")
    dust_table.add_row("Privacy", "Shielded (amounts encrypted)")
    
    console.print(dust_table)
    console.print()
    
    # Transfer types
    console.print("[bold cyan]Transfer Types[/bold cyan]\n")
    
    transfer_table = Table()
    transfer_table.add_column("Type", style="cyan")
    transfer_table.add_column("Command", style="yellow")
    transfer_table.add_column("Privacy", style="green")
    transfer_table.add_column("Speed", style="magenta")
    
    transfer_table.add_row(
        "Unshielded",
        "midnight transfer unshielded",
        "Public",
        "Fast (~2s)"
    )
    transfer_table.add_row(
        "Shielded",
        "midnight transfer shielded",
        "Private",
        "Slower (~30s)"
    )
    
    console.print(transfer_table)
    console.print()
    
    # Important notes
    console.print("[bold yellow]Important Notes:[/bold yellow]\n")
    console.print("• DUST cannot be transferred between wallets")
    console.print("• DUST is generated automatically based on NIGHT holdings")
    console.print("• Unshielded transfers are public and fast")
    console.print("• Shielded transfers are private but require ZK proof generation")
    console.print("• Both transfer types consume DUST for transaction fees")
    console.print()
    
    # Examples
    console.print("[bold cyan]Examples:[/bold cyan]\n")
    console.print("[dim]# Transfer 1,000,000 NIGHT (unshielded)[/dim]")
    console.print("midnight transfer unshielded mn_addr_preprod1... 1000000\n")
    console.print("[dim]# Transfer 5,000,000 NIGHT (shielded/private)[/dim]")
    console.print("midnight transfer shielded <shielded_addr> 5000000\n")
    console.print("[dim]# Check balance before transfer[/dim]")
    console.print("midnight wallet balance\n")
