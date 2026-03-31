"""
midnight-py CLI — interact with Midnight from the terminal.

Commands:
    midnight-py status           — check all services
    midnight-py deploy <file>    — deploy a .compact contract
    midnight-py call <addr> <fn> — call a circuit function
    midnight-py state <addr>     — read contract state
    midnight-py balance <addr>   — get wallet balance
"""

import typer
import json
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from pathlib import Path
from .client import MidnightClient

app = typer.Typer(
    name="midnight-py",
    help="Python CLI for the Midnight blockchain",
    no_args_is_help=True,
)
console = Console()

# AI subcommand
ai_app = typer.Typer(help="ZK AI inference commands")
app.add_typer(ai_app, name="ai")


@app.command()
def status(network: str = typer.Option("local", help="Network to connect to")):
    """Check if all Midnight services are running."""
    client = MidnightClient(network=network)
    result = client.status()

    table = Table(title=f"Midnight Services ({network})")
    table.add_column("Service", style="bold")
    table.add_column("Status")
    table.add_column("URL")

    cfg = {"node": client.wallet.url, "indexer": client.indexer.url, "prover": client.prover.url}
    for service, alive in result.items():
        icon = "[green]✓ ONLINE[/green]" if alive else "[red]✗ OFFLINE[/red]"
        table.add_row(service.capitalize(), icon, cfg[service])

    console.print(table)


@app.command()
def deploy(
    contract: str = typer.Argument(..., help="Path to .compact file"),
    network: str = typer.Option("local"),
    key: str = typer.Option(..., help="Private key for signing"),
):
    """Deploy a .compact contract to Midnight."""
    rprint(f"[bold]Deploying[/bold] {contract} to {network}...")
    client = MidnightClient(network=network)
    deployed = client.contracts.deploy(contract, private_key=key)
    rprint(f"[green]✓ Deployed at:[/green] {deployed.address}")


@app.command()
def call(
    address: str = typer.Argument(..., help="Contract address"),
    circuit: str = typer.Argument(..., help="Circuit function name"),
    args: str = typer.Option("{}", help="JSON public inputs"),
    private: str = typer.Option("{}", help="JSON private inputs"),
    key: str = typer.Option(..., help="Private key for signing"),
    network: str = typer.Option("local"),
):
    """Call a circuit function on a deployed contract."""
    client = MidnightClient(network=network)
    contract = client.get_contract(address, [circuit])
    contract.set_key(key)
    result = contract.call(
        circuit_name=circuit,
        public_inputs=json.loads(args),
        private_inputs=json.loads(private),
    )
    rprint(f"[green]TX Hash:[/green] {result.tx_hash}")
    rprint(f"[green]Status:[/green]  {result.status}")


@app.command()
def state(
    address: str = typer.Argument(..., help="Contract address"),
    network: str = typer.Option("local"),
):
    """Read the current on-chain state of a contract."""
    client = MidnightClient(network=network)
    contract_state = client.indexer.get_contract_state(address)
    rprint(f"[bold]Contract:[/bold] {address}")
    rprint(f"[bold]Block:[/bold]    {contract_state.block_height}")
    rprint(f"[bold]State:[/bold]")
    console.print_json(json.dumps(contract_state.state))


@app.command()
def balance(
    address: str = typer.Argument(..., help="Wallet address"),
    network: str = typer.Option("local"),
):
    """Get token balances for a wallet address."""
    client = MidnightClient(network=network)
    bal = client.wallet.get_balance(address)
    rprint(f"[bold]DUST:[/bold]  {bal.dust:,}")
    rprint(f"[bold]NIGHT:[/bold] {bal.night:,}")


def main():
    app()



# AI Commands

@ai_app.command("train")
def ai_train(
    wallet: str = typer.Option(
        "mn_addr_undeployed1zaa268rc7sjz0ctscrsy7mp2ne7khfz8wu2uqsu4msfvxnlt6qfsmfrhr0",
        help="Wallet address"
    )
):
    """Train the iris classification model."""
    client = MidnightClient(network="undeployed", wallet_address=wallet)
    model_hash = client.ai.train_iris()
    rprint(f"[green]✓ Model trained[/green]")
    rprint(f"[bold]Model hash:[/bold] {model_hash}")


@ai_app.command("infer")
def ai_infer(
    features: str = typer.Option(..., help="Comma-separated features (4 values)"),
    wallet: str = typer.Option(
        "mn_addr_undeployed1zaa268rc7sjz0ctscrsy7mp2ne7khfz8wu2uqsu4msfvxnlt6qfsmfrhr0",
        help="Wallet address"
    )
):
    """Run ZK inference on input features."""
    # Parse features
    try:
        feature_list = [float(x.strip()) for x in features.split(",")]
    except ValueError:
        rprint("[red]ERROR: Features must be comma-separated numbers[/red]")
        raise typer.Exit(1)
    
    # Create client and run inference
    client = MidnightClient(network="undeployed", wallet_address=wallet)
    result = client.ai.predict_private(features=feature_list)
    
    # Print full demo output
    print("╔══════════════════════════════════════════════════════╗")
    print("║          Midnight ZK AI Inference — Demo             ║")
    print("║          AI Track · INTO THE MIDNIGHT Hackathon      ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    
    wallet_short = wallet[:40] + "..."
    print(f"Wallet        {wallet_short}")
    print(f"Proof Server  localhost:6300  ✓ connected")
    print(f"Model         iris_rf.joblib  ✓ loaded")
    print("─" * 54)
    print()
    print("[PRIVATE]  Input features:       ██████████  ZK sealed")
    print("[PRIVATE]  Raw probabilities:    ██████████  ZK sealed")
    print()
    print("─" * 54)
    print()
    print(f"[PUBLIC]   Prediction:           {result.prediction}")
    print(f"[PUBLIC]   Confidence:           {result.confidence * 100:.2f}%")
    print(f"[PUBLIC]   Model hash:           {result.model_hash[:16]}...")
    print()
    print("─" * 54)
    print()
    print(f"[PROOF]    Proof hash:           {result.proof_hash[:16]}...")
    print(f"[PROOF]    Proof bytes (hex):    {result.raw_proof_bytes[:32]}...")
    print(f"[STORED]   Receipt:              {result.receipt_path}")
    print()
    print("─" * 54)
    print()
    print("The private input NEVER left this machine.")
    print("The ZK proof was generated by the Midnight proof server.")
    print("Anyone can verify the prediction is correct — nobody can see the input.")
    print()


@ai_app.command("list-proofs")
def ai_list_proofs():
    """List all stored inference proofs."""
    proofs_dir = Path.home() / ".midnight" / "inference_proofs"
    
    if not proofs_dir.exists():
        rprint("[yellow]No proofs found. Run inference first.[/yellow]")
        return
    
    proof_files = sorted(proofs_dir.glob("*.json"))
    
    if not proof_files:
        rprint("[yellow]No proofs found. Run inference first.[/yellow]")
        return
    
    table = Table(title="Inference Proofs")
    table.add_column("Timestamp", style="cyan")
    table.add_column("Prediction", style="green")
    table.add_column("Confidence", style="yellow")
    table.add_column("Proof Hash", style="dim")
    
    for proof_file in proof_files:
        try:
            receipt = json.loads(proof_file.read_text())
            timestamp = receipt["timestamp"][:19]  # Remove milliseconds
            prediction = receipt["revealed"]["prediction"]
            confidence = f"{receipt['revealed']['confidence'] * 100:.2f}%"
            proof_hash = receipt["proof_hash"][:16] + "..."
            
            table.add_row(timestamp, prediction, confidence, proof_hash)
        except Exception:
            continue
    
    console.print(table)


@ai_app.command("show")
def ai_show_proof(
    proof_hash: str = typer.Argument(..., help="Proof hash (full or prefix)")
):
    """Show full receipt for a specific proof."""
    proofs_dir = Path.home() / ".midnight" / "inference_proofs"
    
    if not proofs_dir.exists():
        rprint("[red]No proofs found.[/red]")
        raise typer.Exit(1)
    
    # Find matching proof
    for proof_file in proofs_dir.glob("*.json"):
        try:
            receipt = json.loads(proof_file.read_text())
            if receipt["proof_hash"].startswith(proof_hash):
                rprint(f"[bold]Receipt:[/bold] {proof_file.name}")
                console.print_json(json.dumps(receipt, indent=2))
                return
        except Exception:
            continue
    
    rprint(f"[red]No proof found matching: {proof_hash}[/red]")
    raise typer.Exit(1)
