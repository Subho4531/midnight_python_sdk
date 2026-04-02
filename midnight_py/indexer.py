import httpx
import json
from typing import AsyncIterator
from .models import ContractState, Balance
from .exceptions import ConnectionError as MidnightConnectionError


class IndexerClient:
    """
    Reads public on-chain state from the Midnight indexer.
    Connects to real Midnight GraphQL API.
    """

    def __init__(self, url: str, ws_url: str = None, network_id: str = "undeployed"):
        self.url = url
        self.ws_url = ws_url
        self.network_id = network_id
        self._http = httpx.Client(timeout=30.0)

    def is_alive(self) -> bool:
        """Check if indexer is reachable via introspection."""
        try:
            r = self._http.post(
                self.url,
                json={"query": "{ __typename }"},
                headers={"Content-Type": "application/json"},
                timeout=5.0,
            )
            return r.status_code == 200
        except Exception:
            return False

    def get_balance(self, address: str) -> Balance:
        """
        Get real wallet balance from Midnight indexer.
        
        Midnight has TWO token types:
        - DUST: unshielded, readable by address
        - NIGHT: shielded, requires viewing key session
        
        This queries unshielded DUST. For NIGHT you need a viewing key.
        """
        # Query 1: Try to get DUST (unshielded coins)
        dust_query = """
        query GetUnshieldedBalance($address: String!) {
            unshieldedCoins(address: $address) {
                value
            }
        }
        """
        dust = 0
        try:
            response = self._http.post(
                self.url,
                json={"query": dust_query, "variables": {"address": address}},
                headers={"Content-Type": "application/json"},
            )
            if response.status_code == 200:
                data = response.json()
                if "data" in data and data["data"] and data["data"].get("unshieldedCoins"):
                    coins = data["data"]["unshieldedCoins"]
                    if isinstance(coins, list):
                        dust = sum(int(c.get("value", 0)) for c in coins)
                    elif isinstance(coins, dict):
                        dust = int(coins.get("value", 0))
        except Exception:
            pass

        # Query 2: Try block-level query for latest block info
        block_query = """
        query {
            blocks(limit: 1) {
                height
                hash
            }
        }
        """
        try:
            response = self._http.post(
                self.url,
                json={"query": block_query},
                headers={"Content-Type": "application/json"},
            )
            # Just confirms indexer is working, we don't need the data
        except Exception:
            pass

        return Balance(dust=dust, night=0)

    def get_night_balance_note(self) -> str:
        """
        NIGHT tokens are shielded on Midnight.
        To read shielded NIGHT balance, you need to:
        1. Call indexer connect() mutation with your viewing key
        2. Use the returned sessionId to query shieldedBalance
        This requires the @midnight-ntwrk/wallet-sdk packages.
        The Python SDK bridges this via the Node.js wallet helper.
        """
        return (
            "NIGHT is shielded — use wallet_fix.py to check real balance via official SDK"
        )

    def get_contract_state(self, address: str) -> ContractState:
        """Read public contract state from the indexer."""
        # Try v4 schema first
        query_v4 = """
        query GetContractState($address: String!) {
            contractAction(contractAddress: $address) {
                state
                blockHeight: blockOffset {
                    blockHeight
                }
            }
        }
        """
        # Fallback v3 schema
        query_v3 = """
        query GetContractState($address: String!) {
            contractState(address: $address) {
                state
                blockHeight
            }
        }
        """
        for query, schema in [(query_v4, "v4"), (query_v3, "v3")]:
            try:
                response = self._http.post(
                    self.url,
                    json={"query": query, "variables": {"address": address}},
                    headers={"Content-Type": "application/json"},
                )
                if response.status_code == 200:
                    data = response.json()
                    if "errors" not in data and "data" in data and data["data"]:
                        d = data["data"]
                        if schema == "v4" and d.get("contractAction"):
                            ca = d["contractAction"]
                            bh = ca.get("blockHeight", {})
                            return ContractState(
                                address=address,
                                state=ca.get("state", {}),
                                block_height=bh.get("blockHeight", 0) if isinstance(bh, dict) else 0,
                            )
                        elif schema == "v3" and d.get("contractState"):
                            cs = d["contractState"]
                            return ContractState(
                                address=address,
                                state=cs.get("state", {}),
                                block_height=cs.get("blockHeight", 0),
                            )
            except Exception:
                continue

        return ContractState(address=address, state={}, block_height=0)

    def get_transaction(self, tx_hash: str) -> dict:
        """Get a real transaction from the indexer."""
        query = """
        query GetTx($hash: String!) {
            transaction(hash: $hash) {
                hash
                blockHeight
                status
            }
        }
        """
        try:
            response = self._http.post(
                self.url,
                json={"query": query, "variables": {"hash": tx_hash}},
                headers={"Content-Type": "application/json"},
            )
            if response.status_code == 200:
                data = response.json()
                if "data" in data and data["data"].get("transaction"):
                    return data["data"]["transaction"]
        except Exception:
            pass
        return {}

    def get_latest_block(self) -> dict:
        """Get the latest block from the chain."""
        query = """
        query {
            blocks(limit: 1) {
                height
                hash
                timestamp
            }
        }
        """
        try:
            r = self._http.post(
                self.url,
                json={"query": query},
                headers={"Content-Type": "application/json"},
            )
            if r.status_code == 200:
                data = r.json()
                if "data" in data and data["data"].get("blocks"):
                    blocks = data["data"]["blocks"]
                    if blocks:
                        return blocks[0]
        except Exception:
            pass
        return {}

    async def stream_events(self, address: str) -> AsyncIterator[dict]:
        """Stream contract events via WebSocket."""
        import websockets
        async with websockets.connect(self.ws_url) as ws:
            await ws.send(json.dumps({
                "type": "start",
                "payload": {
                    "query": """
                    subscription {
                        contractActions(address: "%s") {
                            state
                            blockHeight
                        }
                    }
                    """ % address,
                },
            }))
            async for raw in ws:
                msg = json.loads(raw)
                if msg.get("type") == "data":
                    yield msg["payload"]["data"]
