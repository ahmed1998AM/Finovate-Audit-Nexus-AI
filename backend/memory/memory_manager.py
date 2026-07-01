"""
Finovate Audit Nexus AI - Memory Management Module

Handles short-term and long-term memory for AI agents,
including context management, conversation history, and knowledge storage.
"""

import json
import os
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger


class MemoryManager:
    """
    Memory Manager for AI Agents

    Responsibilities:
    - Short-term memory (conversation context)
    - Long-term memory (persistent storage)
    - Context window management
    - Memory retrieval & search
    - Vector storage integration
    """

    def __init__(self, agent_id: str = "default"):
        self.agent_id = agent_id
        self.memory_id = f"memory_{agent_id}"

        # Short-term memory (conversation history)
        self.short_term_memory = deque(maxlen=50)  # Last 50 messages

        # Long-term memory (persistent)
        self.long_term_memory = []
        self.memory_file = f"database/memory_{agent_id}.json"

        # Context management
        self.context_window_size = 4096  # tokens
        self.current_context_size = 0

        # Working memory (current session)
        self.working_memory = {}

        # Load existing memory
        self._load_memory()

        logger.info(f"Memory Manager initialized: {self.memory_id}")

    def add_to_short_term(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add message to short-term memory"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.short_term_memory.append(message)
        logger.debug(f"Added to short-term memory: {role}")

    def get_short_term(self, limit: int = 10) -> List[Dict]:
        """Get recent messages from short-term memory"""
        messages = list(self.short_term_memory)[-limit:]
        return messages

    def add_to_long_term(self, key: str, value: Any, category: str = "general"):
        """Add information to long-term memory"""
        memory_entry = {
            "key": key,
            "value": value,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "accessed_count": 0
        }
        self.long_term_memory.append(memory_entry)
        self._save_memory()
        logger.info(f"Added to long-term memory: {key} ({category})")

    def search_long_term(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """Search long-term memory"""
        results = []
        query_lower = query.lower()

        for entry in self.long_term_memory:
            if category and entry["category"] != category:
                continue

            # Search in key and value
            key_match = query_lower in str(entry["key"]).lower()
            value_match = query_lower in str(entry["value"]).lower()

            if key_match or value_match:
                entry["accessed_count"] += 1
                results.append(entry)

        # Sort by relevance (access count)
        results.sort(key=lambda x: x["accessed_count"], reverse=True)

        logger.info(f"Long-term memory search: '{query}' found {len(results)} results")
        return results

    def set_working_memory(self, key: str, value: Any):
        """Set value in working memory"""
        self.working_memory[key] = value
        logger.debug(f"Set working memory: {key}")

    def get_working_memory(self, key: str, default: Any = None) -> Any:
        """Get value from working memory"""
        return self.working_memory.get(key, default)

    def clear_working_memory(self):
        """Clear working memory"""
        self.working_memory.clear()
        logger.info("Working memory cleared")

    def get_context(self, max_tokens: Optional[int] = None) -> List[Dict]:
        """Get current context for AI model"""
        messages = list(self.short_term_memory)

        # Simple token estimation (1 token ≈ 4 characters)
        max_tokens = max_tokens or self.context_window_size
        estimated_tokens = sum(len(str(msg)) // 4 for msg in messages)

        # Trim if exceeds context window
        while estimated_tokens > max_tokens and len(messages) > 1:
            messages.pop(0)
            estimated_tokens = sum(len(str(msg)) // 4 for msg in messages)

        self.current_context_size = estimated_tokens
        return messages

    def _save_memory(self):
        """Save long-term memory to file"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.long_term_memory, f, indent=2, ensure_ascii=False)
            logger.debug(f"Memory saved to {self.memory_file}")
        except Exception as e:
            logger.error(f"Error saving memory: {str(e)}")

    def _load_memory(self):
        """Load long-term memory from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.long_term_memory = json.load(f)
                logger.info(f"Loaded {len(self.long_term_memory)} memory entries")
        except Exception as e:
            logger.error(f"Error loading memory: {str(e)}")
            self.long_term_memory = []

    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "agent_id": self.agent_id,
            "short_term_count": len(self.short_term_memory),
            "long_term_count": len(self.long_term_memory),
            "working_memory_keys": list(self.working_memory.keys()),
            "context_window_size": self.context_window_size,
            "current_context_size": self.current_context_size,
            "memory_file": self.memory_file
        }

    def clear_all(self):
        """Clear all memory"""
        self.short_term_memory.clear()
        self.long_term_memory.clear()
        self.working_memory.clear()
        self._save_memory()
        logger.warning("All memory cleared")


# Singleton instance per agent
_memory_managers = {}


def get_memory_manager(agent_id: str = "default") -> MemoryManager:
    """Get or create Memory Manager for an agent"""
    global _memory_managers
    if agent_id not in _memory_managers:
        _memory_managers[agent_id] = MemoryManager(agent_id)
    return _memory_managers[agent_id]
