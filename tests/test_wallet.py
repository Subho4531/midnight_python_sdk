from midnight_sdk.wallet import WalletClient
from midnight_sdk.models import Balance
import pytest


def test_generate_address_preprod():
    wallet = WalletClient()
    # Use get_real_address which is the actual method
    result = wallet.get_real_address("test seed phrase for wallet generation", network_id="preprod")
    addr = result.get("address")
    assert addr.startswith("mn_addr_preprod1")
    assert len(addr) > 20


def test_generate_address_mainnet():
    wallet = WalletClient()
    result = wallet.get_real_address("test seed phrase for wallet generation", network_id="mainnet")
    addr = result.get("address")
    assert addr.startswith("mn_addr1")


def test_generate_address_deterministic():
    wallet = WalletClient()
    result1 = wallet.get_real_address("same seed phrase for deterministic test", network_id="preprod")
    result2 = wallet.get_real_address("same seed phrase for deterministic test", network_id="preprod")
    addr1 = result1.get("address")
    addr2 = result2.get("address")
    assert addr1 == addr2

