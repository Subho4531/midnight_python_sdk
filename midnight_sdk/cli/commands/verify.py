"""
Verification commands for Midnight SDK.
"""

import typer
from typing import Optional
from rich.console import Console

from midnight_sdk.verify import main as verify_main

console = Console()


def verify_installation():
    """
    Verify Midnight SDK installation and dependencies.
    
    Checks Python version, required dependencies, and SDK components
    to ensure everything is properly installed and configured.
    """
    try:
        success = verify_main()
        if not success:
            raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n⚠️  Verification cancelled by user")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ Verification failed: {e}")
        raise typer.Exit(1)