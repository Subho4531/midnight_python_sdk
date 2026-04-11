#!/usr/bin/env python3
"""
Build script for preparing Midnight SDK for PyPI distribution.
"""

import subprocess
import sys
from pathlib import Path
from rich.console import Console

console = Console()


def run_command(cmd: str, description: str) -> bool:
    """Run a command and return success status."""
    console.print(f"[cyan]{description}...[/cyan]")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        console.print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"❌ {description} failed:")
        console.print(f"[red]{e.stderr}[/red]")
        return False


def main():
    """Main build process."""
    console.print("🌙 [bold blue]Building Midnight SDK for PyPI[/bold blue]\n")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        console.print("❌ pyproject.toml not found. Run from project root.")
        return False
    
    # Clean previous builds
    console.print("[bold]Cleaning previous builds...[/bold]")
    for path in ["build/", "dist/", "*.egg-info/"]:
        if Path(path.rstrip("/")).exists():
            run_command(f"rm -rf {path}", f"Removing {path}")
    
    # Install build dependencies
    if not run_command("pip install build twine", "Installing build tools"):
        return False
    
    # Run linting
    console.print("\n[bold]Running code quality checks...[/bold]")
    if not run_command("ruff check midnight_sdk/", "Linting with ruff"):
        console.print("[yellow]⚠️  Linting issues found, but continuing...[/yellow]")
    
    # Run type checking
    if not run_command("mypy midnight_sdk/ --ignore-missing-imports", "Type checking with mypy"):
        console.print("[yellow]⚠️  Type checking issues found, but continuing...[/yellow]")
    
    # Build the package
    console.print("\n[bold]Building package...[/bold]")
    if not run_command("python -m build", "Building wheel and source distribution"):
        return False
    
    # Check the package
    console.print("\n[bold]Checking package...[/bold]")
    if not run_command("twine check dist/*", "Validating package"):
        return False
    
    # Show build results
    console.print("\n[bold green]✅ Build completed successfully![/bold green]")
    console.print("\n[bold]Build artifacts:[/bold]")
    
    dist_files = list(Path("dist").glob("*"))
    for file in dist_files:
        size = file.stat().st_size / 1024  # KB
        console.print(f"  📦 {file.name} ({size:.1f} KB)")
    
    console.print("\n[bold]Next steps:[/bold]")
    console.print("1. Test the package: [cyan]pip install dist/*.whl[/cyan]")
    console.print("2. Upload to TestPyPI: [cyan]twine upload --repository testpypi dist/*[/cyan]")
    console.print("3. Upload to PyPI: [cyan]twine upload dist/*[/cyan]")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)