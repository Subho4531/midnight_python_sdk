"""Wallet management commands."""

import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
from mnemonic import Mnemonic
import httpx

from ...wallet import WalletClient
from ...config import ConfigManager

app = typer.Typer(help="Wallet key management")
console = Console()


def airdrop_tokens(address: str, node_url: str, dust: int = 1000000000000, night: int = 5000000000):
    """Fund a wallet with testnet tokens via airdrop."""
    try:
        response = httpx.post(
            f"{node_url}/balance",
            json={
                "address": address,
                "dust": dust,
                "night": night
            },
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            console.print(f"\n[green]✓ Airdrop successful![/green]")
            console.print(f"  DUST:  {data['dust']:,}")
            console.print(f"  NIGHT: {data['night']:,}")
            console.print(f"\n[dim]Note: Balance set on local node. Use 'midnight wallet balance' to verify.[/dim]\n")
            return True
        else:
            console.print(f"[red]✗ Airdrop failed: HTTP {response.status_code}[/red]")
            return False
            
    except httpx.ConnectError:
        console.print("[red]✗ Cannot connect to node for airdrop[/red]")
        console.print("[yellow]Make sure local node is running: docker-compose up -d[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]✗ Airdrop error: {e}[/red]")
        return False


@app.command("new")
def wallet_new(
    name: str = typer.Argument(..., help="Wallet name"),
    words: int = typer.Option(24, help="Mnemonic word count (12 or 24)"),
    airdrop: bool = typer.Option(False, "--airdrop", help="Fund wallet with testnet tokens"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile for airdrop"),
):
    """Generate a new wallet with mnemonic."""
    if words not in [12, 24]:
        console.print("[red]Error: words must be 12 or 24[/red]")
        raise typer.Exit(1)
    
    mnemo = Mnemonic("english")
    mnemonic = mnemo.generate(strength=128 if words == 12 else 256)
    
    # Save to config directory
    config_dir = Path.home() / ".midnight" / "wallets"
    config_dir.mkdir(parents=True, exist_ok=True)
    wallet_file = config_dir / f"{name}.txt"
    
    if wallet_file.exists():
        console.print(f"[red]Wallet '{name}' already exists[/red]")
        raise typer.Exit(1)
    
    wallet_file.write_text(mnemonic)
    wallet_file.chmod(0o600)  # Secure permissions
    
    # Update config
    config_mgr = ConfigManager()
    config_mgr.load()
    config_mgr.config.wallets[name] = str(wallet_file)
    if not config_mgr.config.default_wallet:
        config_mgr.config.default_wallet = name
    config_mgr.save()
    
    console.print(f"[green]✓[/green] Wallet '{name}' created")
    console.print(f"\n[yellow]⚠ SAVE THIS MNEMONIC SECURELY:[/yellow]")
    console.print(f"\n{mnemonic}\n")
    console.print(f"Saved to: {wallet_file}")
    
    # Airdrop if requested
    if airdrop:
        profile_obj = config_mgr.get_profile(profile)
        
        if profile_obj.network_id not in ["undeployed", "local"]:
            console.print(f"\n[yellow]⚠ Airdrop only works on local network[/yellow]")
            console.print(f"[yellow]Current network: {profile_obj.name} ({profile_obj.network_id})[/yellow]")
            console.print(f"[yellow]For testnet tokens, visit: https://faucet.{profile_obj.network_id}.midnight.network/[/yellow]")
        else:
            wallet_client = WalletClient(profile_obj.node_url)
            try:
                addr_info = wallet_client.get_real_address(mnemonic, profile_obj.network_id)
                address = addr_info['address']
                console.print(f"\n[cyan]Address:[/cyan] {address}")
                airdrop_tokens(address, profile_obj.node_url)
            except Exception as e:
                console.print(f"[red]Error during airdrop: {e}[/red]")


@app.command("import")
def wallet_import(
    name: str = typer.Argument(..., help="Wallet name"),
    mnemonic: str = typer.Option(None, "--mnemonic", "-m", help="Mnemonic phrase"),
    file: Path = typer.Option(None, "--file", "-f", help="File containing mnemonic"),
    airdrop: bool = typer.Option(False, "--airdrop", help="Fund wallet with testnet tokens"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile for airdrop"),
):
    """Import wallet from mnemonic or file."""
    if not mnemonic and not file:
        console.print("[red]Error: provide --mnemonic or --file[/red]")
        raise typer.Exit(1)
    
    if file:
        if not file.exists():
            console.print(f"[red]File not found: {file}[/red]")
            raise typer.Exit(1)
        mnemonic = file.read_text().strip()
    
    # Validate mnemonic
    mnemo = Mnemonic("english")
    if not mnemo.check(mnemonic):
        console.print("[red]Invalid mnemonic phrase[/red]")
        raise typer.Exit(1)
    
    # Save wallet
    config_dir = Path.home() / ".midnight" / "wallets"
    config_dir.mkdir(parents=True, exist_ok=True)
    wallet_file = config_dir / f"{name}.txt"
    
    if wallet_file.exists():
        overwrite = typer.confirm(f"Wallet '{name}' exists. Overwrite?")
        if not overwrite:
            raise typer.Exit(0)
    
    wallet_file.write_text(mnemonic)
    wallet_file.chmod(0o600)
    
    # Update config
    config_mgr = ConfigManager()
    config_mgr.load()
    config_mgr.config.wallets[name] = str(wallet_file)
    if not config_mgr.config.default_wallet:
        config_mgr.config.default_wallet = name
    config_mgr.save()
    
    console.print(f"[green]✓[/green] Wallet '{name}' imported")
    
    # Airdrop if requested
    if airdrop:
        profile_obj = config_mgr.get_profile(profile)
        
        if profile_obj.network_id not in ["undeployed", "local"]:
            console.print(f"\n[yellow]⚠ Airdrop only works on local network[/yellow]")
            console.print(f"[yellow]Current network: {profile_obj.name} ({profile_obj.network_id})[/yellow]")
            console.print(f"[yellow]For testnet tokens, visit: https://faucet.{profile_obj.network_id}.midnight.network/[/yellow]")
        else:
            wallet_client = WalletClient(profile_obj.node_url)
            try:
                addr_info = wallet_client.get_real_address(mnemonic, profile_obj.network_id)
                address = addr_info['address']
                console.print(f"\n[cyan]Address:[/cyan] {address}")
                airdrop_tokens(address, profile_obj.node_url)
            except Exception as e:
                console.print(f"[red]Error during airdrop: {e}[/red]")


@app.command("list")
def wallet_list():
    """List all stored wallets."""
    config_mgr = ConfigManager()
    config_mgr.load()
    
    if not config_mgr.config.wallets:
        console.print("[yellow]No wallets found[/yellow]")
        return
    
    table = Table(title="Wallets")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="dim")
    table.add_column("Default", style="green")
    
    for name, path in config_mgr.config.wallets.items():
        is_default = "✓" if name == config_mgr.config.default_wallet else ""
        table.add_row(name, path, is_default)
    
    console.print(table)


@app.command("balance")
def wallet_balance(
    address: str = typer.Argument(None, help="Address to check (default: active wallet)"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """Show DUST balance for address."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    # Get address
    if not address:
        if not config_mgr.config.default_wallet:
            console.print("[red]No default wallet set[/red]")
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
        
        try:
            with console.status("[cyan]Deriving address..."):
                wallet_client = WalletClient(profile_obj.node_url)
                addr_info = wallet_client.get_real_address(mnemonic, profile_obj.network_id)
                address = addr_info.get("address")
                
                if not address:
                    console.print("[red]Failed to derive address[/red]")
                    raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Error deriving address: {e}[/red]")
            raise typer.Exit(1)
    
    # Get balance
    wallet_client = WalletClient(profile_obj.node_url)
    
    try:
        with console.status("[cyan]Fetching balance from indexer..."):
            balance = wallet_client.get_balance(address, profile_obj.network_id)
        
        table = Table(title=f"Balance for {address[:16]}...")
        table.add_column("Token", style="cyan")
        table.add_column("Amount", style="green", justify="right")
        
        # Format amounts with commas
        dust_str = f"{balance.dust:,}" if balance.dust else "0"
        
        table.add_row("DUST", dust_str)
        table.add_row("NIGHT", "[dim]Shielded (use wallet SDK)[/dim]")
        
        console.print(table)
        console.print("\n[dim]Note: NIGHT is shielded and cannot be queried from indexer without a viewing key.[/dim]")
    except Exception as e:
        console.print(f"[red]Error fetching balance: {e}[/red]")
        raise typer.Exit(1)


@app.command("address")
def wallet_address(
    name: str = typer.Argument(None, help="Wallet name (default: active)"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
    airdrop: bool = typer.Option(False, "--airdrop", help="Fund wallet with testnet tokens"),
):
    """Show address for named wallet."""
    config_mgr = ConfigManager()
    config_mgr.load()
    
    wallet_name = name or config_mgr.config.default_wallet
    if not wallet_name:
        console.print("[red]No wallet specified and no default set[/red]")
        raise typer.Exit(1)
    
    if wallet_name not in config_mgr.config.wallets:
        console.print(f"[red]Wallet '{wallet_name}' not found[/red]")
        raise typer.Exit(1)
    
    wallet_path = Path(config_mgr.config.wallets[wallet_name])
    mnemonic = wallet_path.read_text().strip()
    
    profile_obj = config_mgr.get_profile(profile)
    wallet_client = WalletClient(profile_obj.node_url)
    
    try:
        addr_info = wallet_client.get_real_address(mnemonic, profile_obj.network_id)
        address = addr_info['address']
        console.print(f"[cyan]Wallet:[/cyan] {wallet_name}")
        console.print(f"[cyan]Address:[/cyan] {address}")
        
        # Airdrop if requested
        if airdrop:
            if profile_obj.network_id not in ["undeployed", "local"]:
                console.print(f"\n[yellow]⚠ Airdrop only works on local network[/yellow]")
                console.print(f"[yellow]Current network: {profile_obj.name} ({profile_obj.network_id})[/yellow]")
                console.print(f"[yellow]For testnet tokens, visit: https://faucet.{profile_obj.network_id}.midnight.network/[/yellow]")
            else:
                airdrop_tokens(address, profile_obj.node_url)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("export")
def wallet_export(
    name: str = typer.Argument(..., help="Wallet name"),
    show_private_key: bool = typer.Option(False, "--private-key", help="Show private key"),
):
    """Export wallet mnemonic (with warning)."""
    config_mgr = ConfigManager()
    config_mgr.load()
    
    if name not in config_mgr.config.wallets:
        console.print(f"[red]Wallet '{name}' not found[/red]")
        raise typer.Exit(1)
    
    console.print("[yellow]⚠ WARNING: Never share your mnemonic or private key![/yellow]")
    confirmed = typer.confirm("Continue?")
    if not confirmed:
        raise typer.Exit(0)
    
    wallet_path = Path(config_mgr.config.wallets[name])
    mnemonic = wallet_path.read_text().strip()
    
    console.print(f"\n[cyan]Mnemonic:[/cyan]\n{mnemonic}\n")
    
    if show_private_key:
        wallet_client = WalletClient()
        keys = wallet_client.get_private_keys(mnemonic)
        console.print(f"[cyan]Private Key:[/cyan]\n{keys['private_key']}\n")
