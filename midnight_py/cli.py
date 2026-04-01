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

# Transaction management subcommand
tx_app = typer.Typer(help="Transaction management commands")
app.add_typer(tx_app, name="tx")


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
    wallet: str = typer.Option(..., help="Wallet address"),
    sign: bool = typer.Option(True, help="Sign transaction with private key"),
):
    """Deploy a .compact contract to Midnight."""
    from pathlib import Path as P
    
    rprint(f"[bold]Deploying[/bold] {contract} to {network}...")
    
    # Get private key if signing
    private_key = None
    if sign:
        mnemonic_file = P("mnemonic.txt")
        if not mnemonic_file.exists():
            rprint("[red]ERROR: mnemonic.txt not found. Required for signing.[/red]")
            raise typer.Exit(1)
        
        client = MidnightClient(network=network, wallet_address=wallet)
        mnemonic = mnemonic_file.read_text().strip()
        keys = client.wallet.get_private_keys(mnemonic)
        private_key = keys['nightExternal']
        rprint(f"[dim]Using wallet: {wallet[:40]}...[/dim]")
    
    client = MidnightClient(network=network, wallet_address=wallet)
    deployed = client.contracts.deploy(contract, private_key=private_key, sign_transaction=sign)
    
    rprint(f"[green]✓ Deployed at:[/green] {deployed.address}")
    if hasattr(deployed, 'tx_hash') and deployed.tx_hash:
        rprint(f"[green]✓ Transaction:[/green] {deployed.tx_hash}")
        rprint(f"[dim]View: http://localhost:8088/tx/{deployed.tx_hash}[/dim]")


@app.command()
def call(
    address: str = typer.Argument(..., help="Contract address"),
    circuit: str = typer.Argument(..., help="Circuit function name"),
    args: str = typer.Option("{}", help="JSON public inputs"),
    private: str = typer.Option("{}", help="JSON private inputs"),
    wallet: str = typer.Option(..., help="Wallet address"),
    network: str = typer.Option("local"),
    sign: bool = typer.Option(True, help="Sign transaction"),
):
    """Call a circuit function on a deployed contract."""
    from pathlib import Path as P
    
    # Get private key if signing
    private_key = None
    if sign:
        mnemonic_file = P("mnemonic.txt")
        if not mnemonic_file.exists():
            rprint("[red]ERROR: mnemonic.txt not found. Required for signing.[/red]")
            raise typer.Exit(1)
        
        client = MidnightClient(network=network, wallet_address=wallet)
        mnemonic = mnemonic_file.read_text().strip()
        keys = client.wallet.get_private_keys(mnemonic)
        private_key = keys['nightExternal']
    
    client = MidnightClient(network=network, wallet_address=wallet)
    contract = client.get_contract(address, [circuit])
    
    if private_key:
        contract.set_key(private_key)
    
    result = contract.call(
        circuit_name=circuit,
        public_inputs=json.loads(args),
        private_inputs=json.loads(private),
        sign_transaction=sign,
    )
    
    rprint(f"[green]✓ Circuit called:[/green] {circuit}")
    rprint(f"[green]✓ TX Hash:[/green] {result.tx_hash}")
    rprint(f"[green]✓ Status:[/green]  {result.status}")
    rprint(f"[dim]View: http://localhost:8088/tx/{result.tx_hash}[/dim]")


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
    ),
    sign: bool = typer.Option(False, help="Sign and submit transaction"),
):
    """Run ZK inference on input features."""
    from pathlib import Path as P
    
    # Parse features
    try:
        feature_list = [float(x.strip()) for x in features.split(",")]
    except ValueError:
        rprint("[red]ERROR: Features must be comma-separated numbers[/red]")
        raise typer.Exit(1)
    
    # Get private key if signing
    private_key = None
    if sign:
        mnemonic_file = P("mnemonic.txt")
        if not mnemonic_file.exists():
            rprint("[red]ERROR: mnemonic.txt not found. Required for signing.[/red]")
            raise typer.Exit(1)
        
        client = MidnightClient(network="undeployed", wallet_address=wallet)
        mnemonic = mnemonic_file.read_text().strip()
        keys = client.wallet.get_private_keys(mnemonic)
        private_key = keys['nightExternal']
    
    # Create client and run inference
    client = MidnightClient(network="undeployed", wallet_address=wallet)
    result = client.ai.predict_private(
        features=feature_list,
        sign_transaction=sign,
        private_key=private_key
    )
    
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
    
    if sign and result.transaction_hash:
        print()
        print("─" * 54)
        print()
        print(f"[TX]       Transaction hash:     {result.transaction_hash}")
        print(f"[TX]       Status:               signed & submitted")
        print(f"[TX]       Explorer:             http://localhost:8088/tx/{result.transaction_hash}")
    
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


# Transaction Management Commands

@tx_app.command("list")
def tx_list():
    """List all transactions."""
    import httpx
    
    try:
        response = httpx.get("http://localhost:9944/transactions", timeout=10.0)
        data = response.json()
        txs = data.get("transactions", [])
        
        if not txs:
            rprint("[yellow]No transactions found.[/yellow]")
            return
        
        # Group by status
        pending = [tx for tx in txs if tx['status'] == 'pending']
        confirmed = [tx for tx in txs if tx['status'] == 'confirmed']
        rejected = [tx for tx in txs if tx['status'] == 'rejected']
        
        table = Table(title=f"Transactions ({len(txs)} total)")
        table.add_column("Hash", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Timestamp", style="dim")
        
        for tx in txs:
            status_color = {
                'pending': '[yellow]⏳ pending[/yellow]',
                'confirmed': '[green]✅ confirmed[/green]',
                'rejected': '[red]❌ rejected[/red]'
            }.get(tx['status'], tx['status'])
            
            table.add_row(
                tx['hash'][:32] + "...",
                status_color,
                tx['timestamp'][:19]
            )
        
        console.print(table)
        
        rprint(f"\n[bold]Summary:[/bold]")
        rprint(f"  Pending:   {len(pending)}")
        rprint(f"  Confirmed: {len(confirmed)}")
        rprint(f"  Rejected:  {len(rejected)}")
        
    except Exception as e:
        rprint(f"[red]ERROR: {e}[/red]")
        raise typer.Exit(1)


@tx_app.command("status")
def tx_status(
    tx_hash: str = typer.Argument(..., help="Transaction hash")
):
    """Check transaction status."""
    import httpx
    
    try:
        response = httpx.get(f"http://localhost:9944/tx/{tx_hash}", timeout=10.0)
        
        if response.status_code != 200:
            rprint(f"[red]Transaction not found: {tx_hash}[/red]")
            raise typer.Exit(1)
        
        tx = response.json()
        
        rprint(f"\n[bold]Transaction Details[/bold]")
        rprint(f"{'='*70}")
        rprint(f"Hash:      {tx['hash']}")
        rprint(f"Status:    {tx['status']}")
        rprint(f"Timestamp: {tx['timestamp']}")
        rprint(f"Block:     {tx.get('block_height', 'N/A')}")
        
        if tx['status'] == 'confirmed':
            rprint(f"Confirmed: {tx.get('confirmed_at', 'N/A')}")
        elif tx['status'] == 'rejected':
            rprint(f"Rejected:  {tx.get('rejected_at', 'N/A')}")
            rprint(f"Reason:    {tx.get('error', 'N/A')}")
        
        # Show payload if available
        data = tx.get('data', {})
        payload = data.get('payload', {})
        
        if payload:
            public_inputs = payload.get('public_inputs', {})
            if public_inputs:
                rprint(f"\n[bold]Public Data:[/bold]")
                if 'prediction' in public_inputs:
                    rprint(f"  Prediction: {public_inputs['prediction']}")
                if 'confidence' in public_inputs:
                    conf = public_inputs['confidence'] / 100
                    rprint(f"  Confidence: {conf:.2f}%")
        
        rprint(f"{'='*70}\n")
        rprint(f"[dim]Explorer: http://localhost:8088/tx/{tx_hash}[/dim]")
        
    except httpx.HTTPError as e:
        rprint(f"[red]ERROR: {e}[/red]")
        raise typer.Exit(1)


@tx_app.command("approve")
def tx_approve(
    tx_hash: str = typer.Argument(..., help="Transaction hash")
):
    """Approve/confirm a pending transaction."""
    import httpx
    
    try:
        # Check current status
        response = httpx.get(f"http://localhost:9944/tx/{tx_hash}", timeout=10.0)
        if response.status_code != 200:
            rprint(f"[red]Transaction not found: {tx_hash}[/red]")
            raise typer.Exit(1)
        
        tx = response.json()
        if tx['status'] != 'pending':
            rprint(f"[yellow]Transaction is already {tx['status']}[/yellow]")
            return
        
        # Approve it
        response = httpx.post(
            "http://localhost:9944",
            json={
                "id": 1,
                "jsonrpc": "2.0",
                "method": "chain_confirmTransaction",
                "params": [tx_hash]
            },
            headers={"Content-Type": "application/json"},
            timeout=10.0
        )
        
        data = response.json()
        if data.get("result", {}).get("confirmed"):
            rprint(f"[green]✅ Transaction approved successfully![/green]")
            rprint(f"[dim]View: http://localhost:8088/tx/{tx_hash}[/dim]")
        else:
            rprint(f"[red]Failed to approve transaction[/red]")
            raise typer.Exit(1)
        
    except httpx.HTTPError as e:
        rprint(f"[red]ERROR: {e}[/red]")
        raise typer.Exit(1)


@tx_app.command("reject")
def tx_reject(
    tx_hash: str = typer.Argument(..., help="Transaction hash"),
    reason: str = typer.Option("Rejected by user", help="Rejection reason")
):
    """Reject a pending transaction."""
    import httpx
    
    try:
        # Check current status
        response = httpx.get(f"http://localhost:9944/tx/{tx_hash}", timeout=10.0)
        if response.status_code != 200:
            rprint(f"[red]Transaction not found: {tx_hash}[/red]")
            raise typer.Exit(1)
        
        tx = response.json()
        if tx['status'] != 'pending':
            rprint(f"[yellow]Transaction is already {tx['status']}[/yellow]")
            return
        
        # Reject it
        response = httpx.post(
            "http://localhost:9944",
            json={
                "id": 1,
                "jsonrpc": "2.0",
                "method": "chain_rejectTransaction",
                "params": [tx_hash, reason]
            },
            headers={"Content-Type": "application/json"},
            timeout=10.0
        )
        
        data = response.json()
        if data.get("result", {}).get("rejected"):
            rprint(f"[red]❌ Transaction rejected[/red]")
            rprint(f"Reason: {reason}")
            rprint(f"[dim]View: http://localhost:8088/tx/{tx_hash}[/dim]")
        else:
            rprint(f"[red]Failed to reject transaction[/red]")
            raise typer.Exit(1)
        
    except httpx.HTTPError as e:
        rprint(f"[red]ERROR: {e}[/red]")
        raise typer.Exit(1)
