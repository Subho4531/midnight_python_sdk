"""
midnight-py CLI — clean workflow for Midnight blockchain.

Commands:
  midnight-py status              — check all 3 services
  midnight-py balance <address>   — get wallet balance
  midnight-py block               — show latest block
  midnight-py deploy <contract>   — deploy a .compact contract
  midnight-py call <addr> <fn>    — call a circuit
  midnight-py state <addr>        — read contract state
  midnight-py tx get <hash>       — look up a transaction by hash

Usage examples:
  midnight-py status
  midnight-py balance mn_addr_undeployed1zaa268rc7sjz0cts...
  midnight-py block
  midnight-py deploy contracts/bulletin_board.compact --wallet mn_addr... --key YOUR_KEY
"""

import typer
import json
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from .client import MidnightClient

app     = typer.Typer(name="midnight-py", help="Python CLI for the Midnight blockchain", no_args_is_help=True)
tx_app  = typer.Typer(help="Transaction commands")
app.add_typer(tx_app, name="tx")
console = Console()


@app.command()
def networks():
    """List all available Midnight networks."""
    from .client import NETWORKS
    from .network_detector import NetworkDetector
    
    rprint("\n[bold]Available Midnight Networks[/bold]\n")
    
    detector = NetworkDetector({})
    
    table = Table(title="Midnight Networks")
    table.add_column("Network", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Status", style="green")
    table.add_column("Indexer URL", style="dim")
    
    for network_id, config in NETWORKS.items():
        network_info = detector.get_network_info(network_id)
        
        # Check if online
        try:
            import httpx
            response = httpx.post(
                config.indexer_url,
                json={"query": "{ __typename }"},
                headers={"Content-Type": "application/json"},
                timeout=3.0,
            )
            status = "🟢 Online" if response.status_code == 200 else "🔴 Offline"
        except Exception:
            status = "🔴 Offline"
        
        table.add_row(
            network_id,
            network_info['name'],
            status,
            config.indexer_url
        )
    
    console.print(table)
    
    rprint("\n[bold]Usage:[/bold]")
    rprint("  midnight-py balance <address>                    # Auto-detect network")
    rprint("  midnight-py balance <address> --network testnet  # Use specific network")
    rprint("  midnight-py status --network preprod             # Check network status")
    rprint()


@app.command()
def explore(
    address: str = typer.Argument(..., help="Wallet address to explore"),
):
    """Explore a wallet across all networks."""
    from .client import NETWORKS
    from .network_detector import NetworkDetector
    
    rprint(f"\n[bold]Exploring wallet across all networks...[/bold]")
    rprint(f"  Address: [cyan]{address[:40]}...[/cyan]\n")
    
    indexer_urls = {name: cfg.indexer_url for name, cfg in NETWORKS.items()}
    detector = NetworkDetector(indexer_urls)
    
    table = Table(title=f"Wallet on All Networks")
    table.add_column("Network", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("DUST Balance", style="green")
    table.add_column("Latest Block", style="dim")
    
    found_on = []
    
    for network in detector.NETWORKS_TO_TRY:
        if network not in NETWORKS:
            continue
        
        try:
            client = MidnightClient(network=network)
            
            # Check if indexer is alive
            if not client.indexer.is_alive():
                table.add_row(network, "🔴 Offline", "-", "-")
                continue
            
            # Get balance
            balance = client.indexer.get_balance(address)
            
            # Get latest block
            block = client.indexer.get_latest_block()
            block_height = str(block.get('height', '-')) if block else '-'
            
            if balance.dust > 0:
                status = "✅ Funded"
                found_on.append(network)
            else:
                status = "⚪ Empty"
            
            table.add_row(
                network,
                status,
                f"{balance.dust:,}",
                block_height
            )
            
        except Exception as e:
            table.add_row(network, f"❌ Error", "-", "-")
    
    console.print(table)
    
    if found_on:
        rprint(f"\n[bold green]✅ Wallet found on: {', '.join(found_on)}[/bold green]")
    else:
        rprint(f"\n[yellow]⚠️  Wallet not funded on any network[/yellow]")
    
    rprint()


@app.command()
def status(network: str = typer.Option("local", help="local | preprod")):
    """Check if all Midnight services are running."""
    client = MidnightClient(network=network)
    status_data = client.status()

    table = Table(title=f"Midnight Services ({network})")
    table.add_column("Service", style="bold")
    table.add_column("Status")
    table.add_column("URL")

    urls = {
        "node":    client.wallet.url,
        "indexer": client.indexer.url,
        "prover":  client.prover.url,
    }
    for svc, ok in status_data.items():
        icon = "[green]ONLINE[/green]" if ok else "[red]OFFLINE[/red]"
        mark = "[green]✓[/green]" if ok else "[red]✗[/red]"
        table.add_row(svc.capitalize(), f"{mark} {'ONLINE' if ok else 'OFFLINE'}", urls.get(svc, ""))
    console.print(table)


@app.command()
def balance(
    address: str = typer.Argument(..., help="Wallet address (mn_addr_undeployed1... or mn_preprod1...)"),
    network: str = typer.Option(None, help="Network (auto-detect if not specified)"),
    auto: bool = typer.Option(True, help="Auto-detect network"),
    use_wallet_sdk: bool = typer.Option(False, help="Use wallet SDK for real NIGHT balance"),
):
    """Get wallet balance. Auto-detects which network has your wallet."""
    import os
    from .network_detector import NetworkDetector
    
    # Check if using wallet SDK
    if use_wallet_sdk:
        if not os.environ.get("MNEMONIC"):
            rprint("\n[red]❌ MNEMONIC environment variable not set[/red]")
            rprint("\n[yellow]To see real NIGHT balance, set your mnemonic:[/yellow]")
            rprint('  [dim]PowerShell:[/dim] $env:MNEMONIC = "your 24 words here"')
            rprint('  [dim]Bash:[/dim]       export MNEMONIC="your 24 words here"')
            rprint("\nThen run:")
            rprint(f"  midnight-py balance {address} --use-wallet-sdk")
            rprint()
            raise typer.Exit(1)
        
        # Use wallet SDK for real balance
        client = MidnightClient(network=network or "undeployed")
        
        rprint(f"\n[bold]Reading balance with Midnight Wallet SDK...[/bold]")
        rprint(f"  Address: [cyan]{address[:40]}...[/cyan]")
        rprint(f"  Network: [cyan]{network or 'undeployed'}[/cyan]")
        rprint(f"\n[dim]Syncing with indexer... (this takes 10-30 seconds)[/dim]\n")
        
        bal = client.wallet.get_balance(address)
        
        rprint(f"[bold]Balance:[/bold]")
        rprint(f"  NIGHT: [green]{bal.night:,}[/green]")
        rprint(f"  DUST:  [green]{bal.dust:,}[/green]")
        rprint()
        return
    
    # If network specified, use it directly
    if network and not auto:
        client = MidnightClient(network=network)
        
        rprint(f"\n[bold]Checking balance on {network}:[/bold]")
        rprint(f"  Address: [cyan]{address[:40]}...[/cyan]")
        rprint(f"  Indexer: [dim]{client.indexer.url}[/dim]\n")
        
        bal = client.indexer.get_balance(address)
        rprint(f"  DUST (unshielded): [green]{bal.dust:,}[/green]")
        rprint(f"  NIGHT (shielded):  [yellow]Requires viewing key[/yellow]")
        
        rprint(f"\n[dim]💡 To see real NIGHT balance, use:[/dim]")
        rprint(f"[dim]   midnight-py balance {address} --use-wallet-sdk[/dim]")
        
        block = client.indexer.get_latest_block()
        if block:
            rprint(f"\n  Latest block: [cyan]{block.get('height', 'unknown')}[/cyan]")
        
        return
    
    # Auto-detect network
    rprint(f"\n[bold]Auto-detecting network for wallet...[/bold]")
    rprint(f"  Address: [cyan]{address[:40]}...[/cyan]\n")
    
    # Build indexer URLs from all networks
    from .client import NETWORKS
    indexer_urls = {name: cfg.indexer_url for name, cfg in NETWORKS.items()}
    
    detector = NetworkDetector(indexer_urls)
    detected_network, balance = detector.get_balance_from_any_network(address)
    
    if not detected_network:
        rprint("\n[red]❌ Wallet not found on any network[/red]")
        rprint("\n[yellow]Possible reasons:[/yellow]")
        rprint("  1. Wallet address is incorrect")
        rprint("  2. Wallet is not funded on any network")
        rprint("  3. Network services are offline")
        rprint("\n[dim]Try specifying a network manually:[/dim]")
        rprint("  midnight-py balance <address> --network testnet --no-auto")
        return
    
    # Show results
    network_info = detector.get_network_info(detected_network)
    
    rprint(f"\n[bold green]✅ Found on {network_info['name']}![/bold green]")
    rprint(f"  Network: [cyan]{detected_network}[/cyan]")
    rprint(f"  Description: [dim]{network_info['description']}[/dim]")
    
    if network_info.get('explorer'):
        rprint(f"  Explorer: [dim]{network_info['explorer']}[/dim]")
    
    rprint(f"\n[bold]Balance:[/bold]")
    rprint(f"  DUST (unshielded): [green]{balance.dust:,}[/green]")
    rprint(f"  NIGHT (shielded):  [yellow]Requires viewing key[/yellow]")
    
    rprint(f"\n[dim]NIGHT tokens are shielded — privacy by design![/dim]")
    rprint(f"[dim]The indexer cannot reveal shielded amounts without your viewing key.[/dim]")
    
    rprint(f"\n[dim]💡 To see real NIGHT balance, use:[/dim]")
    rprint(f"[dim]   midnight-py balance {address} --use-wallet-sdk[/dim]")
    
    # Get latest block
    client = MidnightClient(network=detected_network)
    block = client.indexer.get_latest_block()
    if block:
        rprint(f"\n  Latest block: [cyan]{block.get('height', 'unknown')}[/cyan]")
    
    rprint()


@app.command()
def block(network: str = typer.Option("local", help="local | preprod")):
    """Show the latest block on the chain."""
    client = MidnightClient(network=network)
    b = client.indexer.get_latest_block()
    if b:
        rprint(f"\n  [bold]Latest block[/bold]")
        rprint(f"  Height:    [cyan]{b.get('height', 'unknown')}[/cyan]")
        rprint(f"  Hash:      [dim]{b.get('hash', 'unknown')}[/dim]")
        rprint(f"  Timestamp: {b.get('timestamp', 'unknown')}")
    else:
        rprint("[yellow]Could not get latest block. Is the indexer running?[/yellow]")


@app.command()
def deploy(
    contract: str  = typer.Argument(..., help="Path to .compact file"),
    wallet:   str  = typer.Option(...,  help="Your wallet address"),
    key:      str  = typer.Option("",   help="Private key (or set MIDNIGHT_KEY env var)"),
    network:  str  = typer.Option("local"),
    sign:     bool = typer.Option(True,  help="Sign the transaction"),
):
    """Deploy a .compact contract to Midnight."""
    import os
    private_key = key or os.environ.get("MIDNIGHT_KEY", "")
    if not private_key and sign:
        rprint("[red]No private key. Use --key or set MIDNIGHT_KEY env var.[/red]")
        raise typer.Exit(1)

    rprint(f"\n[bold]Deploying:[/bold] {contract}")
    rprint(f"[dim]Network: {network} | Wallet: {wallet[:30]}...[/dim]\n")

    client = MidnightClient(network=network)
    try:
        deployed = client.contracts.deploy(contract, private_key=private_key)
        rprint(f"  [green]Deployed at:[/green] [cyan]{deployed.address}[/cyan]")
        rprint(f"  [dim]Save this address to interact with the contract[/dim]")
    except Exception as e:
        rprint(f"  [red]Deploy failed: {e}[/red]")


@app.command()
def call(
    address: str = typer.Argument(..., help="Contract address"),
    circuit: str = typer.Argument(..., help="Circuit function name"),
    args:    str = typer.Option("{}", help="JSON public inputs"),
    private: str = typer.Option("{}", help="JSON private inputs"),
    key:     str = typer.Option("",  help="Private key"),
    network: str = typer.Option("local"),
):
    """Call a circuit function on a deployed contract."""
    import os
    private_key = key or os.environ.get("MIDNIGHT_KEY", "")
    if not private_key:
        rprint("[red]No private key. Use --key or set MIDNIGHT_KEY env var.[/red]")
        raise typer.Exit(1)

    client  = MidnightClient(network=network)
    contract = client.get_contract(address, [circuit])
    contract.set_key(private_key)

    rprint(f"\n[bold]Calling:[/bold] {circuit} on {address[:30]}...")
    try:
        result = contract.call(
            circuit_name=circuit,
            public_inputs=json.loads(args),
            private_inputs=json.loads(private),
        )
        rprint(f"  [green]TX Hash:[/green] [cyan]{result.tx_hash}[/cyan]")
        rprint(f"  Status:  [green]{result.status}[/green]")
    except Exception as e:
        rprint(f"  [red]Call failed: {e}[/red]")


@app.command()
def state(
    address: str = typer.Argument(..., help="Contract address"),
    network: str = typer.Option("local"),
):
    """Read the current on-chain state of a contract."""
    client = MidnightClient(network=network)
    try:
        s = client.indexer.get_contract_state(address)
        rprint(f"\n  [bold]Contract:[/bold] [cyan]{address}[/cyan]")
        rprint(f"  Block:   [cyan]{s.block_height}[/cyan]")
        rprint(f"  State:")
        console.print_json(json.dumps(s.state))
    except Exception as e:
        rprint(f"  [red]State query failed: {e}[/red]")


@tx_app.command("get")
def tx_get(
    tx_hash: str = typer.Argument(..., help="Transaction hash"),
    network: str = typer.Option("local"),
):
    """Look up a transaction by hash on the real chain."""
    client = MidnightClient(network=network)
    tx = client.indexer.get_transaction(tx_hash)
    if tx:
        rprint(f"\n  [bold]Transaction:[/bold] [cyan]{tx_hash}[/cyan]")
        rprint(f"  Block:  [cyan]{tx.get('blockHeight', 'pending')}[/cyan]")
        rprint(f"  Status: [green]{tx.get('status', 'unknown')}[/green]")
    else:
        rprint(f"  [yellow]Transaction not found or still pending[/yellow]")


@tx_app.command("list")
def tx_list(
    address: str = typer.Argument(..., help="Contract address"),
    network: str = typer.Option("local"),
    limit:   int = typer.Option(10, help="Number of transactions"),
):
    """List real transactions for a contract address from the indexer."""
    client = MidnightClient(network=network)
    rprint(f"\n[dim]Querying real transactions for {address[:30]}... from {network}[/dim]")
    
    # Real query — get transactions from indexer
    try:
        import httpx
        r = httpx.post(
            client.indexer.url,
            json={
                "query": """
                query GetTxs($address: String!, $limit: Int!) {
                    transactions(contractAddress: $address, limit: $limit) {
                        hash
                        blockHeight
                        status
                        timestamp
                    }
                }
                """,
                "variables": {"address": address, "limit": limit},
            },
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        txs = data.get("data", {}).get("transactions", [])
        
        if not txs:
            rprint("[yellow]No transactions found for this address.[/yellow]")
            return

        table = Table(title=f"Transactions for {address[:20]}...")
        table.add_column("Hash", style="dim")
        table.add_column("Block")
        table.add_column("Status")
        for tx in txs:
            icon = "[green]✓[/green]" if tx.get("status") == "confirmed" else "[red]✗[/red]"
            table.add_row(
                tx.get("hash", "")[:32] + "...",
                str(tx.get("blockHeight", "pending")),
                f"{icon} {tx.get('status', 'unknown')}",
            )
        console.print(table)
    except Exception as e:
        rprint(f"[red]Could not fetch transactions: {e}[/red]")


def main():
    app()
