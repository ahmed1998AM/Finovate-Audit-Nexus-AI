"""
Finovate Audit Nexus AI - Google Gemini Provider
Implementation of LLMInterface for Google Gemini API
Enterprise AI Financial Audit & Intelligence Platform
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

try:
    from google import genai
except ImportError:
    logger.error("Google GenAI library not installed. Install with: pip install google-genai")
    genai = None

from backend.ai_engine.llm_interface import LLMInterface, LLMMessage, LLMResponse


class GeminiProvider(LLMInterface):
    """
    Google Gemini LLM Provider
    Supports Gemini Pro and Gemini Pro Vision models
    """

    def __init__(
        self,
        provider_name: str = "gemini",
        api_key: Optional[str] = None,
        model: str = "gemini-pro"
    ):
        """
        Initialize Google Gemini provider
        Args:
            provider_name: Provider name (default: "gemini")
            api_key: Google API key (if None, uses GOOGLE_API_KEY env var)
            model: Model name (default: "gemini-pro")
        """
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError(
                    "Google API key not provided and GOOGLE_API_KEY environment variable not set"
                )

        super().__init__(provider_name, api_key, model)

        if genai is None:
            raise ImportError("Google GenAI library not installed")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model

        logger.info(f"Google Gemini provider initialized with model: {model}")

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0
    ) -> LLMResponse:
        """Generate text from a prompt using Google Gemini API"""
        try:
            logger.info(f"Generating text with Google Gemini model: {self.model_name}")

            config = genai.types.GenerateContentConfig(
                temperature=temperature,
                top_p=top_p,
                max_output_tokens=max_tokens,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            content = response.text
            tokens_used = len(content.split()) * 1.3

            self.tokens_used += int(tokens_used)
            self.requests_count += 1

            logger.info(f"Text generated successfully. Estimated tokens: {int(tokens_used)}")

            return LLMResponse(
                content=content,
                model=self.model_name,
                provider=self.provider_name,
                tokens_used=int(tokens_used),
                timestamp=datetime.now(),
                confidence=0.9,
                metadata={
                    "finish_reason": getattr(response, "finish_reason", "STOP")
                }
            )

        except Exception as e:
            logger.error(f"Error generating text with Google Gemini: {str(e)}")
            raise

    async def chat_completion(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """Generate chat completion using Google Gemini API"""
        try:
            logger.info(f"Generating chat completion with Google Gemini model: {self.model_name}")

            config = genai.types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )

            chat_messages = []

            for msg in messages:
                chat_messages.append({
                    "role": "user" if msg.role == "user" else "model",
                    "parts": [msg.content]
                })

            chat = self.client.chats.create(
                model=self.model_name,
                history=chat_messages[:-1],
                config=config
            )
            response = chat.send_message(chat_messages[-1]["parts"][0])

            content = response.text
            tokens_used = len(content.split()) * 1.3

            self.tokens_used += int(tokens_used)
            self.requests_count += 1

            logger.info(f"Chat completion generated successfully. Estimated tokens: {int(tokens_used)}")

            return LLMResponse(
                content=content,
                model=self.model_name,
                provider=self.provider_name,
                tokens_used=int(tokens_used),
                timestamp=datetime.now(),
                confidence=0.9,
                metadata={
                    "finish_reason": getattr(response, "finish_reason", "STOP")
                }
            )

        except Exception as e:
            logger.error(f"Error generating chat completion with Google Gemini: {str(e)}")
            raise

    async def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text using Google Gemini API"""
        try:
            logger.info("Generating embeddings with Google Gemini")

            result = self.client.models.embed_content(
                model="models/embedding-001",
                contents=text
            )

            embedding = result.embeddings[0].values
            self.tokens_used += 1
            self.requests_count += 1

            logger.info(f"Embeddings generated successfully. Embedding dimension: {len(embedding)}")

            return embedding

        except Exception as e:
            logger.error(f"Error generating embeddings with Google Gemini: {str(e)}")
            raise

    async def list_models(self) -> List[str]:
        """List available Google Gemini models"""
        try:
            models = [
                "gemini-pro",
                "gemini-pro-vision",
                "gemini-1.5-pro",
                "gemini-1.5-flash"
            ]
            logger.info(f"Available Google Gemini models: {models}")
            return models

        except Exception as e:
            logger.error(f"Error listing Google Gemini models: {str(e)}")
            return []

    async def validate_connection(self) -> bool:
        """Validate Google Gemini connection"""
        try:
            logger.info("Validating Google Gemini connection")

            self.client.models.generate_content(
                model=self.model_name,
                contents="Hello",
                config=genai.types.GenerateContentConfig(max_output_tokens=10)
            )

            logger.info("Google Gemini connection validated successfully")
            return True

        except Exception as e:
            logger.error(f"Google Gemini connection validation failed: {str(e)}")
            return False

    def get_provider_info(self) -> Dict[str, Any]:
        """Get Google Gemini provider information"""
        return {
            "provider": self.provider_name,
            "name": "Google Gemini",
            "model": self.model_name,
            "supported_models": [
                "gemini-pro",
                "gemini-pro-vision",
                "gemini-1.5-pro",
                "gemini-1.5-flash"
            ],
            "capabilities": [
                "text_generation",
                "chat_completion",
                "vision",
                "embeddings"
            ],
            "max_tokens": 32000,
            "supports_streaming": True,
            "supports_vision": True,
            "api_endpoint": "https://generativelanguage.googleapis.com"
        }
