#!/usr/bin/env python3
"""
Small Transfer Test - Test with 1 NIGHT transfer
"""

import sys
from pathlib import Path
from rich.console import Console

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from midnight_sdk.wallet import WalletClient
from midnight_sdk.config import ConfigManager

console = Console()

# Load config
config_mgr = ConfigManager()
config_mgr.load()
profile = config_mgr.get_profile("preprod")

# Get wallet
wallet_path = Path(config_mgr.config.wallets["mywallet"])
mnemonic = wallet_path.read_text().strip()

# Initialize wallet client
wallet_client = WalletClient(profile.node_url)

# Generate random recipient
import secrets
words = ["test", "wallet", "midnight", "network", "python", "sdk", "transfer", "balance",
        "address", "token", "night", "dust", "preprod", "testnet", "faucet", "random",
        "secure", "private", "public", "key", "signature", "transaction", "block", "chain"]
recipient_mnemonic = " ".join(secrets.choice(words) for _ in range(24))
addr_info = wallet_client.get_all_addresses(recipient_mnemonic, profile.network_id)
recipient = addr_info['addresses']['unshielded']

console.print(f"[cyan]Recipient:[/cyan] {recipient}")
console.print(f"[cyan]Amount:[/cyan] 1.000000 NIGHT (1,000,000 STAR)")
console.print()

# Transfer 1 NIGHT
try:
    console.print("[cyan]Initiating transfer...[/cyan]")
    console.print("[dim]This will take 1-3 minutes (wallet sync + proof generation)[/dim]")
    console.print()
    
    result = wallet_client.transfer_unshielded(
        recipient=recipient,
        amount=1_000_000,  # 1 NIGHT
        mnemonic=mnemonic,
        network_id=profile.network_id,
        indexer_url=profile.indexer_url,
        indexer_ws=profile.indexer_ws_url,
        node_url=profile.node_url,
        proof_url=profile.proof_server_url
    )
    
    console.print(f"\n[green]✓ Transfer successful![/green]")
    console.print(f"[cyan]TX Hash:[/cyan] {result['tx_hash']}")
    console.print(f"[cyan]Status:[/cyan] {result['status']}")
    
except Exception as e:
    console.print(f"\n[red]✗ Transfer failed: {e}[/red]")
    import traceback
    traceback.print_exc()
    sys.exit(1)
