"""
Hypernode Client Implementation
"""

import requests
from typing import Optional, List, Dict, Any
from solana.rpc.api import Client as SolanaClient

from .types import (
    DeploymentConfig,
    DeploymentResponse,
    GenerationRequest,
    GenerationResponse,
    ImageGenerationRequest,
    ImageGenerationResponse,
    Node,
    Metrics,
)


class HypernodeClient:
    """
    Main client for interacting with Hypernode network
    """

    def __init__(
        self,
        api_url: str = "https://api.hypernodesolana.org",
        rpc_url: str = "https://api.mainnet-beta.solana.com",
        api_key: Optional[str] = None,
    ):
        """
        Initialize Hypernode client

        Args:
            api_url: Hypernode API endpoint
            rpc_url: Solana RPC endpoint
            api_key: Optional API key for authentication
        """
        self.api_url = api_url.rstrip("/")
        self.rpc_url = rpc_url
        self.api_key = api_key

        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

        self.solana_client = SolanaClient(rpc_url)

    def deploy(self, config: DeploymentConfig) -> DeploymentResponse:
        """
        Deploy a new AI model

        Args:
            config: Deployment configuration

        Returns:
            DeploymentResponse with deployment details
        """
        response = self.session.post(
            f"{self.api_url}/v1/deployments",
            json=config.dict()
        )
        response.raise_for_status()
        return DeploymentResponse(**response.json())

    def get_deployment(self, deployment_id: str) -> DeploymentResponse:
        """
        Get deployment status and information

        Args:
            deployment_id: Deployment ID

        Returns:
            DeploymentResponse with current status
        """
        response = self.session.get(
            f"{self.api_url}/v1/deployments/{deployment_id}"
        )
        response.raise_for_status()
        return DeploymentResponse(**response.json())

    def list_deployments(self) -> List[DeploymentResponse]:
        """
        List all deployments

        Returns:
            List of deployments
        """
        response = self.session.get(f"{self.api_url}/v1/deployments")
        response.raise_for_status()
        return [DeploymentResponse(**d) for d in response.json()]

    def terminate_deployment(self, deployment_id: str) -> None:
        """
        Terminate a deployment

        Args:
            deployment_id: Deployment ID to terminate
        """
        response = self.session.delete(
            f"{self.api_url}/v1/deployments/{deployment_id}"
        )
        response.raise_for_status()

    def scale_deployment(self, deployment_id: str, replicas: int) -> None:
        """
        Scale a deployment

        Args:
            deployment_id: Deployment ID
            replicas: Number of replicas
        """
        response = self.session.post(
            f"{self.api_url}/v1/deployments/{deployment_id}/scale",
            json={"replicas": replicas}
        )
        response.raise_for_status()

    def generate(
        self,
        endpoint: str,
        request: GenerationRequest
    ) -> GenerationResponse:
        """
        Generate text using deployed LLM

        Args:
            endpoint: Deployment endpoint URL
            request: Generation request parameters

        Returns:
            GenerationResponse with generated text
        """
        response = requests.post(
            f"{endpoint}/generate",
            json=request.dict(exclude_none=True)
        )
        response.raise_for_status()
        return GenerationResponse(**response.json())

    def generate_image(
        self,
        endpoint: str,
        request: ImageGenerationRequest
    ) -> ImageGenerationResponse:
        """
        Generate images using Stable Diffusion

        Args:
            endpoint: Deployment endpoint URL
            request: Image generation parameters

        Returns:
            ImageGenerationResponse with generated images
        """
        response = requests.post(
            f"{endpoint}/generate",
            json=request.dict(exclude_none=True)
        )
        response.raise_for_status()
        return ImageGenerationResponse(**response.json())

    def get_embeddings(
        self,
        endpoint: str,
        text: str,
        normalize: bool = True
    ) -> List[float]:
        """
        Get text embeddings

        Args:
            endpoint: Deployment endpoint URL
            text: Input text
            normalize: Whether to normalize the embeddings

        Returns:
            List of embedding values
        """
        response = requests.post(
            f"{endpoint}/embed",
            json={"text": text, "normalize": normalize}
        )
        response.raise_for_status()
        return response.json()["embedding"]

    def classify(
        self,
        endpoint: str,
        text: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Classify text

        Args:
            endpoint: Deployment endpoint URL
            text: Input text
            top_k: Number of top results to return

        Returns:
            List of classification results
        """
        response = requests.post(
            f"{endpoint}/classify",
            json={"text": text, "top_k": top_k}
        )
        response.raise_for_status()
        return response.json()["results"]

    def get_metrics(self) -> Metrics:
        """
        Get network metrics

        Returns:
            Metrics object with network statistics
        """
        response = self.session.get(f"{self.api_url}/v1/metrics")
        response.raise_for_status()
        return Metrics(**response.json())

    def get_nodes(self) -> List[Node]:
        """
        Get available nodes

        Returns:
            List of nodes
        """
        response = self.session.get(f"{self.api_url}/v1/nodes")
        response.raise_for_status()
        return [Node(**n) for n in response.json()]

    def register_node(self, node_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new node

        Args:
            node_config: Node configuration

        Returns:
            Registration response
        """
        response = self.session.post(
            f"{self.api_url}/v1/nodes/register",
            json=node_config
        )
        response.raise_for_status()
        return response.json()

    def get_solana_client(self) -> SolanaClient:
        """
        Get Solana RPC client

        Returns:
            Solana client instance
        """
        return self.solana_client


def create_client(
    api_url: str = "https://api.hypernodesolana.org",
    rpc_url: str = "https://api.mainnet-beta.solana.com",
    api_key: Optional[str] = None,
) -> HypernodeClient:
    """
    Helper function to create a client

    Args:
        api_url: Hypernode API endpoint
        rpc_url: Solana RPC endpoint
        api_key: Optional API key

    Returns:
        HypernodeClient instance
    """
    return HypernodeClient(api_url=api_url, rpc_url=rpc_url, api_key=api_key)
