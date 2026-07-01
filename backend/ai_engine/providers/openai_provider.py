"""
Finovate Audit Nexus AI - OpenAI Provider
Implementation of LLMInterface for OpenAI API
Enterprise AI Financial Audit & Intelligence Platform
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

try:
    from openai import AsyncOpenAI, OpenAI
except ImportError:
    logger.error("OpenAI library not installed. Install with: pip install openai")
    AsyncOpenAI = None
    OpenAI = None

from backend.ai_engine.llm_interface import LLMInterface, LLMMessage, LLMResponse


class OpenAIProvider(LLMInterface):
    """
    OpenAI LLM Provider
    Supports GPT-4, GPT-3.5-turbo, and other OpenAI models
    """

    def __init__(
        self,
        provider_name: str = "openai",
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        organization: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize OpenAI provider
        Args:
            provider_name: Provider name (default: "openai")
            api_key: OpenAI API key (if None, uses OPENAI_API_KEY env var)
            model: Model name (default: "gpt-4")
            organization: OpenAI organization ID (optional)
            base_url: Custom base URL for OpenAI-compatible APIs
        """
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OpenAI API key not provided and OPENAI_API_KEY environment variable not set"
                )

        super().__init__(provider_name, api_key, model)

        if AsyncOpenAI is None:
            raise ImportError("OpenAI library not installed")

        # Initialize async client
        client_kwargs = {
            "api_key": api_key,
        }
        if organization:
            client_kwargs["organization"] = organization
        if base_url:
            client_kwargs["base_url"] = base_url

        self.client = AsyncOpenAI(**client_kwargs)
        self.sync_client = OpenAI(**client_kwargs)

        logger.info(f"OpenAI provider initialized with model: {model}")

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0
    ) -> LLMResponse:
        """Generate text from a prompt using OpenAI API"""
        try:
            logger.info(f"Generating text with OpenAI model: {self.model}")

            response = await self.client.chat.completions.create(
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
                confidence=0.95,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            )

        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {str(e)}")
            raise

    async def chat_completion(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """Generate chat completion using OpenAI API"""
        try:
            logger.info(f"Generating chat completion with OpenAI model: {self.model}")

            # Convert LLMMessage objects to OpenAI format
            openai_messages = []

            if system_prompt:
                openai_messages.append({"role": "system", "content": system_prompt})

            for msg in messages:
                openai_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
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
                confidence=0.95,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            )

        except Exception as e:
            logger.error(f"Error generating chat completion with OpenAI: {str(e)}")
            raise

    async def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text using OpenAI API"""
        try:
            logger.info("Generating embeddings with OpenAI")

            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )

            embedding = response.data[0].embedding
            self.tokens_used += response.usage.total_tokens
            self.requests_count += 1

            logger.info(f"Embeddings generated successfully. Embedding dimension: {len(embedding)}")

            return embedding

        except Exception as e:
            logger.error(f"Error generating embeddings with OpenAI: {str(e)}")
            raise

    async def list_models(self) -> List[str]:
        """List available OpenAI models"""
        try:
            # Return commonly used OpenAI models
            # In production, you might want to fetch this from the API
            models = [
                "gpt-4",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
                "text-davinci-003",
                "text-davinci-002"
            ]
            logger.info(f"Available OpenAI models: {models}")
            return models

        except Exception as e:
            logger.error(f"Error listing OpenAI models: {str(e)}")
            return []

    async def validate_connection(self) -> bool:
        """Validate OpenAI connection"""
        try:
            logger.info("Validating OpenAI connection")

            _response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )

            logger.info("OpenAI connection validated successfully")
            return True

        except Exception as e:
            logger.error(f"OpenAI connection validation failed: {str(e)}")
            return False

    def get_provider_info(self) -> Dict[str, Any]:
        """Get OpenAI provider information"""
        return {
            "provider": self.provider_name,
            "name": "OpenAI",
            "model": self.model,
            "supported_models": [
                "gpt-4",
                "gpt-4-turbo",
                "gpt-3.5-turbo"
            ],
            "capabilities": [
                "text_generation",
                "chat_completion",
                "embeddings",
                "function_calling"
            ],
            "max_tokens": 4096,
            "supports_streaming": True,
            "supports_vision": True,
            "api_endpoint": "https://api.openai.com/v1"
        }
