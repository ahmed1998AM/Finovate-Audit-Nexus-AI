"""
Finovate Audit Nexus AI - Anthropic Provider
Implementation of LLMInterface for Anthropic Claude API
Enterprise AI Financial Audit & Intelligence Platform
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

try:
    import anthropic
except ImportError:
    logger.error("Anthropic library not installed. Install with: pip install anthropic")
    anthropic = None

from backend.ai_engine.llm_interface import LLMInterface, LLMResponse, LLMMessage


class AnthropicProvider(LLMInterface):
    """
    Anthropic LLM Provider
    Supports Claude models (Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku)
    """

    def __init__(
        self,
        provider_name: str = "anthropic",
        api_key: Optional[str] = None,
        model: str = "claude-3-opus-20240229"
    ):
        """
        Initialize Anthropic provider
        Args:
            provider_name: Provider name (default: "anthropic")
            api_key: Anthropic API key (if None, uses ANTHROPIC_API_KEY env var)
            model: Model name (default: "claude-3-opus-20240229")
        """
        if api_key is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    "Anthropic API key not provided and ANTHROPIC_API_KEY environment variable not set"
                )

        super().__init__(provider_name, api_key, model)

        if anthropic is None:
            raise ImportError("Anthropic library not installed")

        self.client = anthropic.Anthropic(api_key=api_key)

        logger.info(f"Anthropic provider initialized with model: {model}")

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0
    ) -> LLMResponse:
        """Generate text from a prompt using Anthropic API"""
        try:
            logger.info(f"Generating text with Anthropic model: {self.model}")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                top_p=top_p
            )

            content = response.content[0].text
            tokens_used = response.usage.output_tokens + response.usage.input_tokens

            self.tokens_used += tokens_used
            self.requests_count += 1

            logger.info(f"Text generated successfully. Tokens used: {tokens_used}")

            return LLMResponse(
                content=content,
                model=self.model,
                provider=self.provider_name,
                tokens_used=tokens_used,
                timestamp=datetime.now(),
                confidence=0.95,
                metadata={
                    "stop_reason": response.stop_reason,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            )

        except Exception as e:
            logger.error(f"Error generating text with Anthropic: {str(e)}")
            raise

    async def chat_completion(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """Generate chat completion using Anthropic API"""
        try:
            logger.info(f"Generating chat completion with Anthropic model: {self.model}")

            # Convert LLMMessage objects to Anthropic format
            anthropic_messages = []

            for msg in messages:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": anthropic_messages,
                "temperature": temperature,
                "top_p": top_p
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            response = self.client.messages.create(**kwargs)

            content = response.content[0].text
            tokens_used = response.usage.output_tokens + response.usage.input_tokens

            self.tokens_used += tokens_used
            self.requests_count += 1

            logger.info(f"Chat completion generated successfully. Tokens used: {tokens_used}")

            return LLMResponse(
                content=content,
                model=self.model,
                provider=self.provider_name,
                tokens_used=tokens_used,
                timestamp=datetime.now(),
                confidence=0.95,
                metadata={
                    "stop_reason": response.stop_reason,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            )

        except Exception as e:
            logger.error(f"Error generating chat completion with Anthropic: {str(e)}")
            raise

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embeddings for text
        Note: Anthropic doesn't provide embeddings API, so we return a placeholder
        """
        logger.warning("Anthropic does not provide embeddings API. Returning placeholder.")
        # In production, you might want to use a different embedding service
        return [0.0] * 1536  # Placeholder embedding

    async def list_models(self) -> List[str]:
        """List available Anthropic models"""
        try:
            models = [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
                "claude-2.1",
                "claude-2"
            ]
            logger.info(f"Available Anthropic models: {models}")
            return models

        except Exception as e:
            logger.error(f"Error listing Anthropic models: {str(e)}")
            return []

    async def validate_connection(self) -> bool:
        """Validate Anthropic connection"""
        try:
            logger.info("Validating Anthropic connection")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )

            logger.info("Anthropic connection validated successfully")
            return True

        except Exception as e:
            logger.error(f"Anthropic connection validation failed: {str(e)}")
            return False

    def get_provider_info(self) -> Dict[str, Any]:
        """Get Anthropic provider information"""
        return {
            "provider": self.provider_name,
            "name": "Anthropic",
            "model": self.model,
            "supported_models": [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ],
            "capabilities": [
                "text_generation",
                "chat_completion",
                "vision",
                "long_context"
            ],
            "max_tokens": 200000,
            "supports_streaming": True,
            "supports_vision": True,
            "api_endpoint": "https://api.anthropic.com"
        }
