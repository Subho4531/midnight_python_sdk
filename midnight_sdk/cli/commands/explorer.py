"""Explorer integration commands."""

import typer
from rich.console import Console
import webbrowser

from ...config import ConfigManager

app = typer.Typer(help="Explorer integration")
console = Console()


@app.command("open")
def explorer_open(
    tx_hash: str = typer.Argument(None, help="Transaction hash"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """Open explorer in browser."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    if not profile_obj.explorer_url:
        console.print("[yellow]No explorer URL configured for this network[/yellow]")
        return
    
    url = profile_obj.explorer_url
    if tx_hash:
        url = f"{url}/tx/{tx_hash}"
    
    console.print(f"[cyan]Opening:[/cyan] {url}")
    webbrowser.open(url)


@app.command("address")
def explorer_address(
    address: str = typer.Argument(..., help="Address"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """View address in explorer."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    if not profile_obj.explorer_url:
        console.print("[yellow]No explorer URL configured for this network[/yellow]")
        return
    
    url = f"{profile_obj.explorer_url}/address/{address}"
    console.print(f"[cyan]Opening:[/cyan] {url}")
    webbrowser.open(url)


@app.command("block")
def explorer_block(
    number: int = typer.Argument(..., help="Block number"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """View block in explorer."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    if not profile_obj.explorer_url:
        console.print("[yellow]No explorer URL configured for this network[/yellow]")
        return
    
    url = f"{profile_obj.explorer_url}/block/{number}"
    console.print(f"[cyan]Opening:[/cyan] {url}")
    webbrowser.open(url)
