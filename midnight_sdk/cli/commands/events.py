"""Event subscription and querying commands."""

import typer
from rich.console import Console
import json

from ...client import MidnightClient
from ...config import ConfigManager

app = typer.Typer(help="Event subscription and querying")
console = Console()


@app.command("listen")
def events_listen(
    contract: str = typer.Option(None, "--contract", "-c", help="Filter by contract"),
    event_type: str = typer.Option(None, "--type", "-t", help="Filter by event type"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """Subscribe to real-time events."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    console.print("[cyan]Listening for events...[/cyan]")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")
    
    try:
        client = MidnightClient(network=profile_obj.name)
        
        # TODO: Implement WebSocket subscription
        console.print("[yellow]Real-time event streaming not yet implemented[/yellow]")
        console.print("Use 'midnight events query' for historical events")
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped listening[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("query")
def events_query(
    contract: str = typer.Option(None, "--contract", "-c", help="Filter by contract"),
    event_type: str = typer.Option(None, "--type", "-t", help="Filter by event type"),
    from_block: int = typer.Option(None, "--from", help="Start block"),
    to_block: int = typer.Option(None, "--to", help="End block"),
    limit: int = typer.Option(100, "--limit", "-n", help="Max events"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """Query historical events."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    try:
        client = MidnightClient(network=profile_obj.name)
        
        filters = {}
        if contract:
            filters["contract"] = contract
        if event_type:
            filters["type"] = event_type
        if from_block:
            filters["from_block"] = from_block
        if to_block:
            filters["to_block"] = to_block
        
        events = client.indexer.query_events(filters, limit)
        
        for event in events:
            console.print(json.dumps(event, indent=2))
            console.print("---")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
