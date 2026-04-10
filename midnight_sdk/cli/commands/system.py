"""System health and diagnostics commands."""

import typer
from rich.console import Console
from rich.table import Table
import platform
import sys

from ...client import MidnightClient
from ...config import ConfigManager

app = typer.Typer(help="System health and diagnostics")
console = Console()


@app.command("status")
def system_status(profile: str = typer.Option(None, "--profile", "-p", help="Network profile")):
    """Check all service health."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    console.print(f"[cyan]Checking services on {profile_obj.name}...[/cyan]\n")
    
    try:
        client = MidnightClient(network=profile_obj.name)
        status = client.status()
        
        table = Table(title="Service Status")
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("URL", style="dim")
        
        services = [
            ("Node", status["node"], profile_obj.node_url),
            ("Indexer", status["indexer"], profile_obj.indexer_url),
            ("Proof Server", status["prover"], profile_obj.proof_server_url),
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


@app.command("info")
def system_info():
    """Show SDK and environment information."""
    console.print("[cyan]Midnight SDK Information[/cyan]\n")
    
    table = Table()
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="yellow")
    
    # SDK info
    try:
        from ... import __version__
        sdk_version = __version__
    except:
        sdk_version = "0.1.0"
    
    table.add_row("SDK Version", sdk_version)
    table.add_row("Python Version", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    table.add_row("Platform", platform.system())
    table.add_row("Architecture", platform.machine())
    
    # Config location
    from pathlib import Path
    config_path = Path.home() / ".midnight" / "config.yaml"
    table.add_row("Config Path", str(config_path))
    table.add_row("Config Exists", "Yes" if config_path.exists() else "No")
    
    console.print(table)


@app.command("logs")
def system_logs(
    service: str = typer.Argument(None, help="Service name (node/indexer/proof)"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
    lines: int = typer.Option(50, "--lines", "-n", help="Number of lines"),
):
    """Tail service logs (for local Docker services)."""
    if not service:
        console.print("[yellow]Available services: node, indexer, proof[/yellow]")
        return
    
    service_map = {
        "node": "midnight-node",
        "indexer": "midnight-indexer",
        "proof": "midnight-proof-server",
    }
    
    if service not in service_map:
        console.print(f"[red]Unknown service: {service}[/red]")
        raise typer.Exit(1)
    
    container_name = service_map[service]
    
    import subprocess
    
    try:
        cmd = ["docker", "logs"]
        if follow:
            cmd.append("-f")
        cmd.extend(["--tail", str(lines), container_name])
        
        subprocess.run(cmd)
    except FileNotFoundError:
        console.print("[red]Docker not found. Is Docker installed?[/red]")
        raise typer.Exit(1)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error reading logs: {e}[/red]")
        raise typer.Exit(1)
