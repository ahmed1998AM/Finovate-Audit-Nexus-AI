"""
Finovate Audit Nexus AI - Groq Provider
Implementation of LLMInterface for Groq API (Fast LLM Inference)
Enterprise AI Financial Audit & Intelligence Platform
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

try:
    from groq import Groq, AsyncGroq
except ImportError:
    logger.error("Groq library not installed. Install with: pip install groq")
    Groq = None
    AsyncGroq = None

from backend.ai_engine.llm_interface import LLMInterface, LLMResponse, LLMMessage


class GroqProvider(LLMInterface):
    """
    Groq LLM Provider
    Fast LLM inference using Groq's LPU technology
    Supports Llama, Mixtral, and other models
    """

    def __init__(
        self,
        provider_name: str = "groq",
        api_key: Optional[str] = None,
        model: str = "mixtral-8x7b-32768"
    ):
        """
        Initialize Groq provider
        Args:
            provider_name: Provider name (default: "groq")
            api_key: Groq API key (if None, uses GROQ_API_KEY env var)
            model: Model name (default: "mixtral-8x7b-32768")
        """
        if api_key is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError(
                    "Groq API key not provided and GROQ_API_KEY environment variable not set"
                )

        super().__init__(provider_name, api_key, model)

        if Groq is None:
            raise ImportError("Groq library not installed")

        self.client = Groq(api_key=api_key)

        logger.info(f"Groq provider initialized with model: {model}")

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0
    ) -> LLMResponse:
        """Generate text from a prompt using Groq API"""
        try:
            logger.info(f"Generating text with Groq model: {self.model}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            self.tokens_used += tokens_used
            self.requests_count += 1

            logger.info(f"Text generated successfully. Tokens used: {tokens_used}")

            return LLMResponse(
                content=content,
                model=self.model,
                provider=self.provider_name,
                tokens_used=tokens_used,
                timestamp=datetime.now(),
                confidence=0.92,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            )

        except Exception as e:
            logger.error(f"Error generating text with Groq: {str(e)}")
            raise

    async def chat_completion(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """Generate chat completion using Groq API"""
        try:
            logger.info(f"Generating chat completion with Groq model: {self.model}")

            # Convert LLMMessage objects to Groq format
            groq_messages = []

            if system_prompt:
                groq_messages.append({"role": "system", "content": system_prompt})

            for msg in messages:
                groq_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            response = self.client.chat.completions.create(
                model=self.model,
                messages=groq_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            self.tokens_used += tokens_used
            self.requests_count += 1

            logger.info(f"Chat completion generated successfully. Tokens used: {tokens_used}")

            return LLMResponse(
                content=content,
                model=self.model,
                provider=self.provider_name,
                tokens_used=tokens_used,
                timestamp=datetime.now(),
                confidence=0.92,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            )

        except Exception as e:
            logger.error(f"Error generating chat completion with Groq: {str(e)}")
            raise

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embeddings for text
        Note: Groq doesn't provide embeddings API yet
        """
        logger.warning("Groq does not provide embeddings API. Returning placeholder.")
        return [0.0] * 1536  # Placeholder embedding

    async def list_models(self) -> List[str]:
        """List available Groq models"""
        try:
            models = [
                "mixtral-8x7b-32768",
                "llama2-70b-4096",
                "gemma-7b-it"
            ]
            logger.info(f"Available Groq models: {models}")
            return models

        except Exception as e:
            logger.error(f"Error listing Groq models: {str(e)}")
            return []

    async def validate_connection(self) -> bool:
        """Validate Groq connection"""
        try:
            logger.info("Validating Groq connection")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )

            logger.info("Groq connection validated successfully")
            return True

        except Exception as e:
            logger.error(f"Groq connection validation failed: {str(e)}")
            return False

    def get_provider_info(self) -> Dict[str, Any]:
        """Get Groq provider information"""
        return {
            "provider": self.provider_name,
            "name": "Groq",
            "model": self.model,
            "supported_models": [
                "mixtral-8x7b-32768",
                "llama2-70b-4096",
                "gemma-7b-it"
            ],
            "capabilities": [
                "text_generation",
                "chat_completion",
                "fast_inference"
            ],
            "max_tokens": 32768,
            "supports_streaming": True,
            "supports_vision": False,
            "api_endpoint": "https://api.groq.com",
            "special_feature": "Ultra-fast LLM inference using LPU technology"
        }
