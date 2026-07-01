"""
Finovate Audit Nexus AI - Ollama Provider
Implementation of LLMInterface for Ollama (Local LLM Models)
Enterprise AI Financial Audit & Intelligence Platform
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

try:
    import requests
except ImportError:
    logger.error("Requests library not installed. Install with: pip install requests")
    requests = None

from backend.ai_engine.llm_interface import LLMInterface, LLMMessage, LLMResponse


class OllamaProvider(LLMInterface):
    """
    Ollama LLM Provider
    For running local LLM models using Ollama
    Supports Llama, Mistral, Orca, and other models
    """

    def __init__(
        self,
        provider_name: str = "ollama",
        api_key: str = "local",  # Not used for local models
        model: str = "llama2",
        base_url: str = "http://localhost:11434"
    ):
        """
        Initialize Ollama provider
        Args:
            provider_name: Provider name (default: "ollama")
            api_key: Not used for local models (default: "local")
            model: Model name (default: "llama2")
            base_url: Ollama server URL (default: "http://localhost:11434")
        """
        super().__init__(provider_name, api_key, model)

        if requests is None:
            raise ImportError("Requests library not installed")

        self.base_url = base_url.rstrip("/")
        self.api_endpoint = f"{self.base_url}/api"

        logger.info(f"Ollama provider initialized with model: {model}, base_url: {base_url}")

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0
    ) -> LLMResponse:
        """Generate text from a prompt using Ollama"""
        try:
            logger.info(f"Generating text with Ollama model: {self.model}")

            response = requests.post(
                f"{self.api_endpoint}/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": top_p,
                    "stream": False
                },
                timeout=300
            )

            response.raise_for_status()
            data = response.json()

            content = data.get("response", "")
            # Estimate tokens
            tokens_used = len(content.split()) * 1.3

            self.tokens_used += int(tokens_used)
            self.requests_count += 1

            logger.info(f"Text generated successfully. Estimated tokens: {int(tokens_used)}")

            return LLMResponse(
                content=content,
                model=self.model,
                provider=self.provider_name,
                tokens_used=int(tokens_used),
                timestamp=datetime.now(),
                confidence=0.85,
                metadata={
                    "eval_count": data.get("eval_count", 0),
                    "eval_duration": data.get("eval_duration", 0)
                }
            )

        except Exception as e:
            logger.error(f"Error generating text with Ollama: {str(e)}")
            raise

    async def chat_completion(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """Generate chat completion using Ollama"""
        try:
            logger.info(f"Generating chat completion with Ollama model: {self.model}")

            # Convert LLMMessage objects to Ollama format
            ollama_messages = []

            if system_prompt:
                ollama_messages.append({"role": "system", "content": system_prompt})

            for msg in messages:
                ollama_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            response = requests.post(
                f"{self.api_endpoint}/chat",
                json={
                    "model": self.model,
                    "messages": ollama_messages,
                    "temperature": temperature,
                    "stream": False
                },
                timeout=300
            )

            response.raise_for_status()
            data = response.json()

            content = data["message"]["content"]
            tokens_used = len(content.split()) * 1.3

            self.tokens_used += int(tokens_used)
            self.requests_count += 1

            logger.info(f"Chat completion generated successfully. Estimated tokens: {int(tokens_used)}")

            return LLMResponse(
                content=content,
                model=self.model,
                provider=self.provider_name,
                tokens_used=int(tokens_used),
                timestamp=datetime.now(),
                confidence=0.85,
                metadata={
                    "eval_count": data.get("eval_count", 0),
                    "eval_duration": data.get("eval_duration", 0)
                }
            )

        except Exception as e:
            logger.error(f"Error generating chat completion with Ollama: {str(e)}")
            raise

    async def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text using Ollama"""
        try:
            logger.info("Generating embeddings with Ollama")

            response = requests.post(
                f"{self.api_endpoint}/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                },
                timeout=300
            )

            response.raise_for_status()
            data = response.json()

            embedding = data.get("embedding", [])
            self.tokens_used += 1
            self.requests_count += 1

            logger.info(f"Embeddings generated successfully. Embedding dimension: {len(embedding)}")

            return embedding

        except Exception as e:
            logger.error(f"Error generating embeddings with Ollama: {str(e)}")
            raise

    async def list_models(self) -> List[str]:
        """List available Ollama models"""
        try:
            response = requests.get(
                f"{self.api_endpoint}/tags",
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            models = [model["name"] for model in data.get("models", [])]
            logger.info(f"Available Ollama models: {models}")
            return models

        except Exception as e:
            logger.error(f"Error listing Ollama models: {str(e)}")
            return ["llama2", "mistral", "orca"]  # Return common models as fallback

    async def validate_connection(self) -> bool:
        """Validate Ollama connection"""
        try:
            logger.info("Validating Ollama connection")

            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )

            logger.info("Ollama connection validated successfully")
            return response.status_code == 200

        except Exception as e:
            logger.error(f"Ollama connection validation failed: {str(e)}")
            return False

    def get_provider_info(self) -> Dict[str, Any]:
        """Get Ollama provider information"""
        return {
            "provider": self.provider_name,
            "name": "Ollama",
            "model": self.model,
            "supported_models": [
                "llama2",
                "mistral",
                "orca",
                "neural-chat",
                "starling-lm"
            ],
            "capabilities": [
                "text_generation",
                "chat_completion",
                "embeddings",
                "local_execution"
            ],
            "max_tokens": 4096,
            "supports_streaming": True,
            "supports_vision": False,
            "api_endpoint": self.base_url,
            "special_feature": "Run LLMs locally without internet connection"
        }
