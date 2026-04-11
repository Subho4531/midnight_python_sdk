#!/usr/bin/env python3
"""
Verification script for Midnight SDK installation.
"""

import sys
from typing import List, Tuple
from rich.console import Console
from rich.table import Table

console = Console()


def check_dependencies() -> List[Tuple[str, bool, str]]:
    """Check if all required dependencies are available."""
    results = []
    
    # Core dependencies
    deps = [
        ("httpx", "HTTP client for API calls"),
        ("websockets", "WebSocket support for real-time updates"),
        ("pydantic", "Data validation and serialization"),
        ("typer", "CLI framework"),
        ("rich", "Rich text and beautiful formatting"),
        ("mnemonic", "BIP39 mnemonic phrase support"),
        ("scikit-learn", "Machine learning for AI inference"),
        ("numpy", "Numerical computing"),
        ("pandas", "Data manipulation"),
        ("yaml", "YAML configuration support"),
    ]
    
    for dep, description in deps:
        try:
            if dep == "yaml":
                import yaml
            else:
                __import__(dep)
            results.append((dep, True, description))
        except ImportError:
            results.append((dep, False, description))
    
    return results


def check_midnight_sdk():
    """Check if Midnight SDK components are working."""
    try:
        from midnight_sdk import MidnightClient
        from midnight_sdk.cli import cli_main
        return True, "Midnight SDK imported successfully"
    except ImportError as e:
        return False, f"Failed to import Midnight SDK: {e}"


def main():
    """Run verification checks."""
    console.print("🌙 [bold blue]Midnight SDK Installation Verification[/bold blue]")
    console.print()
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 10):
        console.print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} (supported)")
    else:
        console.print(f"❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (requires 3.10+)")
        return False
    
    console.print()
    
    # Check dependencies
    console.print("[bold]Checking Dependencies:[/bold]")
    deps = check_dependencies()
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Package", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Description", style="dim")
    
    all_good = True
    for dep, available, description in deps:
        status = "✅ Available" if available else "❌ Missing"
        if not available:
            all_good = False
        table.add_row(dep, status, description)
    
    console.print(table)
    console.print()
    
    # Check Midnight SDK
    console.print("[bold]Checking Midnight SDK:[/bold]")
    sdk_ok, sdk_msg = check_midnight_sdk()
    if sdk_ok:
        console.print(f"✅ {sdk_msg}")
    else:
        console.print(f"❌ {sdk_msg}")
        all_good = False
    
    console.print()
    
    if all_good:
        console.print("🎉 [bold green]All checks passed! Midnight SDK is ready to use.[/bold green]")
        console.print()
        console.print("Try running: [bold cyan]midnight status[/bold cyan]")
        return True
    else:
        console.print("⚠️  [bold yellow]Some issues found. Install missing dependencies:[/bold yellow]")
        console.print("[bold cyan]pip install midnight-sdk[all][/bold cyan]")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)