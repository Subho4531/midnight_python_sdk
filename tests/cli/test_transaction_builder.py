"""Tests for transaction builder."""

import pytest
from midnight_sdk.builder import TransactionBuilder


def test_transaction_builder_init():
    """Test TransactionBuilder initialization."""
    builder = TransactionBuilder()
    assert builder.tx_data["type"] is None
    assert builder.tx_data["nonce"] is None
    assert builder.tx_data["fee"] is None


def test_transaction_builder_call_contract():
    """Test building contract call transaction."""
    builder = TransactionBuilder()
    builder.call_contract("addr123", "increment", {"value": 1})
    
    assert builder.tx_data["type"] == "contract_call"
    assert builder.tx_data["payload"]["contract_address"] == "addr123"
    assert builder.tx_data["payload"]["circuit"] == "increment"
    assert builder.tx_data["payload"]["arguments"] == {"value": 1}


def test_transaction_builder_deploy_contract():
    """Test building contract deployment transaction."""
    builder = TransactionBuilder()
    builder.deploy_contract("contracts/my_contract.compact")
    
    assert builder.tx_data["type"] == "contract_deploy"
    assert builder.tx_data["payload"]["contract_path"] == "contracts/my_contract.compact"


def test_transaction_builder_transfer():
    """Test building transfer transaction."""
    builder = TransactionBuilder()
    builder.transfer("dest_addr", 1000)
    
    assert builder.tx_data["type"] == "transfer"
    assert builder.tx_data["payload"]["destination"] == "dest_addr"
    assert builder.tx_data["payload"]["amount"] == 1000


def test_transaction_builder_set_nonce():
    """Test setting nonce."""
    builder = TransactionBuilder()
    builder.set_nonce(42)
    
    assert builder.tx_data["nonce"] == 42


def test_transaction_builder_set_fee():
    """Test setting fee."""
    builder = TransactionBuilder()
    builder.set_fee(100)
    
    assert builder.tx_data["fee"] == 100


def test_transaction_builder_build():
    """Test building complete transaction."""
    builder = TransactionBuilder()
    tx = (
        builder
        .call_contract("addr", "fn", {"arg": 1})
        .set_nonce(10)
        .set_fee(50)
        .build()
    )
    
    assert tx["type"] == "contract_call"
    assert tx["nonce"] == 10
    assert tx["fee"] == 50
    assert tx["payload"]["contract_address"] == "addr"


def test_transaction_builder_build_without_type():
    """Test building without type raises error."""
    builder = TransactionBuilder()
    
    with pytest.raises(ValueError, match="Transaction type not set"):
        builder.build()


def test_transaction_builder_reset():
    """Test resetting builder."""
    builder = TransactionBuilder()
    builder.call_contract("addr", "fn").set_nonce(10)
    
    builder.reset()
    
    assert builder.tx_data["type"] is None
    assert builder.tx_data["nonce"] is None


def test_transaction_builder_chaining():
    """Test method chaining."""
    builder = TransactionBuilder()
    result = builder.transfer("addr", 100).set_nonce(5).set_fee(10)
    
    assert result is builder  # Verify chaining returns self
    assert builder.tx_data["type"] == "transfer"
    assert builder.tx_data["nonce"] == 5
    assert builder.tx_data["fee"] == 10
