"""Interactive REPL console."""

import typer
from rich.console import Console

app = typer.Typer(help="Interactive REPL console")
console = Console()


@app.command()
def console_repl(profile: str = typer.Option(None, "--profile", "-p", help="Network profile")):
    """Start interactive Python console with SDK preloaded."""
    try:
        from IPython import embed
        from ...client import MidnightClient
        from ...config import ConfigManager
        
        config_mgr = ConfigManager()
        config_mgr.load()
        profile_obj = config_mgr.get_profile(profile)
        
        # Create client
        client = MidnightClient(network=profile_obj.name)
        
        console.print(f"[cyan]Midnight SDK Console[/cyan]")
        console.print(f"[dim]Network: {profile_obj.name}[/dim]")
        console.print(f"[dim]Available: client, config_mgr[/dim]\n")
        
        # Start IPython with preloaded objects
        embed(colors="neutral", using="asyncio")
    except ImportError:
        console.print("[red]IPython not installed. Install with: pip install ipython[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
