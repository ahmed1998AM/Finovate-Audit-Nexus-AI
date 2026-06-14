"""
Finovate Audit Nexus AI - LLM Interface (Abstract Base Class)
Defines the interface for all LLM providers
Enterprise AI Financial Audit & Intelligence Platform
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class LLMResponse:
    """Standard response format from LLM providers"""
    content: str
    model: str
    provider: str
    tokens_used: int
    timestamp: datetime
    confidence: float = 0.0
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "tokens_used": self.tokens_used,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "metadata": self.metadata or {}
        }


@dataclass
class LLMMessage:
    """Message format for chat-based LLMs"""
    role: str  # "system", "user", "assistant"
    content: str


class LLMInterface(ABC):
    """
    Abstract base class for all LLM providers
    Defines the interface that all LLM implementations must follow
    """

    def __init__(self, provider_name: str, api_key: str, model: str):
        """
        Initialize LLM provider
        Args:
            provider_name: Name of the provider (e.g., "openai", "anthropic")
            api_key: API key for authentication
            model: Model name/identifier
        """
        self.provider_name = provider_name
        self.api_key = api_key
        self.model = model
        self.tokens_used = 0
        self.requests_count = 0

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0
    ) -> LLMResponse:
        """
        Generate text from a prompt
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty
            presence_penalty: Presence penalty
        Returns:
            LLMResponse object
        """
        pass

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """
        Generate chat completion from messages
        Args:
            messages: List of LLMMessage objects
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
        Returns:
            LLMResponse object
        """
        pass

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embeddings for text
        Args:
            text: Text to embed
        Returns:
            List of floats representing the embedding
        """
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """
        List available models from this provider
        Returns:
            List of model names
        """
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """
        Validate that the connection to the provider is working
        Returns:
            True if connection is valid, False otherwise
        """
        pass

    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about this provider
        Returns:
            Dictionary with provider information
        """
        pass

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics for this provider
        Returns:
            Dictionary with usage stats
        """
        return {
            "provider": self.provider_name,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "requests_count": self.requests_count,
            "average_tokens_per_request": (
                self.tokens_used / self.requests_count
                if self.requests_count > 0
                else 0
            )
        }

    def reset_stats(self):
        """Reset usage statistics"""
        self.tokens_used = 0
        self.requests_count = 0


class LLMProviderFactory:
    """Factory for creating LLM provider instances"""

    _providers = {}

    @classmethod
    def register_provider(cls, provider_name: str, provider_class: type):
        """Register a new LLM provider"""
        cls._providers[provider_name.lower()] = provider_class

    @classmethod
    def create_provider(
        cls,
        provider_name: str,
        api_key: str,
        model: str,
        **kwargs
    ) -> LLMInterface:
        """
        Create an LLM provider instance
        Args:
            provider_name: Name of the provider
            api_key: API key for the provider
            model: Model name
            **kwargs: Additional provider-specific arguments
        Returns:
            LLMInterface instance
        Raises:
            ValueError: If provider is not registered
        """
        provider_class = cls._providers.get(provider_name.lower())
        if provider_class is None:
            raise ValueError(f"Unknown provider: {provider_name}")
        return provider_class(provider_name, api_key, model, **kwargs)

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available providers"""
        return list(cls._providers.keys())
