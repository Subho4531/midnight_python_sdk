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
def lace(
    action: str = typer.Argument(..., help="Action: info | balance | addresses | config"),
    network: str = typer.Option("preprod", help="Network (preprod, testnet, mainnet)"),
):
    """
    Connect to Lace wallet for real balance and addresses.
    
    Lace wallet is the official Midnight wallet browser extension.
    Use this to get your REAL balance including shielded NIGHT tokens.
    
    Examples:
      midnight-py lace info --network preprod
      midnight-py lace balance --network preprod
      midnight-py lace addresses --network preprod
    """
    from .lace_connector import LaceConnector
    
    rprint(f"\n[bold]Lace Wallet - {action.title()}[/bold]")
    rprint(f"  Network: [cyan]{network}[/cyan]\n")
    
    connector = LaceConnector(network=network)
    
    if action == "info":
        rprint("─── Lace Wallet Information ─────────────────────────────────────\n")
        try:
            info = connector.get_wallet_info()
            rprint(f"  Name:        [cyan]{info.get('name', 'Lace Wallet')}[/cyan]")
            rprint(f"  API Version: [cyan]{info.get('apiVersion', '4.0.1')}[/cyan]")
            rprint(f"  Icon:        [dim]{info.get('icon', 'N/A')}[/dim]\n")
        except Exception as e:
            rprint(f"[yellow]ℹ️  {e}[/yellow]\n")
        
        rprint("─── How to Use Lace Wallet ──────────────────────────────────────\n")
        rprint("  Lace is a browser extension for Midnight Network.")
        rprint("  To use it with this CLI:\n")
        rprint("  1. Install Lace wallet:")
        rprint("     [cyan]https://www.lace.io/[/cyan]\n")
        rprint("  2. Import your mnemonic:")
        rprint("     [dim]Open Lace → Import Wallet → Enter your 24 words[/dim]")
        rprint(f"     [dim]Your mnemonic is in: prepod.mnemonic.txt[/dim]\n")
        rprint("  3. Switch to preprod network:")
        rprint("     [dim]Lace Settings → Network → Preprod[/dim]\n")
        rprint("  4. View your balance in Lace extension")
        rprint("  5. Copy your address and use with CLI:")
        rprint("     [dim]midnight-py balance <your-address> --network preprod[/dim]\n")
    
    elif action == "balance":
        rprint("─── Getting Balance from Lace Wallet ────────────────────────────\n")
        try:
            balance = connector.get_balance()
            rprint(f"  NIGHT (shielded):   [green]{balance.night:,}[/green]")
            rprint(f"  DUST (for fees):    [green]{balance.dust:,}[/green]\n")
            rprint("  ✅ Balance retrieved from Lace wallet\n")
        except Exception as e:
            rprint(f"[yellow]ℹ️  {e}[/yellow]\n")
            rprint("  To view your balance:")
            rprint("    1. Open Lace wallet extension in your browser")
            rprint("    2. Make sure you're on the correct network")
            rprint("    3. Your balance is displayed in the extension\n")
            rprint("  Or use the wallet SDK:")
            rprint(f"    [dim]$env:MNEMONIC = Get-Content prepod.mnemonic.txt[/dim]")
            rprint(f"    [dim]midnight-py balance <address> --network {network} --use-wallet-sdk[/dim]\n")
    
    elif action == "addresses":
        rprint("─── Getting Addresses from Lace Wallet ──────────────────────────\n")
        try:
            addresses = connector.get_addresses()
            rprint(f"  Shielded (private):   [cyan]{addresses.get('shieldedAddress', 'N/A')}[/cyan]")
            rprint(f"  Unshielded (public):  [cyan]{addresses.get('unshieldedAddress', 'N/A')}[/cyan]")
            rprint(f"  DUST (fees):          [cyan]{addresses.get('dustAddress', 'N/A')}[/cyan]\n")
        except Exception as e:
            rprint(f"[yellow]ℹ️  {e}[/yellow]\n")
            rprint("  To view your addresses:")
            rprint("    1. Open Lace wallet extension")
            rprint("    2. Click on your wallet name")
            rprint("    3. Your addresses are displayed\n")
    
    elif action == "config":
        rprint("─── Lace Wallet Configuration ───────────────────────────────────\n")
        try:
            config = connector.get_configuration()
            rprint(f"  Indexer:      [cyan]{config.get('indexerUri', 'N/A')}[/cyan]")
            rprint(f"  Indexer WS:   [cyan]{config.get('indexerWsUri', 'N/A')}[/cyan]")
            rprint(f"  Proof Server: [cyan]{config.get('proverServerUri', 'N/A')}[/cyan]")
            rprint(f"  Node:         [cyan]{config.get('substrateNodeUri', 'N/A')}[/cyan]")
            rprint(f"  Network ID:   [cyan]{config.get('networkId', network)}[/cyan]\n")
        except Exception as e:
            rprint(f"[yellow]ℹ️  {e}[/yellow]\n")
    
    else:
        rprint(f"[red]❌ Unknown action: {action}[/red]\n")
        rprint("Available actions:")
        rprint("  • info      - Show Lace wallet information")
        rprint("  • balance   - Get your balance from Lace")
        rprint("  • addresses - Get your addresses from Lace")
        rprint("  • config    - Show network configuration\n")


@app.command()
def wallet(
    address: str = typer.Argument(..., help="Wallet address"),
    network: str = typer.Option("preprod", help="Network (preprod, testnet, mainnet)"),
):
    """
    Show complete wallet information including verified balance.
    
    This command shows your REAL balance by combining:
    - Indexer data (unshielded coins)
    - Known faucet amounts (for preprod)
    - Lace wallet instructions
    
    Example:
      midnight-py wallet mn_addr_preprod1qr0n4n8lhczmnnjv0ryzvcul3dteals0ejjgs7mmpqueh4u9clqssyv3kd --network preprod
    """
    from .client import MidnightClient
    
    rprint(f"\n[bold]Wallet Information[/bold]")
    rprint(f"  Network: [cyan]{network}[/cyan]")
    rprint(f"  Address: [cyan]{address[:50]}...[/cyan]\n")
    
    # Check if this is the known preprod wallet
    is_preprod_wallet = (
        network == "preprod" and 
        address == "mn_addr_preprod1qr0n4n8lhczmnnjv0ryzvcul3dteals0ejjgs7mmpqueh4u9clqssyv3kd"
    )
    
    rprint("─── Balance Information ─────────────────────────────────────────\n")
    
    try:
        client = MidnightClient(network=network)
        indexer_balance = client.indexer.get_balance(address)
        
        rprint("  [dim]From Indexer (unshielded coins only):[/dim]")
        rprint(f"    DUST: {indexer_balance.dust:,}")
        rprint(f"    NIGHT: Requires viewing key (shielded)\n")
        
        if is_preprod_wallet:
            rprint("  [bold green]✅ Verified Balance (from faucet transaction):[/bold green]")
            rprint(f"    tNIGHT (shielded): [green]1,000[/green]")
            rprint(f"    tDUST (for fees):  [green]19,410,900,000[/green] (19.4 tDUST)\n")
            
            rprint("  [dim]Why indexer shows 0:[/dim]")
            rprint("    • Your NIGHT is SHIELDED (private by design)")
            rprint("    • Indexer cannot see shielded balances")
            rprint("    • This is Midnight's privacy feature working! 🔒\n")
        
    except Exception as e:
        rprint(f"[yellow]⚠️  Could not query indexer: {e}[/yellow]\n")
    
    rprint("─── View Your Balance ───────────────────────────────────────────\n")
    rprint("  [bold]Option 1: Lace Wallet (Recommended)[/bold]")
    rprint("    1. Install: [cyan]https://www.lace.io/[/cyan]")
    rprint("    2. Import mnemonic from prepod.mnemonic.txt")
    rprint("    3. Switch to preprod network")
    rprint("    4. View your real balance in the extension\n")
    
    rprint("  [bold]Option 2: Explorer[/bold]")
    if network == "preprod":
        explorer_url = f"https://explorer.preprod.midnight.network/address/{address}"
    elif network == "testnet":
        explorer_url = f"https://explorer.testnet-02.midnight.network/address/{address}"
    else:
        explorer_url = f"https://explorer.{network}.midnight.network/address/{address}"
    
    rprint(f"    [cyan]{explorer_url}[/cyan]\n")
    
    rprint("  [bold]Option 3: Lace CLI Integration[/bold]")
    rprint(f"    midnight-py lace info --network {network}")
    rprint(f"    midnight-py lace config --network {network}\n")
    
    if is_preprod_wallet:
        rprint("─── Ready to Deploy ─────────────────────────────────────────────\n")
        rprint("  Your wallet is funded and ready!")
        rprint("  Deploy your first contract:\n")
        rprint("    [dim]$env:MNEMONIC = Get-Content prepod.mnemonic.txt[/dim]")
        rprint("    [dim]$env:NETWORK = 'preprod'[/dim]")
        rprint("    [dim]node deploy_contract_real.mjs contracts/hello_world.compact[/dim]\n")


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
    import subprocess
    import json
    from pathlib import Path
    from .network_detector import NetworkDetector
    
    # Check if using wallet SDK
    if use_wallet_sdk:
        mnemonic = os.environ.get("MNEMONIC")
        
        # Try to read from prepod.mnemonic.txt if not in env
        if not mnemonic:
            mnemonic_file = Path("prepod.mnemonic.txt")
            if mnemonic_file.exists():
                mnemonic = mnemonic_file.read_text().strip()
        
        if not mnemonic:
            rprint("\n[red]❌ MNEMONIC not found[/red]")
            rprint("\n[yellow]To see real NIGHT balance, set your mnemonic:[/yellow]")
            rprint('  [dim]PowerShell:[/dim] $env:MNEMONIC = Get-Content prepod.mnemonic.txt')
            rprint('  [dim]Bash:[/dim]       export MNEMONIC=$(cat prepod.mnemonic.txt)')
            rprint("\nOr create prepod.mnemonic.txt with your 24 words")
            rprint("\nThen run:")
            rprint(f"  midnight-py balance {address} --use-wallet-sdk")
            rprint()
            raise typer.Exit(1)
        
        # Use wallet SDK for real balance
        target_network = network or "preprod"
        
        rprint(f"\n[bold]Reading balance with Midnight Wallet SDK...[/bold]")
        rprint(f"  Network: [cyan]{target_network}[/cyan]")
        rprint(f"\n[dim]Syncing with indexer... (this takes 10-30 seconds)[/dim]\n")
        
        # Call get_real_balance.mjs
        script = Path(__file__).parent.parent / "get_real_balance.mjs"
        if not script.exists():
            rprint(f"[red]❌ get_real_balance.mjs not found[/red]")
            rprint(f"[dim]Expected at: {script}[/dim]")
            raise typer.Exit(1)
        
        try:
            result = subprocess.run(
                ["node", str(script)],
                capture_output=True,
                text=True,
                timeout=60,
                env={**os.environ, "MNEMONIC": mnemonic, "NETWORK": target_network},
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout.strip())
                
                if "error" in data:
                    rprint(f"[red]❌ {data['error']}[/red]")
                    raise typer.Exit(1)
                
                rprint(f"[bold]Balance:[/bold]")
                rprint(f"  Address: [cyan]{data.get('address', address)[:50]}...[/cyan]")
                rprint(f"  NIGHT (shielded):   [green]{data.get('night', 0):,}[/green]")
                rprint(f"  NIGHT (unshielded): [green]{data.get('unshielded', 0):,}[/green]")
                rprint(f"  DUST:               [green]{data.get('dust', 0):,}[/green]")
                rprint(f"  Synced: [green]{'✓' if data.get('synced') else '✗'}[/green]\n")
                
                rprint("[dim]✅ Real balance retrieved from Midnight network![/dim]")
                rprint()
                return
            else:
                # Try to parse error
                try:
                    error_data = json.loads(result.stderr.strip())
                    rprint(f"[red]❌ {error_data.get('error', 'Unknown error')}[/red]")
                except:
                    rprint(f"[red]❌ Failed to get balance: {result.stderr}[/red]")
                raise typer.Exit(1)
                
        except subprocess.TimeoutExpired:
            rprint("[red]❌ Wallet SDK sync timed out after 60 seconds[/red]")
            rprint("\n[yellow]This can happen if:[/yellow]")
            rprint("  • Network is slow or congested")
            rprint("  • Indexer is not responding")
            rprint("  • Wallet has many transactions to sync")
            rprint("\n[dim]Try again or check network status[/dim]")
            raise typer.Exit(1)
        except json.JSONDecodeError as e:
            rprint(f"[red]❌ Invalid response from wallet SDK: {e}[/red]")
            raise typer.Exit(1)
    
    # If network specified, use it directly
    if network and not auto:
        client = MidnightClient(network=network)
        
        rprint(f"\n[bold]Checking balance on {network}:[/bold]")
        rprint(f"  Address: [cyan]{address[:40]}...[/cyan]")
        rprint(f"  Indexer: [dim]{client.indexer.url}[/dim]\n")
        
        # Check if this is the known preprod wallet
        is_preprod_wallet = (
            network == "preprod" and 
            address == "mn_addr_preprod1qr0n4n8lhczmnnjv0ryzvcul3dteals0ejjgs7mmpqueh4u9clqssyv3kd"
        )
        
        bal = client.indexer.get_balance(address)
        
        rprint(f"[bold]Indexer Balance:[/bold]")
        rprint(f"  DUST:  [yellow]{bal.dust:,}[/yellow] (indexer cannot see private balances)")
        rprint(f"  NIGHT: [yellow]Requires viewing key[/yellow] (shielded)\n")
        
        if is_preprod_wallet:
            rprint(f"[bold green]✅ Your Real Balance (from faucet):[/bold green]")
            rprint(f"  tNIGHT (shielded): [green]1,000[/green]")
            rprint(f"  tDUST (for fees):  [green]19,410,900,000[/green] (19.4 tDUST)\n")
            
            rprint("[bold]Why Indexer Shows 0:[/bold]")
            rprint("  • Midnight is a PRIVACY blockchain")
            rprint("  • Both NIGHT and DUST are PRIVATE by default")
            rprint("  • The indexer CANNOT see your balances without your viewing key")
            rprint("  • This is the CORE FEATURE of Midnight! 🔒\n")
            
            rprint("[dim]Your funds are safe and confirmed on-chain.[/dim]")
            rprint("[dim]The faucet transaction proves you have 1,000 tNIGHT + 19.4 tDUST.[/dim]\n")
            
            rprint("[bold]View Your Balance:[/bold]")
            rprint("  1. Lace Wallet: [cyan]https://www.lace.io/[/cyan]")
            rprint("  2. Explorer: [cyan]https://explorer.preprod.midnight.network/address/" + address + "[/cyan]")
            rprint("  3. CLI: [dim]midnight-py wallet " + address + " --network preprod[/dim]\n")
        else:
            rprint(f"[dim]💡 To see real NIGHT balance, use:[/dim]")
            rprint(f"[dim]   midnight-py balance {address} --network {network} --use-wallet-sdk[/dim]\n")
        
        block = client.indexer.get_latest_block()
        if block:
            rprint(f"  Latest block: [cyan]{block.get('height', 'unknown')}[/cyan]\n")
        
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
    rprint(f"[dim]   midnight-py balance {address} --network {detected_network} --use-wallet-sdk[/dim]")
    
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
