"""
Advanced Error Handling Example

Demonstrates proper error handling, retry logic, and resource management
with the Hypernode Python SDK.
"""

import sys
from hypernode_sdk import HypernodeClient, init_logging
from hypernode_sdk.exceptions import (
    APIError,
    ConnectionError,
    AuthenticationError,
    RateLimitError,
    TimeoutError,
)


def example_with_context_manager():
    """
    Recommended: Use context manager for automatic resource cleanup.
    """
    print("Example 1: Context Manager (Recommended)")
    print("=" * 50)

    # Initialize logging
    init_logging(level="INFO", json_logs=False)

    try:
        # Context manager automatically closes connection
        with HypernodeClient(
            api_url="http://localhost:3001",
            api_key="your-api-key-here"
        ) as client:
            # Get available nodes
            nodes = client.get_nodes()
            print(f"Found {len(nodes)} available nodes")

            # Submit a job
            job = client.submit_job(
                wallet_address="your-wallet-address",
                job_type="inference",
                model_name="llama-3-8b",
                input_data="Hello, world!",
                max_price=1000
            )
            print(f"Job submitted: {job.job_id}")

    except ConnectionError as e:
        print(f"Connection failed: {e}")
        print("Tip: Check if the backend is running")
        sys.exit(1)

    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
        print("Tip: Check your API key")
        sys.exit(1)

    except RateLimitError as e:
        print(f"Rate limit exceeded: {e}")
        print("Tip: Wait before retrying")
        sys.exit(1)

    except APIError as e:
        print(f"API error: {e}")
        sys.exit(1)

    print("✓ Request completed successfully")
    print()


def example_with_manual_cleanup():
    """
    Alternative: Manual resource management.
    """
    print("Example 2: Manual Cleanup")
    print("=" * 50)

    client = None
    try:
        client = HypernodeClient(
            api_url="http://localhost:3001",
            api_key="your-api-key-here"
        )

        # Perform operations
        nodes = client.get_nodes()
        print(f"Found {len(nodes)} available nodes")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    finally:
        # Always close the client
        if client:
            client.close()
            print("✓ Client closed")

    print()


def example_with_retry_logic():
    """
    Retry logic is built-in, but you can add custom handling.
    """
    print("Example 3: Custom Retry Logic")
    print("=" * 50)

    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        print(f"Attempt {attempt}/{max_attempts}")

        try:
            with HypernodeClient(api_url="http://localhost:3001") as client:
                nodes = client.get_nodes()
                print(f"✓ Success: Found {len(nodes)} nodes")
                break

        except ConnectionError as e:
            if attempt < max_attempts:
                print(f"Connection failed, retrying... ({e})")
                # Exponential backoff is handled by @retry_with_backoff
                continue
            else:
                print(f"✗ Failed after {max_attempts} attempts")
                sys.exit(1)

        except APIError as e:
            # Don't retry on API errors (4xx)
            print(f"✗ API error (not retrying): {e}")
            sys.exit(1)

    print()


def example_with_timeout():
    """
    Handle timeout errors gracefully.
    """
    print("Example 4: Timeout Handling")
    print("=" * 50)

    try:
        with HypernodeClient(api_url="http://localhost:3001") as client:
            # This uses the built-in timeout from requests
            job = client.submit_job(
                wallet_address="your-wallet-address",
                job_type="inference",
                model_name="llama-3-8b",
                input_data="Long running task",
                max_price=5000,
                timeout=3600  # 1 hour
            )
            print(f"✓ Job submitted: {job.job_id}")

    except TimeoutError as e:
        print(f"✗ Request timed out: {e}")
        print("Tip: Increase timeout or check network")
        sys.exit(1)

    print()


def example_with_structured_logging():
    """
    Use structured logging for better observability.
    """
    print("Example 5: Structured Logging")
    print("=" * 50)

    # Enable JSON logging for production
    init_logging(level="DEBUG", json_logs=True)

    try:
        with HypernodeClient(api_url="http://localhost:3001") as client:
            nodes = client.get_nodes()
            print(f"Found {len(nodes)} nodes (check logs for details)")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    print()


def main():
    """Run all examples."""
    print("\n🚀 Hypernode SDK - Advanced Error Handling Examples\n")

    examples = [
        example_with_context_manager,
        example_with_manual_cleanup,
        example_with_retry_logic,
        example_with_timeout,
        example_with_structured_logging,
    ]

    for example in examples:
        try:
            example()
        except KeyboardInterrupt:
            print("\n\n✗ Interrupted by user")
            sys.exit(0)
        except Exception as e:
            print(f"\n✗ Example failed: {e}\n")
            continue

    print("=" * 50)
    print("All examples completed!")
    print("\nBest Practices:")
    print("1. ✓ Use context manager (with statement)")
    print("2. ✓ Handle specific exceptions")
    print("3. ✓ Enable structured logging in production")
    print("4. ✓ Set appropriate timeouts")
    print("5. ✓ Don't retry on 4xx errors")
    print("6. ✓ Use exponential backoff (built-in)")


if __name__ == "__main__":
    main()
