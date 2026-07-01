"""
Finovate Audit Nexus AI - Enhanced Agent Base Class
Base class for intelligent agents with LLM integration
Enterprise AI Financial Audit & Intelligence Platform
"""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from loguru import logger

from backend.ai_engine.engine_v2 import get_ai_engine_v2
from backend.ai_engine.llm_interface import LLMMessage


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class AgentResult:
    """Result returned by an agent"""
    success: bool
    data: Any = None
    message: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    ai_insights: Optional[str] = None
    confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
            "ai_insights": self.ai_insights,
            "confidence_score": self.confidence_score,
            "timestamp": datetime.now().isoformat()
        }


class EnhancedAgent(ABC):
    """
    Enhanced base class for all AI agents with LLM integration

    Features:
    - LLM-powered analysis and decision making
    - Tool management and execution
    - Context and memory management
    - Error handling and recovery
    - Comprehensive logging
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        agent_type: str = "generic",
        llm_provider: Optional[str] = None
    ):
        """
        Initialize enhanced agent
        Args:
            name: Agent name
            description: Agent description
            agent_type: Type of agent (audit, fraud, risk, compliance, etc.)
            llm_provider: Preferred LLM provider (optional)
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.agent_type = agent_type
        self.status = AgentStatus.IDLE
        self.created_at = datetime.now()
        self.last_execution: Optional[datetime] = None
        self.execution_count = 0

        # LLM integration
        self.ai_engine = get_ai_engine_v2()
        self.llm_provider = llm_provider
        self.conversation_history: List[LLMMessage] = []

        # Context and memory
        self._context: Dict[str, Any] = {}
        self._memory: Dict[str, Any] = {}
        self._tools: Dict[str, callable] = {}

        logger.info(f"Enhanced agent initialized: {name} ({self.id})")

    @abstractmethod
    async def execute(self, **kwargs) -> AgentResult:
        """Execute the agent's main task"""
        pass

    @abstractmethod
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters"""
        pass

    def set_context(self, key: str, value: Any) -> None:
        """Set a context value"""
        self._context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context value"""
        return self._context.get(key, default)

    def clear_context(self) -> None:
        """Clear all context"""
        self._context = {}

    def set_memory(self, key: str, value: Any) -> None:
        """Set a memory value (persists across executions)"""
        self._memory[key] = value

    def get_memory(self, key: str, default: Any = None) -> Any:
        """Get a memory value"""
        return self._memory.get(key, default)

    def register_tool(self, tool_name: str, tool_func: callable) -> None:
        """
        Register a tool that the agent can use
        Args:
            tool_name: Name of the tool
            tool_func: Callable function that implements the tool
        """
        self._tools[tool_name] = tool_func
        logger.info(f"Tool registered: {tool_name}")

    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Use a registered tool
        Args:
            tool_name: Name of the tool to use
            **kwargs: Arguments to pass to the tool
        Returns:
            Result from the tool
        """
        if tool_name not in self._tools:
            logger.error(f"Tool not found: {tool_name}")
            raise ValueError(f"Tool not found: {tool_name}")

        tool_func = self._tools[tool_name]
        logger.info(f"Using tool: {tool_name}")
        return await tool_func(**kwargs) if hasattr(tool_func, '__await__') else tool_func(**kwargs)

    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return list(self._tools.keys())

    async def analyze_with_ai(
        self,
        prompt: str,
        context_data: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Use LLM to analyze data and generate insights
        Args:
            prompt: Analysis prompt
            context_data: Optional context data to include
            provider: Optional LLM provider to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        Returns:
            AI-generated analysis
        """
        try:
            # Build the full prompt with context
            full_prompt = prompt

            if context_data:
                context_str = "\n".join(
                    f"{k}: {v}" for k, v in context_data.items()
                )
                full_prompt = f"{prompt}\n\nContext:\n{context_str}"

            # Add to conversation history
            user_message = LLMMessage(role="user", content=full_prompt)
            self.conversation_history.append(user_message)

            # Generate response using AI engine
            response = await self.ai_engine.generate_text(
                prompt=full_prompt,
                provider=provider or self.llm_provider,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Add response to conversation history
            assistant_message = LLMMessage(role="assistant", content=response.content)
            self.conversation_history.append(assistant_message)

            logger.info(f"AI analysis completed. Tokens used: {response.tokens_used}")

            return response.content

        except Exception as e:
            logger.error(f"Error during AI analysis: {str(e)}")
            raise

    async def chat_with_ai(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Have a multi-turn conversation with LLM
        Args:
            messages: List of messages in the conversation
            system_prompt: Optional system prompt
            provider: Optional LLM provider to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        Returns:
            LLM response
        """
        try:
            # Combine with conversation history
            all_messages = self.conversation_history + messages

            response = await self.ai_engine.chat_completion(
                messages=all_messages,
                system_prompt=system_prompt,
                provider=provider or self.llm_provider,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Update conversation history
            self.conversation_history = all_messages
            assistant_message = LLMMessage(role="assistant", content=response.content)
            self.conversation_history.append(assistant_message)

            logger.info(f"Chat completed. Tokens used: {response.tokens_used}")

            return response.content

        except Exception as e:
            logger.error(f"Error during chat: {str(e)}")
            raise

    def clear_conversation_history(self) -> None:
        """Clear the conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")

    def before_execute(self, **kwargs) -> None:
        """Hook called before execution"""
        self.status = AgentStatus.RUNNING
        self.last_execution = datetime.now()
        self.execution_count += 1
        logger.info(f"Agent execution started: {self.name}")

    def after_execute(self, result: AgentResult) -> None:
        """Hook called after execution"""
        if result.success:
            self.status = AgentStatus.COMPLETED
        else:
            self.status = AgentStatus.FAILED
        logger.info(f"Agent execution completed: {self.name}, success: {result.success}")

    def get_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "execution_count": self.execution_count,
            "available_tools": self.get_available_tools(),
            "llm_provider": self.llm_provider
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "total_executions": self.execution_count,
            "status": self.status.value,
            "conversation_history_length": len(self.conversation_history),
            "tools_available": len(self._tools),
            "memory_items": len(self._memory)
        }
