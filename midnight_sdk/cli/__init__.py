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


def cli_main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    cli_main()
