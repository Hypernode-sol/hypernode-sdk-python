# Hypernode Python SDK

Official Python SDK for interacting with the Hypernode decentralized compute network.

## Installation

```bash
pip install hypernode-sdk
```

## Quick Start

### Initialize Client

```python
from hypernode_sdk import HypernodeClient

client = HypernodeClient(
    api_key='your_api_key',  # Optional
    api_url='https://api.hypernodesolana.org',  # Optional
    rpc_url='https://api.mainnet-beta.solana.com'  # Optional
)
```

### Deploy a Model

```python
from hypernode_sdk import DeploymentConfig

# Deploy Stable Diffusion
deployment = client.deploy(
    DeploymentConfig(
        model='stable-diffusion-v1-5',
        template='stable-diffusion',
        gpu_memory='8GB',
        replicas=2,
        auto_scale=True,
        min_replicas=1,
        max_replicas=5,
        region='us-west'
    )
)

print(f"Deployed at: {deployment.endpoint}")
print(f"Deployment ID: {deployment.deployment_id}")
```

### Generate Text

```python
from hypernode_sdk import DeploymentConfig, GenerationRequest

# Deploy LLM
llm = client.deploy(
    DeploymentConfig(
        model='meta-llama/Llama-2-7b-chat-hf',
        template='pytorch',
        gpu_memory='16GB'
    )
)

# Generate text
result = client.generate(
    llm.endpoint,
    GenerationRequest(
        prompt='Explain quantum computing in simple terms',
        max_tokens=200,
        temperature=0.7
    )
)

print(result.generated_text)
```

### Generate Images

```python
from hypernode_sdk import ImageGenerationRequest
import base64

# Deploy Stable Diffusion
sd = client.deploy(
    DeploymentConfig(
        model='stable-diffusion-v1-5',
        template='stable-diffusion',
        gpu_memory='8GB'
    )
)

# Generate image
result = client.generate_image(
    sd.endpoint,
    ImageGenerationRequest(
        prompt='A serene mountain landscape at sunset, oil painting',
        negative_prompt='blurry, low quality',
        num_inference_steps=30,
        guidance_scale=7.5,
        width=512,
        height=512
    )
)

# Save image
image_data = base64.b64decode(result.images[0])
with open('output.png', 'wb') as f:
    f.write(image_data)

print(f"Image saved! Seed: {result.seed}")
```

### Get Embeddings

```python
# Deploy sentence transformer
embeddings = client.deploy(
    DeploymentConfig(
        model='sentence-transformers/all-MiniLM-L6-v2',
        template='huggingface',
        gpu_memory='4GB'
    )
)

# Get embeddings
vector = client.get_embeddings(
    embeddings.endpoint,
    'Hypernode is a decentralized compute network'
)

print(f"Embedding dimensions: {len(vector)}")  # 384
```

## API Reference

### HypernodeClient

#### `__init__(api_url, rpc_url, api_key)`

Initialize Hypernode client.

**Parameters:**
- `api_url` (str): Hypernode API URL (default: `https://api.hypernodesolana.org`)
- `rpc_url` (str): Solana RPC URL (default: `https://api.mainnet-beta.solana.com`)
- `api_key` (str, optional): Your API key

#### `deploy(config: DeploymentConfig) -> DeploymentResponse`

Deploy a new AI model.

**Parameters:**
- `config` (DeploymentConfig): Deployment configuration
  - `model` (str): Model ID (e.g., 'meta-llama/Llama-2-7b')
  - `template` (str, optional): 'pytorch' | 'huggingface' | 'stable-diffusion'
  - `gpu_memory` (str, optional): e.g., '8GB', '16GB'
  - `replicas` (int, optional): Number of replicas (default: 1)
  - `auto_scale` (bool, optional): Enable auto-scaling
  - `min_replicas` (int, optional): Min replicas for auto-scaling
  - `max_replicas` (int, optional): Max replicas for auto-scaling
  - `region` (str, optional): Preferred region
  - `env` (dict, optional): Environment variables

#### `get_deployment(deployment_id: str) -> DeploymentResponse`

Get deployment status and information.

#### `list_deployments() -> List[DeploymentResponse]`

List all your deployments.

#### `terminate_deployment(deployment_id: str) -> None`

Terminate a deployment.

#### `scale_deployment(deployment_id: str, replicas: int) -> None`

Manually scale a deployment.

#### `generate(endpoint: str, request: GenerationRequest) -> GenerationResponse`

Generate text using deployed LLM.

**Parameters:**
- `endpoint` (str): Deployment endpoint URL
- `request` (GenerationRequest):
  - `prompt` (str): Input prompt
  - `max_tokens` (int, optional): Max tokens to generate
  - `temperature` (float, optional): Sampling temperature (0-2)
  - `top_p` (float, optional): Nucleus sampling
  - `stop_sequences` (list, optional): Stop sequences

#### `generate_image(endpoint: str, request: ImageGenerationRequest) -> ImageGenerationResponse`

Generate images using Stable Diffusion.

**Parameters:**
- `endpoint` (str): Deployment endpoint URL
- `request` (ImageGenerationRequest):
  - `prompt` (str): Text description
  - `negative_prompt` (str, optional): What to avoid
  - `num_inference_steps` (int, optional): Number of steps (15-50)
  - `guidance_scale` (float, optional): Prompt adherence (1-20)
  - `width` (int, optional): Image width
  - `height` (int, optional): Image height
  - `num_images` (int, optional): Number of images (1-4)
  - `seed` (int, optional): Random seed

#### `get_embeddings(endpoint: str, text: str, normalize: bool = True) -> List[float]`

Get text embeddings.

#### `classify(endpoint: str, text: str, top_k: int = 5) -> List[dict]`

Classify text.

#### `get_metrics() -> Metrics`

Get network metrics.

#### `get_nodes() -> List[Node]`

Get available nodes.

## Examples

### Complete Example: Text Generation

```python
import os
import time
from hypernode_sdk import HypernodeClient, DeploymentConfig, GenerationRequest

def main():
    client = HypernodeClient(
        api_key=os.getenv('HYPERNODE_API_KEY')
    )

    # Deploy Llama 2
    print('Deploying Llama 2...')
    deployment = client.deploy(
        DeploymentConfig(
            model='meta-llama/Llama-2-7b-chat-hf',
            template='pytorch',
            gpu_memory='16GB',
            replicas=2,
            auto_scale=True
        )
    )

    print(f"Deployment ID: {deployment.deployment_id}")
    print(f"Endpoint: {deployment.endpoint}")

    # Wait for deployment to be ready
    status = deployment.status
    while status != 'running':
        time.sleep(5)
        updated = client.get_deployment(deployment.deployment_id)
        status = updated.status
        print(f"Status: {status}")

    # Generate text
    print('Generating text...')
    result = client.generate(
        deployment.endpoint,
        GenerationRequest(
            prompt='Write a haiku about decentralized computing',
            max_tokens=50,
            temperature=0.8
        )
    )

    print(f"Generated: {result.generated_text}")
    print(f"Tokens: {result.tokens_generated}")
    print(f"Device: {result.device}")

    # Cleanup
    client.terminate_deployment(deployment.deployment_id)
    print('Deployment terminated')

if __name__ == '__main__':
    main()
```

### Complete Example: Image Generation

```python
import os
import time
import base64
from hypernode_sdk import HypernodeClient, DeploymentConfig, ImageGenerationRequest

def generate_image():
    client = HypernodeClient(
        api_key=os.getenv('HYPERNODE_API_KEY')
    )

    # Deploy Stable Diffusion
    deployment = client.deploy(
        DeploymentConfig(
            model='stable-diffusion-v1-5',
            template='stable-diffusion',
            gpu_memory='8GB'
        )
    )

    # Wait for ready
    status = deployment.status
    while status != 'running':
        time.sleep(5)
        updated = client.get_deployment(deployment.deployment_id)
        status = updated.status

    # Generate image
    result = client.generate_image(
        deployment.endpoint,
        ImageGenerationRequest(
            prompt='A futuristic city at night, neon lights, cyberpunk, 4k',
            negative_prompt='blurry, low quality',
            num_inference_steps=30,
            guidance_scale=7.5,
            width=768,
            height=512,
            seed=42
        )
    )

    # Save image
    image_data = base64.b64decode(result.images[0])
    with open('output.png', 'wb') as f:
        f.write(image_data)

    print(f"Image saved! Seed: {result.seed}")

    # Cleanup
    client.terminate_deployment(deployment.deployment_id)

if __name__ == '__main__':
    generate_image()
```

### Async Support

The SDK uses synchronous requests by default. For async operations, use `asyncio`:

```python
import asyncio
from hypernode_sdk import HypernodeClient

async def async_generate():
    client = HypernodeClient(api_key='your_key')

    # Run in executor for async behavior
    loop = asyncio.get_event_loop()
    deployment = await loop.run_in_executor(
        None,
        client.deploy,
        DeploymentConfig(model='gpt2', template='pytorch')
    )

    return deployment

asyncio.run(async_generate())
```

## Error Handling

```python
from requests.exceptions import HTTPError

try:
    deployment = client.deploy(config)
except HTTPError as e:
    if e.response.status_code == 401:
        print('Invalid API key')
    elif e.response.status_code == 400:
        print(f'Bad request: {e.response.json()}')
    else:
        print(f'HTTP Error: {e}')
except Exception as e:
    print(f'Error: {e}')
```

## Type Hints

The SDK includes full type hints for better IDE support:

```python
from hypernode_sdk import HypernodeClient, DeploymentConfig, GenerationRequest

client: HypernodeClient = HypernodeClient()
config: DeploymentConfig = DeploymentConfig(
    model='meta-llama/Llama-2-7b-chat-hf',
    template='pytorch'
)
request: GenerationRequest = GenerationRequest(
    prompt='Hello world',
    max_tokens=100
)
```

## License

MIT

## Support

- **Docs**: [docs.hypernodesolana.org](https://docs.hypernodesolana.org)
- **GitHub**: [github.com/Hypernode-sol/hypernode-sdk-python](https://github.com/Hypernode-sol/hypernode-sdk-python)
- **Email**: contact@hypernodesolana.org
