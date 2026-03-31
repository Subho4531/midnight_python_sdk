class MidnightSDKError(Exception):
    """Base exception for all midnight-py errors."""


class ConnectionError(MidnightSDKError):
    """Cannot reach a Midnight service."""
    def __init__(self, service: str, url: str):
        super().__init__(f"Cannot connect to {service} at {url}. Is it running?")


class ProofGenerationError(MidnightSDKError):
    """ZK proof generation failed."""


class ContractDeployError(MidnightSDKError):
    """Contract deployment failed."""


class ContractCallError(MidnightSDKError):
    """Circuit call failed."""


class WalletError(MidnightSDKError):
    """Wallet operation failed."""


class CompactParseError(MidnightSDKError):
    """Failed to parse a .compact contract file."""


class ProofServerConnectionError(MidnightSDKError):
    """Raised when proof server is unreachable."""
    pass


class ModelNotTrainedError(MidnightSDKError):
    """Raised when ML model hasn't been trained yet."""
    pass


class InvalidFeaturesError(MidnightSDKError):
    """Raised when input features are invalid."""
    pass
