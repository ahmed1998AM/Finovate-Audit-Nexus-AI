"""
Finovate Audit Nexus AI - AI Provider API Routes
REST API endpoints for managing LLM providers
Enterprise AI Financial Audit & Intelligence Platform
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from loguru import logger

from backend.ai_engine.engine_v2 import get_ai_engine_v2

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/providers")
async def get_providers() -> Dict[str, Any]:
    """
    Get list of all available AI providers
    
    Returns:
        List of available providers with their information
    """
    try:
        ai_engine = get_ai_engine_v2()
        providers = ai_engine.get_available_providers()

        providers_info = []
        for provider_name in providers:
            provider_info = ai_engine.get_provider_info(provider_name)
            providers_info.append(provider_info)

        logger.info(f"Retrieved {len(providers_info)} AI providers")

        return {
            "success": True,
            "data": {
                "providers": providers_info,
                "total": len(providers_info),
                "active_provider": ai_engine.active_provider,
                "active_model": ai_engine.active_model
            }
        }

    except Exception as e:
        logger.error(f"Error getting providers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/providers/select")
async def select_provider(
    provider_name: str,
    model_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Select an active AI provider
    
    Args:
        provider_name: Name of the provider to activate
        model_name: Optional model name to use
    
    Returns:
        Success status and provider information
    """
    try:
        ai_engine = get_ai_engine_v2()

        if not ai_engine.select_provider(provider_name, model_name):
            raise HTTPException(
                status_code=400,
                detail=f"Failed to select provider: {provider_name}"
            )

        logger.info(f"Selected provider: {provider_name}")

        return {
            "success": True,
            "data": {
                "active_provider": ai_engine.active_provider,
                "active_model": ai_engine.active_model,
                "provider_info": ai_engine.get_provider_info(provider_name)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error selecting provider: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/providers/{provider_name}/test")
async def test_provider(provider_name: str) -> Dict[str, Any]:
    """
    Test connection to an AI provider
    
    Args:
        provider_name: Name of the provider to test
    
    Returns:
        Test result with connection status
    """
    try:
        ai_engine = get_ai_engine_v2()

        if provider_name not in ai_engine.providers:
            raise HTTPException(
                status_code=404,
                detail=f"Provider not found: {provider_name}"
            )

        provider = ai_engine.providers[provider_name]
        is_valid = await provider.validate_connection()

        logger.info(f"Tested provider: {provider_name}, valid: {is_valid}")

        return {
            "success": is_valid,
            "data": {
                "provider": provider_name,
                "valid": is_valid,
                "status": "connected" if is_valid else "disconnected",
                "message": f"Connection to {provider_name} is {'successful' if is_valid else 'failed'}"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing provider: {str(e)}")
        return {
            "success": False,
            "data": {
                "provider": provider_name,
                "valid": False,
                "status": "error",
                "message": str(e)
            }
        }


@router.get("/status")
async def get_ai_engine_status() -> Dict[str, Any]:
    """
    Get the status of the AI engine
    
    Returns:
        Detailed AI engine status and statistics
    """
    try:
        ai_engine = get_ai_engine_v2()
        status = ai_engine.get_status()

        logger.info("Retrieved AI engine status")

        return {
            "success": True,
            "data": status
        }

    except Exception as e:
        logger.error(f"Error getting AI engine status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers/{provider_name}/models")
async def get_provider_models(provider_name: str) -> Dict[str, Any]:
    """
    Get available models for a specific provider
    
    Args:
        provider_name: Name of the provider
    
    Returns:
        List of available models
    """
    try:
        ai_engine = get_ai_engine_v2()

        if provider_name not in ai_engine.providers:
            raise HTTPException(
                status_code=404,
                detail=f"Provider not found: {provider_name}"
            )

        provider = ai_engine.providers[provider_name]
        models = await provider.list_models()

        logger.info(f"Retrieved {len(models)} models for provider: {provider_name}")

        return {
            "success": True,
            "data": {
                "provider": provider_name,
                "models": models,
                "total": len(models)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting provider models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers/{provider_name}/stats")
async def get_provider_stats(provider_name: str) -> Dict[str, Any]:
    """
    Get usage statistics for a specific provider
    
    Args:
        provider_name: Name of the provider
    
    Returns:
        Usage statistics
    """
    try:
        ai_engine = get_ai_engine_v2()

        if provider_name not in ai_engine.providers:
            raise HTTPException(
                status_code=404,
                detail=f"Provider not found: {provider_name}"
            )

        provider = ai_engine.providers[provider_name]
        stats = provider.get_usage_stats()

        logger.info(f"Retrieved stats for provider: {provider_name}")

        return {
            "success": True,
            "data": stats
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting provider stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_ai_stats_summary() -> Dict[str, Any]:
    """
    Get summary statistics for all AI providers
    
    Returns:
        Aggregated statistics across all providers
    """
    try:
        ai_engine = get_ai_engine_v2()

        all_stats = {}
        for provider_name in ai_engine.providers:
            provider = ai_engine.providers[provider_name]
            all_stats[provider_name] = provider.get_usage_stats()

        summary = {
            "total_tokens_used": ai_engine.tokens_used,
            "total_requests": ai_engine.requests_count,
            "providers": all_stats,
            "active_provider": ai_engine.active_provider,
            "active_model": ai_engine.active_model
        }

        logger.info("Retrieved AI stats summary")

        return {
            "success": True,
            "data": summary
        }

    except Exception as e:
        logger.error(f"Error getting AI stats summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stats/reset")
async def reset_ai_stats() -> Dict[str, Any]:
    """
    Reset AI engine statistics
    
    Returns:
        Success status
    """
    try:
        ai_engine = get_ai_engine_v2()
        ai_engine.reset_statistics()

        logger.info("Reset AI engine statistics")

        return {
            "success": True,
            "data": {"message": "Statistics reset successfully"}
        }

    except Exception as e:
        logger.error(f"Error resetting AI stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-text")
async def generate_text(
    prompt: str,
    provider: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> Dict[str, Any]:
    """
    Generate text using the AI engine
    
    Args:
        prompt: Input prompt
        provider: Optional provider name
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
    
    Returns:
        Generated text and metadata
    """
    try:
        ai_engine = get_ai_engine_v2()

        response = await ai_engine.generate_text(
            prompt=prompt,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens
        )

        logger.info(f"Generated text with {response.tokens_used} tokens")

        return {
            "success": True,
            "data": response.to_dict()
        }

    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat-completion")
async def chat_completion(
    messages: List[Dict[str, str]],
    provider: Optional[str] = None,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> Dict[str, Any]:
    """
    Generate chat completion using the AI engine
    
    Args:
        messages: List of messages in the conversation
        provider: Optional provider name
        system_prompt: Optional system prompt
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
    
    Returns:
        Chat completion response
    """
    try:
        from backend.ai_engine.llm_interface import LLMMessage

        ai_engine = get_ai_engine_v2()

        # Convert messages to LLMMessage objects
        llm_messages = [
            LLMMessage(role=msg["role"], content=msg["content"])
            for msg in messages
        ]

        response = await ai_engine.chat_completion(
            messages=llm_messages,
            provider=provider,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )

        logger.info(f"Generated chat completion with {response.tokens_used} tokens")

        return {
            "success": True,
            "data": response.to_dict()
        }

    except Exception as e:
        logger.error(f"Error generating chat completion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
