"""Transaction management commands."""

import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import time

from ...client import MidnightClient
from ...config import ConfigManager
from ...builder import TransactionBuilder

app = typer.Typer(help="Transaction submission and management")
console = Console()


@app.command("submit")
def tx_submit(
    file: Path = typer.Argument(..., help="Signed transaction file"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """Submit signed transaction from file."""
    if not file.exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(1)
    
    try:
        signed_tx = json.loads(file.read_text())
    except json.JSONDecodeError:
        console.print("[red]Invalid JSON file[/red]")
        raise typer.Exit(1)
    
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    try:
        client = MidnightClient(network=profile_obj.name)
        result = client.wallet.submit_transaction(signed_tx)
        console.print(f"[green]✓[/green] Transaction submitted")
        console.print(f"[cyan]TX Hash:[/cyan] {result.tx_hash}")
    except Exception as e:
        console.print(f"[red]Submission failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("sign")
def tx_sign(
    file: Path = typer.Argument(..., help="Unsigned transaction file"),
    output: Path = typer.Option(None, "--output", "-o", help="Output file"),
    wallet: str = typer.Option(None, "--wallet", "-w", help="Wallet name"),
):
    """Sign transaction offline."""
    if not file.exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(1)
    
    try:
        unsigned_tx = json.loads(file.read_text())
    except json.JSONDecodeError:
        console.print("[red]Invalid JSON file[/red]")
        raise typer.Exit(1)
    
    config_mgr = ConfigManager()
    config_mgr.load()
    
    wallet_name = wallet or config_mgr.config.default_wallet
    if not wallet_name:
        console.print("[red]No wallet specified[/red]")
        raise typer.Exit(1)
    
    wallet_path = Path(config_mgr.config.wallets[wallet_name])
    mnemonic = wallet_path.read_text().strip()
    
    try:
        from ...wallet import WalletClient
        wallet_client = WalletClient()
        keys = wallet_client.get_private_keys(mnemonic)
        signed_tx = wallet_client.sign_transaction(unsigned_tx, keys["private_key"])
        
        output_file = output or file.with_suffix(".signed.json")
        output_file.write_text(json.dumps(signed_tx, indent=2))
        
        console.print(f"[green]✓[/green] Transaction signed")
        console.print(f"Output: {output_file}")
    except Exception as e:
        console.print(f"[red]Signing failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("status")
def tx_status(
    tx_hash: str = typer.Argument(..., help="Transaction hash"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """Get transaction status."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    try:
        client = MidnightClient(network=profile_obj.name)
        status = client.indexer.get_transaction_status(tx_hash)
        
        console.print(f"[cyan]TX Hash:[/cyan] {tx_hash}")
        console.print(f"[cyan]Status:[/cyan] {status.get('status', 'unknown')}")
        console.print(f"[cyan]Block:[/cyan] {status.get('block_number', 'pending')}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("list")
def tx_list(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of transactions"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """List recent transactions."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    try:
        client = MidnightClient(network=profile_obj.name)
        txs = client.indexer.get_recent_transactions(limit)
        
        table = Table(title="Recent Transactions")
        table.add_column("Hash", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Block", style="dim")
        
        for tx in txs:
            table.add_row(
                tx["hash"][:16] + "...",
                tx.get("type", "unknown"),
                tx.get("status", "pending"),
                str(tx.get("block", "-")),
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("watch")
def tx_watch(
    tx_hash: str = typer.Argument(..., help="Transaction hash"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
    timeout: int = typer.Option(60, "--timeout", help="Timeout in seconds"),
):
    """Watch transaction until finality."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    client = MidnightClient(network=profile_obj.name)
    
    console.print(f"[cyan]Watching transaction {tx_hash}...[/cyan]")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            status = client.indexer.get_transaction_status(tx_hash)
            current_status = status.get("status", "pending")
            
            console.print(f"Status: {current_status}", end="\r")
            
            if current_status in ["finalized", "confirmed"]:
                console.print(f"\n[green]✓[/green] Transaction {current_status}")
                return
            
            time.sleep(2)
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            raise typer.Exit(1)
    
    console.print(f"\n[yellow]Timeout reached[/yellow]")


@app.command("decode")
def tx_decode(
    tx_hash: str = typer.Argument(..., help="Transaction hash"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """Decode transaction payload."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    try:
        client = MidnightClient(network=profile_obj.name)
        tx_data = client.indexer.get_transaction(tx_hash)
        console.print(json.dumps(tx_data, indent=2))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("history")
def tx_history(
    address: str = typer.Argument(..., help="Address"),
    limit: int = typer.Option(20, "--limit", "-n", help="Number of transactions"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """Transaction history for address."""
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    try:
        client = MidnightClient(network=profile_obj.name)
        txs = client.indexer.get_address_transactions(address, limit)
        
        table = Table(title=f"Transaction History for {address[:16]}...")
        table.add_column("Hash", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Amount", style="green", justify="right")
        table.add_column("Block", style="dim")
        
        for tx in txs:
            table.add_row(
                tx["hash"][:16] + "...",
                tx.get("type", "unknown"),
                str(tx.get("amount", "-")),
                str(tx.get("block", "-")),
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("build")
def tx_build(
    output: Path = typer.Option("unsigned_tx.json", "--output", "-o", help="Output file"),
):
    """Build unsigned transaction interactively."""
    console.print("[cyan]Transaction Builder[/cyan]\n")
    
    tx_type = typer.prompt("Transaction type (call/deploy/transfer)", type=str)
    
    builder = TransactionBuilder()
    
    if tx_type == "call":
        address = typer.prompt("Contract address")
        circuit = typer.prompt("Circuit name")
        args = typer.prompt("Arguments (JSON)", default="{}")
        builder.call_contract(address, circuit, json.loads(args))
    elif tx_type == "deploy":
        path = typer.prompt("Contract path")
        builder.deploy_contract(path)
    elif tx_type == "transfer":
        dest = typer.prompt("Destination address")
        amount = typer.prompt("Amount", type=int)
        builder.transfer(dest, amount)
    else:
        console.print("[red]Invalid transaction type[/red]")
        raise typer.Exit(1)
    
    nonce = typer.prompt("Nonce (optional)", default="", type=str)
    if nonce:
        builder.set_nonce(int(nonce))
    
    fee = typer.prompt("Fee (optional)", default="", type=str)
    if fee:
        builder.set_fee(int(fee))
    
    unsigned_tx = builder.build()
    output.write_text(json.dumps(unsigned_tx, indent=2))
    
    console.print(f"\n[green]✓[/green] Unsigned transaction saved to {output}")
