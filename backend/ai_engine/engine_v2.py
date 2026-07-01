"""
Finovate Audit Nexus AI - Enhanced AI Engine V2
Multi-provider LLM management and orchestration
Enterprise AI Financial Audit & Intelligence Platform
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from backend.ai_engine.llm_interface import (
    LLMInterface,
    LLMMessage,
    LLMProviderFactory,
    LLMResponse,
)
from backend.ai_engine.providers.anthropic_provider import AnthropicProvider
from backend.ai_engine.providers.gemini_provider import GeminiProvider
from backend.ai_engine.providers.groq_provider import GroqProvider
from backend.ai_engine.providers.ollama_provider import OllamaProvider
from backend.ai_engine.providers.openai_provider import OpenAIProvider


class AIEngineV2:
    """
    Enhanced AI Engine V2 - Multi-Provider LLM Management

    Features:
    - Support for multiple LLM providers (OpenAI, Anthropic, Gemini, Groq, Ollama)
    - Provider switching and fallback mechanisms
    - Token usage tracking and cost estimation
    - Caching and context management
    - Advanced prompt engineering
    """

    def __init__(self):
        """Initialize the enhanced AI engine"""
        self.engine_id = "ai_engine_v2_001"
        self.name = "AI Engine V2"
        self.status = "initialized"

        # Provider management
        self.providers: Dict[str, LLMInterface] = {}
        self.active_provider: Optional[str] = None
        self.active_model: Optional[str] = None

        # Statistics
        self.tokens_used = 0
        self.requests_count = 0
        self.provider_stats: Dict[str, Dict[str, Any]] = {}

        # Configuration
        self.config = self._load_config()

        # Register providers
        self._register_providers()

        # Initialize configured providers
        self._initialize_providers()

        logger.info(f"{self.name} initialized: {self.engine_id}")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment and config file"""
        config = {
            "providers": {},
            "default_provider": os.getenv("DEFAULT_LLM_PROVIDER", "openai"),
            "fallback_providers": os.getenv("FALLBACK_LLM_PROVIDERS", "ollama,anthropic,gemini,groq").split(","),
            "cache_enabled": os.getenv("LLM_CACHE_ENABLED", "true").lower() == "true",
            "cache_ttl": int(os.getenv("LLM_CACHE_TTL", "3600")),
            "max_retries": int(os.getenv("LLM_MAX_RETRIES", "3")),
            "timeout": int(os.getenv("LLM_TIMEOUT", "300"))
        }

        # Load provider-specific configurations
        if os.getenv("OPENAI_API_KEY"):
            config["providers"]["openai"] = {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model": os.getenv("OPENAI_MODEL", "gpt-4")
            }

        if os.getenv("ANTHROPIC_API_KEY"):
            config["providers"]["anthropic"] = {
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "model": os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
            }

        if os.getenv("GOOGLE_API_KEY"):
            config["providers"]["gemini"] = {
                "api_key": os.getenv("GOOGLE_API_KEY"),
                "model": os.getenv("GEMINI_MODEL", "gemini-pro")
            }

        if os.getenv("GROQ_API_KEY"):
            config["providers"]["groq"] = {
                "api_key": os.getenv("GROQ_API_KEY"),
                "model": os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
            }

        # Ollama is local, so it doesn't need an API key
        config["providers"]["ollama"] = {
            "api_key": "local",
            "model": os.getenv("OLLAMA_MODEL", "llama2"),
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        }

        return config

    def _register_providers(self):
        """Register all available providers with the factory"""
        LLMProviderFactory.register_provider("openai", OpenAIProvider)
        LLMProviderFactory.register_provider("anthropic", AnthropicProvider)
        LLMProviderFactory.register_provider("gemini", GeminiProvider)
        LLMProviderFactory.register_provider("groq", GroqProvider)
        LLMProviderFactory.register_provider("ollama", OllamaProvider)
        logger.info("All LLM providers registered")

    def _initialize_providers(self):
        """Initialize configured providers"""
        for provider_name, config in self.config["providers"].items():
            try:
                if provider_name == "ollama":
                    provider = OllamaProvider(
                        api_key=config["api_key"],
                        model=config["model"],
                        base_url=config.get("base_url", "http://localhost:11434")
                    )
                else:
                    provider = LLMProviderFactory.create_provider(
                        provider_name,
                        config["api_key"],
                        config["model"]
                    )

                self.providers[provider_name] = provider
                self.provider_stats[provider_name] = {
                    "initialized": True,
                    "status": "ready",
                    "last_used": None,
                    "total_tokens": 0,
                    "total_requests": 0
                }
                logger.info(f"Provider '{provider_name}' initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize provider '{provider_name}': {str(e)}")
                self.provider_stats[provider_name] = {
                    "initialized": False,
                    "status": "error",
                    "error": str(e)
                }

    def select_provider(self, provider_name: str, model_name: Optional[str] = None) -> bool:
        """
        Select an active provider
        Args:
            provider_name: Name of the provider to activate
            model_name: Optional model name to use
        Returns:
            True if provider was selected successfully
        """
        try:
            if provider_name not in self.providers:
                logger.error(f"Provider '{provider_name}' not available")
                return False

            provider = self.providers[provider_name]

            if model_name:
                provider.model = model_name

            self.active_provider = provider_name
            self.active_model = provider.model

            logger.info(f"Selected provider: {provider_name}, model: {provider.model}")
            return True
        except Exception as e:
            logger.error(f"Error selecting provider: {str(e)}")
            return False

    async def _try_provider(
        self,
        provider_name: str,
        method: str,
        **kwargs
    ) -> LLMResponse:
        """Try generating with a specific provider, returns None on failure"""
        try:
            if provider_name not in self.providers:
                logger.warning(f"Provider '{provider_name}' not available")
                return None
            provider_instance = self.providers[provider_name]
            if method == "generate_text":
                response = await provider_instance.generate_text(**kwargs)
            else:
                response = await provider_instance.chat_completion(**kwargs)
            self.tokens_used += response.tokens_used
            self.requests_count += 1
            if provider_name in self.provider_stats:
                self.provider_stats[provider_name]["last_used"] = datetime.now()
                self.provider_stats[provider_name]["total_tokens"] += response.tokens_used
                self.provider_stats[provider_name]["total_requests"] += 1
            self.status = "ready"
            return response
        except Exception as e:
            logger.warning(f"Provider '{provider_name}' failed: {str(e)}")
            return None

    async def generate_text(
        self,
        prompt: str,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        """
        Generate text using the active or specified provider with automatic fallback
        Args:
            prompt: Input prompt
            provider: Optional provider name (uses active provider if not specified)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific arguments
        Returns:
            LLMResponse object
        """
        if provider is None:
            provider = self.active_provider or self.config["default_provider"]

        # Build ordered provider list: preferred first, then fallbacks, then any available
        provider_chain = [provider]
        for fb in self.config.get("fallback_providers", []):
            fb = fb.strip()
            if fb and fb not in provider_chain:
                provider_chain.append(fb)
        for p in self.providers:
            if p not in provider_chain:
                provider_chain.append(p)

        last_error = None
        for pname in provider_chain:
            result = await self._try_provider(
                pname, "generate_text",
                prompt=prompt, temperature=temperature,
                max_tokens=max_tokens, **kwargs
            )
            if result is not None:
                if pname != provider:
                    logger.info(f"Fell back to provider '{pname}' after '{provider}' failed")
                return result
            last_error = "No available provider could handle the request"

        self.status = "error"
        raise ValueError(last_error)

    async def chat_completion(
        self,
        messages: List[LLMMessage],
        provider: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        """
        Generate chat completion using the active or specified provider with fallback
        Args:
            messages: List of LLMMessage objects
            provider: Optional provider name
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific arguments
        Returns:
            LLMResponse object
        """
        if provider is None:
            provider = self.active_provider or self.config["default_provider"]

        provider_chain = [provider]
        for fb in self.config.get("fallback_providers", []):
            fb = fb.strip()
            if fb and fb not in provider_chain:
                provider_chain.append(fb)
        for p in self.providers:
            if p not in provider_chain:
                provider_chain.append(p)

        for pname in provider_chain:
            result = await self._try_provider(
                pname, "chat_completion",
                messages=messages, system_prompt=system_prompt,
                temperature=temperature, max_tokens=max_tokens, **kwargs
            )
            if result is not None:
                if pname != provider:
                    logger.info(f"Chat fell back to provider '{pname}' after '{provider}' failed")
                return result

        self.status = "error"
        raise ValueError("No available provider could handle the chat completion request")

    async def embed_text(self, text: str, provider: Optional[str] = None) -> List[float]:
        """
        Generate embeddings for text
        Args:
            text: Text to embed
            provider: Optional provider name
        Returns:
            List of floats representing the embedding
        """
        try:
            if provider is None:
                provider = self.active_provider or self.config["default_provider"]

            if provider not in self.providers:
                raise ValueError(f"Provider '{provider}' not available")

            provider_instance = self.providers[provider]

            logger.info(f"Generating embeddings with provider: {provider}")

            embedding = await provider_instance.embed_text(text)

            self.requests_count += 1
            self.provider_stats[provider]["total_requests"] += 1

            return embedding

        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())

    def get_provider_info(self, provider_name: str) -> Dict[str, Any]:
        """Get information about a specific provider"""
        if provider_name not in self.providers:
            return {}

        provider = self.providers[provider_name]
        return provider.get_provider_info()

    def get_all_providers_info(self) -> Dict[str, Any]:
        """Get information about all providers"""
        return {
            name: provider.get_provider_info()
            for name, provider in self.providers.items()
        }

    def get_status(self) -> Dict[str, Any]:
        """Get engine status"""
        return {
            "engine_id": self.engine_id,
            "name": self.name,
            "status": self.status,
            "active_provider": self.active_provider,
            "active_model": self.active_model,
            "providers_available": self.get_available_providers(),
            "tokens_used": self.tokens_used,
            "requests_count": self.requests_count,
            "provider_stats": self.provider_stats
        }

    def reset_statistics(self):
        """Reset usage statistics"""
        self.tokens_used = 0
        self.requests_count = 0
        for provider_name in self.provider_stats:
            self.provider_stats[provider_name]["total_tokens"] = 0
            self.provider_stats[provider_name]["total_requests"] = 0
        logger.info("AI Engine statistics reset")


# Singleton instance
_ai_engine_v2_instance: Optional[AIEngineV2] = None


def get_ai_engine_v2() -> AIEngineV2:
    """Get or create AI Engine V2 singleton"""
    global _ai_engine_v2_instance
    if _ai_engine_v2_instance is None:
        _ai_engine_v2_instance = AIEngineV2()
    return _ai_engine_v2_instance
