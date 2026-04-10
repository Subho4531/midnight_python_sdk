"""Configuration management commands."""

import typer
from rich.console import Console
from rich.table import Table
import yaml

from ...config import ConfigManager, NetworkProfile

app = typer.Typer(help="Profile and network configuration")
console = Console()


@app.command("init")
def config_init(force: bool = typer.Option(False, "--force", help="Overwrite existing")):
    """Create default configuration."""
    config_mgr = ConfigManager()
    
    if config_mgr.config_path.exists() and not force:
        console.print(f"[yellow]Config already exists at {config_mgr.config_path}[/yellow]")
        console.print("Use --force to overwrite")
        raise typer.Exit(1)
    
    config_mgr.load()  # Creates default if not exists
    console.print(f"[green]✓[/green] Config initialized at {config_mgr.config_path}")


@app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Config key (dot notation)"),
    value: str = typer.Argument(..., help="Value to set"),
):
    """Set configuration value."""
    config_mgr = ConfigManager()
    config_mgr.load()
    
    try:
        config_mgr.set(key, value)
        console.print(f"[green]✓[/green] Set {key} = {value}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("get")
def config_get(key: str = typer.Argument(..., help="Config key (dot notation)")):
    """Get configuration value."""
    config_mgr = ConfigManager()
    config_mgr.load()
    
    try:
        value = config_mgr.get(key)
        console.print(f"{key} = {value}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("list")
def config_list(output: str = typer.Option("table", "--output", "-o", help="table|json|yaml")):
    """Show all configuration."""
    config_mgr = ConfigManager()
    config_mgr.load()
    
    if output == "json":
        import json
        console.print(json.dumps(config_mgr.config.model_dump(), indent=2))
    elif output == "yaml":
        console.print(yaml.dump(config_mgr.config.model_dump(), default_flow_style=False))
    else:
        # Table format
        console.print(f"[cyan]Active Profile:[/cyan] {config_mgr.config.active_profile}")
        console.print(f"[cyan]Default Wallet:[/cyan] {config_mgr.config.default_wallet or 'None'}\n")
        
        table = Table(title="Network Profiles")
        table.add_column("Name", style="cyan")
        table.add_column("Network ID", style="yellow")
        table.add_column("Node URL", style="dim")
        table.add_column("Active", style="green")
        
        for name, profile in config_mgr.config.profiles.items():
            is_active = "✓" if name == config_mgr.config.active_profile else ""
            table.add_row(name, profile.network_id, profile.node_url, is_active)
        
        console.print(table)


@app.command("use")
def config_use(profile: str = typer.Argument(..., help="Profile name")):
    """Switch active profile."""
    config_mgr = ConfigManager()
    config_mgr.load()
    
    if profile not in config_mgr.config.profiles:
        console.print(f"[red]Profile '{profile}' not found[/red]")
        raise typer.Exit(1)
    
    config_mgr.config.active_profile = profile
    config_mgr.save()
    console.print(f"[green]✓[/green] Switched to profile '{profile}'")


@app.command("add-network")
def config_add_network(
    name: str = typer.Argument(..., help="Network name"),
    node_url: str = typer.Option(..., "--node", help="Node RPC URL"),
    indexer_url: str = typer.Option(..., "--indexer", help="Indexer GraphQL URL"),
    indexer_ws_url: str = typer.Option(..., "--indexer-ws", help="Indexer WebSocket URL"),
    proof_server_url: str = typer.Option(..., "--proof", help="Proof server URL"),
    network_id: str = typer.Option(..., "--network-id", help="Network ID"),
    explorer_url: str = typer.Option("", "--explorer", help="Explorer URL"),
):
    """Add custom network profile."""
    config_mgr = ConfigManager()
    config_mgr.load()
    
    profile = NetworkProfile(
        name=name,
        node_url=node_url,
        indexer_url=indexer_url,
        indexer_ws_url=indexer_ws_url,
        proof_server_url=proof_server_url,
        network_id=network_id,
        explorer_url=explorer_url,
    )
    
    config_mgr.add_profile(profile)
    console.print(f"[green]✓[/green] Added network profile '{name}'")
