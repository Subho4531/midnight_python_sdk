"""ZK proof generation and verification commands."""

import typer
from rich.console import Console
from pathlib import Path
import json

from ...client import MidnightClient
from ...config import ConfigManager

app = typer.Typer(help="ZK proof generation and verification")
console = Console()


@app.command("generate")
def proof_generate(
    circuit: str = typer.Argument(..., help="Circuit name"),
    inputs: str = typer.Argument(..., help="JSON inputs"),
    output: Path = typer.Option(None, "--output", "-o", help="Output proof file"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """Generate ZK proof for circuit."""
    try:
        inputs_dict = json.loads(inputs)
    except json.JSONDecodeError:
        console.print("[red]Invalid JSON inputs[/red]")
        raise typer.Exit(1)
    
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    try:
        with console.status("[cyan]Generating proof..."):
            client = MidnightClient(network=profile_obj.name)
            proof = client.prover.generate_proof(circuit, inputs_dict)
        
        if output:
            output.write_text(json.dumps(proof, indent=2))
            console.print(f"[green]✓[/green] Proof saved to {output}")
        else:
            console.print(json.dumps(proof, indent=2))
    except Exception as e:
        console.print(f"[red]Proof generation failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("verify")
def proof_verify(
    proof_file: Path = typer.Argument(..., help="Proof file"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """Verify ZK proof."""
    if not proof_file.exists():
        console.print(f"[red]File not found: {proof_file}[/red]")
        raise typer.Exit(1)
    
    try:
        proof = json.loads(proof_file.read_text())
    except json.JSONDecodeError:
        console.print("[red]Invalid JSON file[/red]")
        raise typer.Exit(1)
    
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    try:
        client = MidnightClient(network=profile_obj.name)
        is_valid = client.prover.verify_proof(proof)
        
        if is_valid:
            console.print("[green]✓[/green] Proof is valid")
        else:
            console.print("[red]✗[/red] Proof is invalid")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Verification failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("info")
def proof_info(
    circuit: str = typer.Argument(..., help="Circuit name"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """Show circuit information."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    try:
        client = MidnightClient(network=profile_obj.name)
        info = client.prover.get_circuit_info(circuit)
        console.print(json.dumps(info, indent=2))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
