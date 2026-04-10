"""Contract lifecycle commands."""

import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json

from ...client import MidnightClient
from ...config import ConfigManager
from ...codegen import compile_compact

app = typer.Typer(help="Contract compilation, deployment, and interaction")
console = Console()


@app.command("compile")
def contract_compile(
    path: Path = typer.Argument(..., help="Path to .compact file"),
    output: Path = typer.Option(None, "--output", "-o", help="Output directory"),
):
    """Compile .compact contract."""
    if not path.exists():
        console.print(f"[red]File not found: {path}[/red]")
        raise typer.Exit(1)
    
    if path.suffix != ".compact":
        console.print("[red]File must have .compact extension[/red]")
        raise typer.Exit(1)
    
    try:
        with console.status("[cyan]Compiling contract..."):
            result = compile_compact(str(path), str(output) if output else None)
        
        console.print(f"[green]✓[/green] Contract compiled successfully")
        console.print(f"Output: {result}")
    except Exception as e:
        console.print(f"[red]Compilation failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("deploy")
def contract_deploy(
    path: Path = typer.Argument(..., help="Path to .compact file"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
    wallet: str = typer.Option(None, "--wallet", "-w", help="Wallet name"),
):
    """Deploy contract to network."""
    if not path.exists():
        console.print(f"[red]File not found: {path}[/red]")
        raise typer.Exit(1)
    
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    # Get wallet mnemonic
    wallet_name = wallet or config_mgr.config.default_wallet
    if not wallet_name:
        console.print("[red]No wallet specified[/red]")
        raise typer.Exit(1)
    
    wallet_path = Path(config_mgr.config.wallets[wallet_name])
    mnemonic = wallet_path.read_text().strip()
    
    try:
        with console.status("[cyan]Deploying contract..."):
            client = MidnightClient(network=profile_obj.name)
            result = client.contracts.deploy(str(path), mnemonic)
        
        console.print(f"[green]✓[/green] Contract deployed")
        console.print(f"[cyan]Address:[/cyan] {result.contract_address}")
        console.print(f"[cyan]TX Hash:[/cyan] {result.tx_hash}")
    except Exception as e:
        console.print(f"[red]Deployment failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("call")
def contract_call(
    address: str = typer.Argument(..., help="Contract address"),
    circuit: str = typer.Argument(..., help="Circuit name"),
    args: str = typer.Option("{}", "--args", help="JSON arguments"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
    wallet: str = typer.Option(None, "--wallet", "-w", help="Wallet name"),
):
    """Call contract circuit (mutating)."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    wallet_name = wallet or config_mgr.config.default_wallet
    if not wallet_name:
        console.print("[red]No wallet specified[/red]")
        raise typer.Exit(1)
    
    wallet_path = Path(config_mgr.config.wallets[wallet_name])
    mnemonic = wallet_path.read_text().strip()
    
    try:
        args_dict = json.loads(args)
    except json.JSONDecodeError:
        console.print("[red]Invalid JSON arguments[/red]")
        raise typer.Exit(1)
    
    try:
        with console.status("[cyan]Calling contract..."):
            client = MidnightClient(network=profile_obj.name)
            contract = client.get_contract(address, [circuit])
            result = contract.call(circuit, args_dict, mnemonic)
        
        console.print(f"[green]✓[/green] Circuit called")
        console.print(f"[cyan]TX Hash:[/cyan] {result.tx_hash}")
    except Exception as e:
        console.print(f"[red]Call failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("query")
def contract_query(
    address: str = typer.Argument(..., help="Contract address"),
    method: str = typer.Argument(..., help="Query method"),
    args: str = typer.Option("{}", "--args", help="JSON arguments"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """Query contract state (read-only)."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    try:
        args_dict = json.loads(args)
    except json.JSONDecodeError:
        console.print("[red]Invalid JSON arguments[/red]")
        raise typer.Exit(1)
    
    try:
        client = MidnightClient(network=profile_obj.name)
        result = client.indexer.query_contract_state(address, method, args_dict)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]Query failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("events")
def contract_events(
    address: str = typer.Argument(..., help="Contract address"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow new events"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """Listen to contract events."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    try:
        client = MidnightClient(network=profile_obj.name)
        
        if follow:
            console.print(f"[cyan]Listening for events from {address}...[/cyan]")
            # TODO: Implement WebSocket subscription
            console.print("[yellow]Event streaming not yet implemented[/yellow]")
        else:
            events = client.indexer.get_contract_events(address)
            for event in events:
                console.print(json.dumps(event, indent=2))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("list")
def contract_list(profile: str = typer.Option(None, "--profile", "-p", help="Network profile")):
    """List locally deployed contracts."""
    # Read from local cache/config
    cache_file = Path.home() / ".midnight" / "contracts.json"
    
    if not cache_file.exists():
        console.print("[yellow]No contracts found[/yellow]")
        return
    
    contracts = json.loads(cache_file.read_text())
    
    table = Table(title="Deployed Contracts")
    table.add_column("Name", style="cyan")
    table.add_column("Address", style="yellow")
    table.add_column("Network", style="dim")
    
    for contract in contracts:
        table.add_row(contract["name"], contract["address"], contract["network"])
    
    console.print(table)


@app.command("info")
def contract_info(
    address: str = typer.Argument(..., help="Contract address"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """Show contract details."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    try:
        client = MidnightClient(network=profile_obj.name)
        info = client.indexer.get_contract_info(address)
        console.print(json.dumps(info, indent=2))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
