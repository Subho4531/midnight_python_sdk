"""Node RPC interaction commands."""

import typer
from rich.console import Console
import json
import httpx

from ...config import ConfigManager

app = typer.Typer(help="Raw node RPC interaction")
console = Console()


@app.command("status")
def node_status(profile: str = typer.Option(None, "--profile", "-p", help="Network profile")):
    """Get node sync status."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    try:
        response = httpx.get(f"{profile_obj.node_url}/status", timeout=10)
        response.raise_for_status()
        status = response.json()
        console.print(json.dumps(status, indent=2))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("peers")
def node_peers(profile: str = typer.Option(None, "--profile", "-p", help="Network profile")):
    """List connected peers."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    try:
        response = httpx.get(f"{profile_obj.node_url}/peers", timeout=10)
        response.raise_for_status()
        peers = response.json()
        console.print(json.dumps(peers, indent=2))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("rpc")
def node_rpc(
    method: str = typer.Argument(..., help="RPC method"),
    params: str = typer.Option("[]", "--params", help="JSON params array"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """Call raw JSON-RPC method."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    try:
        params_list = json.loads(params)
    except json.JSONDecodeError:
        console.print("[red]Invalid JSON params[/red]")
        raise typer.Exit(1)
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params_list,
    }
    
    try:
        response = httpx.post(profile_obj.node_url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]RPC call failed: {e}[/red]")
        raise typer.Exit(1)
