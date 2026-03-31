"""
Full end-to-end demo: deploy and use a BulletinBoard contract.
This demonstrates the midnight-py SDK capabilities.

Run: python examples/bulletin_board.py

Note: You'll need to provide your own private key via environment variable:
export MIDNIGHT_PRIVATE_KEY="your_private_key_here"
"""

import os
from midnight_py import MidnightClient
from midnight_py.codegen import compact_to_python
from rich import print as rprint
from rich.console import Console

console = Console()

def main():
    console.rule("[bold]midnight-py Demo — BulletinBoard")

    # 1. Connect
    rprint("\n[bold]Step 1:[/bold] Connecting to Midnight local network...")
    client = MidnightClient(network="local")
    status = client.status()
    for svc, ok in status.items():
        icon = "[green]✓ OK[/green]" if ok else "[red]✗ OFFLINE[/red]"
        rprint(f"  {svc}: {icon}")
    
    if not all(status.values()):
        rprint("\n[red]⚠ Services not running![/red]")
        rprint("[yellow]Make sure midnight-local-dev is running.[/yellow]")
        return

    # 2. Create/load wallet
    rprint("\n[bold]Step 2:[/bold] Setting up wallet...")
    
    # Get private key from environment or use a demo seed phrase
    private_key = os.getenv("MIDNIGHT_PRIVATE_KEY")
    if not private_key:
        rprint("[yellow]⚠ No MIDNIGHT_PRIVATE_KEY found, using demo seed phrase[/yellow]")
        seed_phrase = "demo seed phrase for testing only"
        address = client.wallet.generate_address(seed_phrase, network="local")
    else:
        # Derive address from private key
        address = client.wallet.generate_address("", network="local")
    
    rprint(f"  Wallet address: [cyan]{address}[/cyan]")
    
    try:
        balance = client.wallet.get_balance(address)
        rprint(f"  Balance: {balance.dust:,} DUST, {balance.night:,} NIGHT")
    except Exception as e:
        rprint(f"  [yellow]Balance check unavailable: {e}[/yellow]")

    # 3. Generate Python class from .compact file
    rprint("\n[bold]Step 3:[/bold] Generating Python class from Compact contract...")
    BulletinBoard = compact_to_python("contracts/bulletin_board.compact")
    rprint(f"  Generated class: [cyan]{BulletinBoard.__name__}[/cyan]")
    rprint(f"  Available methods: {[m for m in dir(BulletinBoard) if not m.startswith('_')]}")

    # 4. Deploy (requires private key)
    if not private_key:
        rprint("\n[yellow]⚠ Skipping deployment - set MIDNIGHT_PRIVATE_KEY to deploy[/yellow]")
        rprint("[green]✓ Demo complete! Auto-codegen feature demonstrated.[/green]")
        return
    
    rprint("\n[bold]Step 4:[/bold] Deploying contract...")
    try:
        raw_contract = client.contracts.deploy(
            "contracts/bulletin_board.compact",
            private_key=private_key,
        )
        board = BulletinBoard(raw_contract)
        rprint(f"  Deployed at: [green]{raw_contract.address}[/green]")

        # 5. Post a message (ZK proof auto-generated)
        rprint("\n[bold]Step 5:[/bold] Posting message with ZK proof...")
        raw_contract.set_key(private_key)
        result = board.post(message="Hello from Python on Midnight!")
        rprint(f"  TX Hash: [cyan]{result.tx_hash}[/cyan]")
        rprint(f"  Status:  [green]{result.status}[/green]")

        # 6. Read state
        rprint("\n[bold]Step 6:[/bold] Reading on-chain state...")
        state = board.state()
        rprint(f"  Block: {state.block_height}")
        rprint(f"  State: {state.state}")

        console.rule("[green]✓ Done! Python on Midnight works.")
    except Exception as e:
        rprint(f"\n[red]✗ Error during deployment: {e}[/red]")
        rprint("[yellow]Make sure your wallet is funded and services are running.[/yellow]")


if __name__ == "__main__":
    main()
