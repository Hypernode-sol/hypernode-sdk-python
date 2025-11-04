"""
Type definitions for Hypernode SDK
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class DeploymentConfig(BaseModel):
    """Configuration for deploying a model"""
    model: str
    template: Optional[Literal["pytorch", "huggingface", "stable-diffusion", "custom"]] = None
    gpu_memory: Optional[str] = Field(None, alias="gpuMemory")
    replicas: Optional[int] = 1
    auto_scale: Optional[bool] = Field(None, alias="autoScale")
    min_replicas: Optional[int] = Field(None, alias="minReplicas")
    max_replicas: Optional[int] = Field(None, alias="maxReplicas")
    region: Optional[str] = None
    env: Optional[Dict[str, str]] = None

    class Config:
        populate_by_name = True


class DeploymentResponse(BaseModel):
    """Response from deployment operations"""
    deployment_id: str = Field(alias="deploymentId")
    endpoint: str
    status: Literal["pending", "deploying", "running", "failed"]
    created_at: str = Field(alias="createdAt")

    class Config:
        populate_by_name = True


class GenerationRequest(BaseModel):
    """Request for text generation"""
    prompt: str
    max_tokens: Optional[int] = Field(None, alias="maxTokens")
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = Field(None, alias="topP")
    stop_sequences: Optional[List[str]] = Field(None, alias="stopSequences")

    class Config:
        populate_by_name = True


class GenerationResponse(BaseModel):
    """Response from text generation"""
    generated_text: str = Field(alias="generatedText")
    tokens_generated: int = Field(alias="tokensGenerated")
    device: str

    class Config:
        populate_by_name = True


class ImageGenerationRequest(BaseModel):
    """Request for image generation"""
    prompt: str
    negative_prompt: Optional[str] = Field(None, alias="negativePrompt")
    num_inference_steps: Optional[int] = Field(25, alias="numInferenceSteps")
    guidance_scale: Optional[float] = Field(7.5, alias="guidanceScale")
    width: Optional[int] = 512
    height: Optional[int] = 512
    num_images: Optional[int] = Field(1, alias="numImages")
    seed: Optional[int] = None

    class Config:
        populate_by_name = True


class ImageGenerationResponse(BaseModel):
    """Response from image generation"""
    images: List[str]  # Base64 encoded
    seed: int
    model: str


class NodeHardware(BaseModel):
    """Node hardware specifications"""
    architecture: str
    cpu: str
    memory: int
    gpu: Optional[str] = None
    gpu_memory: Optional[int] = Field(None, alias="gpuMemory")
    disk: int

    class Config:
        populate_by_name = True


class Node(BaseModel):
    """Node information"""
    id: str
    public_key: str = Field(alias="publicKey")
    hardware: NodeHardware
    reputation: int
    uptime: float
    country: str
    status: Literal["active", "offline", "busy"]
    total_jobs_completed: int = Field(alias="totalJobsCompleted")
    total_earned: float = Field(alias="totalEarned")

    class Config:
        populate_by_name = True


class Job(BaseModel):
    """Job information"""
    id: str
    client_public_key: str = Field(alias="clientPublicKey")
    node_id: Optional[str] = Field(None, alias="nodeId")
    model: str
    status: Literal["pending", "running", "completed", "failed"]
    price: float
    created_at: str = Field(alias="createdAt")
    completed_at: Optional[str] = Field(None, alias="completedAt")
    result: Optional[str] = None

    class Config:
        populate_by_name = True


class StakeInfo(BaseModel):
    """Staking information"""
    amount: float
    duration: int
    multiplier: float
    xnos: float
    tier: Literal["starter", "bronze", "silver", "gold", "diamond"]
    unlock_time: int = Field(alias="unlockTime")

    class Config:
        populate_by_name = True


class Metrics(BaseModel):
    """Network metrics"""
    total_deployments: int = Field(alias="totalDeployments")
    compute_hours: int = Field(alias="computeHours")
    active_nodes: int = Field(alias="activeNodes")
    countries: int
    total_earned: float = Field(alias="totalEarned")
    avg_uptime: float = Field(alias="avgUptime")
    success_rate: float = Field(alias="successRate")

    class Config:
        populate_by_name = True
