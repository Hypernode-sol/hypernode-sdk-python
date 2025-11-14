"""
Smoke tests for Hypernode Python SDK
Basic validation to ensure SDK functionality works
"""

import pytest
import time
from unittest.mock import Mock, patch


def test_import_sdk():
    """Test that SDK can be imported without errors"""
    from hypernode_sdk import HypernodeClient

    assert HypernodeClient is not None


def test_import_all_exports():
    """Test that all expected exports are available"""
    from hypernode_sdk import (
        HypernodeClient,
        create_client,
        DeploymentConfig,
        DeploymentResponse,
        GenerationRequest,
        GenerationResponse,
        retry_with_backoff,
        retry_async_with_backoff,
        calculate_backoff_delay,
    )

    assert HypernodeClient is not None
    assert create_client is not None
    assert DeploymentConfig is not None
    assert DeploymentResponse is not None
    assert GenerationRequest is not None
    assert GenerationResponse is not None
    assert retry_with_backoff is not None
    assert retry_async_with_backoff is not None
    assert calculate_backoff_delay is not None


def test_create_client_basic():
    """Test that client can be created with basic configuration"""
    from hypernode_sdk import HypernodeClient

    client = HypernodeClient(
        api_url="http://localhost:3000",
        rpc_url="http://localhost:8899"
    )

    assert client is not None
    assert client.api_url == "http://localhost:3000"
    assert client.rpc_url == "http://localhost:8899"


def test_create_client_with_api_key():
    """Test that client can be created with API key"""
    from hypernode_sdk import HypernodeClient

    client = HypernodeClient(
        api_url="http://localhost:3000",
        rpc_url="http://localhost:8899",
        api_key="test-api-key-123"
    )

    assert client is not None
    assert client.api_key == "test-api-key-123"
    assert "Authorization" in client.session.headers
    assert client.session.headers["Authorization"] == "Bearer test-api-key-123"


def test_create_client_helper():
    """Test helper function create_client"""
    from hypernode_sdk import create_client

    client = create_client(
        api_url="http://localhost:3000",
        rpc_url="http://localhost:8899"
    )

    assert client is not None
    assert client.api_url == "http://localhost:3000"


def test_client_validation_empty_url():
    """Test that client validates required parameters"""
    from hypernode_sdk import HypernodeClient
    from hypernode_sdk.exceptions import ValidationError

    with pytest.raises(ValidationError, match="api_url cannot be empty"):
        HypernodeClient(api_url="", rpc_url="http://localhost:8899")


def test_deployment_config_creation():
    """Test DeploymentConfig can be created"""
    from hypernode_sdk import DeploymentConfig

    config = DeploymentConfig(
        model="meta-llama/Llama-2-7b-hf",
        template="huggingface"
    )

    assert config is not None
    assert config.model == "meta-llama/Llama-2-7b-hf"
    assert config.template == "huggingface"


def test_generation_request_creation():
    """Test GenerationRequest can be created"""
    from hypernode_sdk import GenerationRequest

    request = GenerationRequest(
        prompt="Hello world",
        max_tokens=100,
        temperature=0.7
    )

    assert request is not None
    assert request.prompt == "Hello world"
    assert request.max_tokens == 100
    assert request.temperature == 0.7


def test_retry_logic_calculate_backoff():
    """Test backoff delay calculation"""
    from hypernode_sdk import calculate_backoff_delay

    # Test exponential backoff
    delay0 = calculate_backoff_delay(0, base_delay=1.0)
    delay1 = calculate_backoff_delay(1, base_delay=1.0)
    delay2 = calculate_backoff_delay(2, base_delay=1.0)

    assert delay0 == 1.0  # 1 * 2^0
    assert delay1 == 2.0  # 1 * 2^1
    assert delay2 == 4.0  # 1 * 2^2

    # Test max delay cap
    delay10 = calculate_backoff_delay(10, base_delay=1.0, max_delay=30.0)
    assert delay10 == 30.0  # Capped at max_delay


def test_retry_decorator_success():
    """Test retry decorator with successful function"""
    from hypernode_sdk import retry_with_backoff

    @retry_with_backoff(max_retries=3, base_delay=0.1)
    def successful_function():
        return "success"

    result = successful_function()
    assert result == "success"


def test_retry_decorator_transient_failure():
    """Test retry decorator with transient failure that eventually succeeds"""
    from hypernode_sdk import retry_with_backoff

    attempt_count = {"count": 0}

    @retry_with_backoff(max_retries=3, base_delay=0.1)
    def flaky_function():
        attempt_count["count"] += 1
        if attempt_count["count"] < 3:
            raise ConnectionError("Simulated network failure")
        return "success"

    result = flaky_function()
    assert result == "success"
    assert attempt_count["count"] == 3  # Failed twice, succeeded on 3rd attempt


def test_retry_decorator_permanent_failure():
    """Test retry decorator with permanent failure"""
    from hypernode_sdk import retry_with_backoff

    @retry_with_backoff(max_retries=3, base_delay=0.1)
    def always_fails():
        raise ConnectionError("Permanent failure")

    with pytest.raises(ConnectionError, match="Permanent failure"):
        always_fails()


def test_retry_decorator_non_retryable_error():
    """Test that ValidationError and AuthenticationError are not retried"""
    from hypernode_sdk import retry_with_backoff
    from hypernode_sdk.exceptions import ValidationError, AuthenticationError

    attempt_count = {"count": 0}

    @retry_with_backoff(max_retries=3, base_delay=0.1)
    def validation_error_function():
        attempt_count["count"] += 1
        raise ValidationError("Invalid input")

    with pytest.raises(ValidationError, match="Invalid input"):
        validation_error_function()

    # Should fail immediately without retry
    assert attempt_count["count"] == 1

    # Test AuthenticationError
    attempt_count["count"] = 0

    @retry_with_backoff(max_retries=3, base_delay=0.1)
    def auth_error_function():
        attempt_count["count"] += 1
        raise AuthenticationError("Invalid credentials")

    with pytest.raises(AuthenticationError, match="Invalid credentials"):
        auth_error_function()

    # Should fail immediately without retry
    assert attempt_count["count"] == 1


@pytest.mark.asyncio
async def test_retry_async_decorator():
    """Test async retry decorator"""
    from hypernode_sdk import retry_async_with_backoff

    @retry_async_with_backoff(max_retries=3, base_delay=0.1)
    async def async_function():
        return "success"

    result = await async_function()
    assert result == "success"


def test_solana_client_accessible():
    """Test that Solana client is accessible"""
    from hypernode_sdk import HypernodeClient

    client = HypernodeClient(
        api_url="http://localhost:3000",
        rpc_url="http://localhost:8899"
    )

    solana_client = client.get_solana_client()
    assert solana_client is not None


def test_exceptions_importable():
    """Test that all exceptions can be imported"""
    from hypernode_sdk.exceptions import (
        APIError,
        ConnectionError,
        AuthenticationError,
        ValidationError,
        TimeoutError,
        RateLimitError,
        ResourceNotFoundError,
    )

    assert APIError is not None
    assert ConnectionError is not None
    assert AuthenticationError is not None
    assert ValidationError is not None
    assert TimeoutError is not None
    assert RateLimitError is not None
    assert ResourceNotFoundError is not None


def test_sdk_version():
    """Test that SDK version is defined"""
    import hypernode_sdk

    assert hasattr(hypernode_sdk, "__version__")
    assert hypernode_sdk.__version__ == "1.0.0"


def test_retry_timing():
    """Test that retry delays are approximately correct"""
    from hypernode_sdk import retry_with_backoff
    import time

    attempt_times = []

    @retry_with_backoff(max_retries=3, base_delay=0.5)
    def timed_function():
        attempt_times.append(time.time())
        if len(attempt_times) < 3:
            raise ConnectionError("Retry")
        return "success"

    start_time = time.time()
    result = timed_function()
    total_time = time.time() - start_time

    assert result == "success"
    assert len(attempt_times) == 3

    # Check delays between attempts (approximately 0.5s and 1.0s)
    # Attempt 1: immediate
    # Attempt 2: after 0.5s delay (0.5 * 2^0)
    # Attempt 3: after 1.0s delay (0.5 * 2^1)
    # Total expected: ~1.5s

    assert total_time >= 1.5  # At least 1.5s due to delays
    assert total_time < 3.0   # Should not take too long
