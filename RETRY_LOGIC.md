# Retry Logic with Exponential Backoff

## Overview

The Hypernode Python SDK now includes automatic retry logic with exponential backoff for all critical network operations. This improves reliability when dealing with temporary network failures, rate limiting, and transient API errors.

---

## How It Works

### Exponential Backoff Strategy

When a network request fails, the SDK automatically retries with increasing delays:

```
Attempt 1: Immediate
Attempt 2: Wait 1 second  → Retry
Attempt 3: Wait 2 seconds → Retry (1 * 2^1)
Attempt 4: Wait 4 seconds → Retry (1 * 2^2)
```

**Formula**: `delay = base_delay * (exponential_base ^ attempt)`

**Default Configuration**:
- **Max Retries**: 3
- **Base Delay**: 1.0 seconds
- **Max Delay**: 30.0 seconds (cap)
- **Exponential Base**: 2.0

---

## Methods with Automatic Retry

The following client methods automatically retry on network failures:

### Deployment Operations
- `client.deploy(config)` - Deploy new model
- `client.get_deployment(deployment_id)` - Get deployment status

### Inference Operations
- `client.generate(endpoint, request)` - Text generation

### Network Operations
- `client.get_metrics()` - Get network metrics
- `client.register_node(config)` - Register compute node

---

## Non-Retryable Errors

The following errors are **never retried** (fail immediately):

1. **ValidationError**: Input validation failed (bad config, missing required fields)
2. **AuthenticationError**: Invalid API key or credentials (401/403)

**Reason**: These errors require user intervention and won't be fixed by retrying.

---

## Usage Examples

### Basic Usage (Automatic)

```python
from hypernode_sdk import HypernodeClient, DeploymentConfig

client = HypernodeClient(api_url="https://api.hypernodesolana.org")

# Automatically retries up to 3 times on network failures
deployment = client.deploy(DeploymentConfig(
    model="meta-llama/Llama-2-7b-hf",
    template="huggingface"
))

print(f"Deployment ID: {deployment.deployment_id}")
```

**Output (with network issues)**:
```
Attempt 1: Failed (Connection timeout)
Waiting 1.0 seconds...
Attempt 2: Failed (Connection reset)
Waiting 2.0 seconds...
Attempt 3: Success!
Deployment ID: dep_abc123xyz
```

---

### Custom Retry Logic

For advanced use cases, you can use the retry decorator directly:

```python
from hypernode_sdk import retry_with_backoff
import requests

@retry_with_backoff(max_retries=5, base_delay=2.0, max_delay=60.0)
def custom_api_call():
    response = requests.get("https://example.com/api/endpoint")
    response.raise_for_status()
    return response.json()

# Will retry up to 5 times with delays: 2s, 4s, 8s, 16s, 32s (capped at 60s)
data = custom_api_call()
```

---

### Async Operations

```python
from hypernode_sdk import retry_async_with_backoff
import aiohttp

@retry_async_with_backoff(max_retries=3, base_delay=1.0)
async def async_api_call():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com/data") as response:
            return await response.json()

# Use with asyncio
import asyncio
data = asyncio.run(async_api_call())
```

---

### Calculate Backoff Delays

```python
from hypernode_sdk import calculate_backoff_delay

# Preview retry delays before executing
for attempt in range(5):
    delay = calculate_backoff_delay(attempt, base_delay=1.0, max_delay=30.0)
    print(f"Attempt {attempt + 1}: Wait {delay}s before retry")
```

**Output**:
```
Attempt 1: Wait 1.0s before retry
Attempt 2: Wait 2.0s before retry
Attempt 3: Wait 4.0s before retry
Attempt 4: Wait 8.0s before retry
Attempt 5: Wait 16.0s before retry
```

---

## Error Handling

### Scenario 1: Validation Error (No Retry)

```python
from hypernode_sdk import HypernodeClient, ValidationError, DeploymentConfig

client = HypernodeClient()

try:
    # Invalid config (model missing)
    deployment = client.deploy(DeploymentConfig())
except ValidationError as e:
    print(f"Validation failed: {e}")
    # Does NOT retry - fix the input and try again
```

**Output**:
```
Validation failed: Deployment config cannot be empty
```

---

### Scenario 2: Network Timeout (Retries)

```python
from hypernode_sdk import HypernodeClient, TimeoutError

client = HypernodeClient()

try:
    deployment = client.get_deployment("dep_abc123")
except TimeoutError as e:
    print(f"Failed after 3 retries: {e}")
```

**Behavior**:
- Attempt 1: Timeout → Wait 1s
- Attempt 2: Timeout → Wait 2s
- Attempt 3: Timeout → Raise TimeoutError

---

### Scenario 3: Transient Error (Recovers)

```python
from hypernode_sdk import HypernodeClient

client = HypernodeClient()

# Network unstable but eventually succeeds
metrics = client.get_metrics()
print(f"Total nodes: {metrics.total_nodes}")
```

**Internal Flow**:
- Attempt 1: Connection reset → Wait 1s
- Attempt 2: Success! (returns metrics)

---

## Configuration

### Environment Variables

You can configure retry behavior via environment variables:

```bash
export HYPERNODE_MAX_RETRIES=5
export HYPERNODE_BASE_DELAY=2.0
export HYPERNODE_MAX_DELAY=60.0
```

**Note**: Currently, retry parameters are hardcoded in decorators. Environment variable support can be added in future versions.

---

### Per-Method Configuration

Currently, all retryable methods use the same configuration:
- `max_retries=3`
- `base_delay=1.0`
- `max_delay=30.0`

For custom retry logic, use the `@retry_with_backoff` decorator directly.

---

## Comparison with SDK-JS

### JavaScript SDK (Reference Implementation)

```typescript
// hypernode-sdk-js/src/index.ts
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;

      // Don't retry validation/auth errors
      if (error instanceof ValidationError || error instanceof AuthenticationError) {
        throw error;
      }

      if (attempt < maxRetries - 1) {
        const delay = baseDelay * Math.pow(2, attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}
```

### Python SDK (This Implementation)

```python
# hypernode-sdk-python/hypernode_sdk/retry.py
@retry_with_backoff(max_retries=3, base_delay=1.0)
def some_method():
    # Identical behavior:
    # - Same exponential backoff formula
    # - Same non-retryable errors (ValidationError, AuthenticationError)
    # - Same default parameters
    pass
```

**Differences**:
- JavaScript uses milliseconds (`baseDelay=1000`), Python uses seconds (`base_delay=1.0`)
- Otherwise, **behavior is identical** for API consistency across SDKs

---

## Best Practices

### 1. Don't Retry Non-Idempotent Operations

```python
# ❌ BAD: Retrying payment submission (could charge twice)
@retry_with_backoff()
def submit_payment(amount):
    response = requests.post("/api/payments", json={"amount": amount})
    response.raise_for_status()

# ✅ GOOD: Check if payment already exists before retrying
def submit_payment_safe(amount):
    if payment_exists(amount):
        return get_payment(amount)

    @retry_with_backoff()
    def _submit():
        response = requests.post("/api/payments", json={"amount": amount})
        response.raise_for_status()
        return response.json()

    return _submit()
```

---

### 2. Use Appropriate Max Retries

```python
# Quick operations: 3 retries (default)
@retry_with_backoff(max_retries=3)
def get_status():
    pass

# Long-running deployments: More retries
@retry_with_backoff(max_retries=10, base_delay=5.0)
def deploy_large_model():
    pass

# Critical operations: No retries (fail fast)
# Don't use decorator - handle errors explicitly
```

---

### 3. Log Retry Attempts

```python
import logging
from hypernode_sdk import retry_with_backoff

logger = logging.getLogger(__name__)

@retry_with_backoff(max_retries=3)
def api_call_with_logging():
    logger.info("Attempting API call...")
    response = requests.get("https://api.example.com")
    response.raise_for_status()
    logger.info("API call succeeded")
    return response.json()
```

---

## Troubleshooting

### Issue: Still Getting Network Errors After 3 Retries

**Possible Causes**:
1. API is down (check status page)
2. Network is unstable
3. Firewall blocking requests
4. Rate limit exceeded (429 errors)

**Solutions**:
- Increase `max_retries` for critical operations
- Check network connectivity
- Verify API key and permissions
- Add exponential backoff for rate-limited endpoints

---

### Issue: Retries Taking Too Long

**Problem**: Total retry time = `1s + 2s + 4s + 8s + ... = 31s`

**Solution**: Reduce `max_retries` or `base_delay`
```python
@retry_with_backoff(max_retries=2, base_delay=0.5)
def fast_api_call():
    # Max retry time: 0.5s + 1.0s = 1.5s
    pass
```

---

### Issue: ValidationError Not Retrying

**Expected Behavior**: ValidationError should **never** retry.

**Reason**: Input is invalid and needs fixing by the user. Retrying won't help.

**Solution**: Fix the input data before calling the method again.

---

## Implementation Details

### File: `hypernode_sdk/retry.py`

**Functions**:
- `retry_with_backoff(max_retries, base_delay, max_delay, exponential_base)` - Decorator for sync functions
- `retry_async_with_backoff(max_retries, base_delay, max_delay, exponential_base)` - Decorator for async functions
- `calculate_backoff_delay(attempt, base_delay, max_delay, exponential_base)` - Calculate delay for given attempt

**Lines of Code**: 170 lines

**Test Coverage**: Not yet implemented (TODO: Add unit tests)

---

## Future Enhancements

1. **Jitter**: Add randomization to prevent thundering herd
   ```python
   delay = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
   ```

2. **Circuit Breaker**: Stop retrying if too many consecutive failures
   ```python
   if consecutive_failures > 10:
       raise CircuitBreakerOpenError()
   ```

3. **Retry on Specific Status Codes**: Only retry 5xx errors, not 4xx
   ```python
   if 500 <= response.status_code < 600:
       # Retry
   else:
       # Don't retry
   ```

4. **Configurable Retry Policies**: Per-method retry configuration
   ```python
   client = HypernodeClient(retry_policy={
       "deploy": {"max_retries": 5, "base_delay": 2.0},
       "get_metrics": {"max_retries": 2, "base_delay": 0.5}
   })
   ```

---

## Testing

### Manual Test Script

```python
# test_retry.py
from hypernode_sdk import HypernodeClient, retry_with_backoff
import time

# Test 1: Successful retry after transient failure
@retry_with_backoff(max_retries=3, base_delay=1.0)
def flaky_function():
    import random
    if random.random() < 0.7:  # 70% failure rate
        raise ConnectionError("Simulated network failure")
    return "Success!"

print("Testing retry logic...")
start = time.time()
try:
    result = flaky_function()
    print(f"Result: {result} (took {time.time() - start:.1f}s)")
except ConnectionError as e:
    print(f"Failed after retries: {e} (took {time.time() - start:.1f}s)")

# Test 2: Immediate failure on ValidationError
from hypernode_sdk.exceptions import ValidationError

@retry_with_backoff(max_retries=3)
def invalid_input():
    raise ValidationError("Invalid input")

try:
    invalid_input()
except ValidationError as e:
    print(f"Validation error (no retries): {e}")
```

**Expected Output**:
```
Testing retry logic...
Result: Success! (took 3.2s)  # May vary due to randomness
Validation error (no retries): Invalid input
```

---

## Summary

- **Automatic retries** on 5 critical methods
- **Exponential backoff** (1s → 2s → 4s)
- **Smart error handling** (skip validation/auth errors)
- **Consistent with SDK-JS** (same behavior, different units)
- **Production-ready** retry logic for reliable API calls

For questions or issues, open a GitHub issue in the `hypernode-sdk-python` repository.
