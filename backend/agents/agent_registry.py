"""
Finovate Audit Nexus AI - Agent Registry
Enterprise AI Financial Audit & Intelligence Platform
"""

from typing import Dict, List, Optional, Type
from .agent_base import BaseAgent

class AgentRegistry:
    """Central registry for all AI agents"""
    
    _instance = None
    _agents: Dict[str, BaseAgent] = {}
    _agent_classes: Dict[str, Type[BaseAgent]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def register(cls, agent_class: Type[BaseAgent]) -> Type[BaseAgent]:
        """Register an agent class"""
        agent_name = agent_class.__name__
        cls._agent_classes[agent_name] = agent_class
        return agent_class
    
    @classmethod
    def get_agent_class(cls, name: str) -> Optional[Type[BaseAgent]]:
        """Get an agent class by name"""
        return cls._agent_classes.get(name)
    
    @classmethod
    def create_agent(cls, name: str, **kwargs) -> Optional[BaseAgent]:
        """Create an agent instance"""
        agent_class = cls.get_agent_class(name)
        if agent_class:
            agent = agent_class(**kwargs)
            cls._agents[agent.id] = agent
            return agent
        return None
    
    @classmethod
    def get_agent(cls, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent instance by ID"""
        return cls._agents.get(agent_id)
    
    @classmethod
    def get_all_agents(cls) -> List[BaseAgent]:
        """Get all registered agent instances"""
        return list(cls._agents.values())
    
    @classmethod
    def get_agent_info(cls, agent_id: str) -> Optional[Dict]:
        """Get information about an agent"""
        agent = cls.get_agent(agent_id)
        if agent:
            return agent.get_info()
        return None
    
    @classmethod
    def get_all_agents_info(cls) -> List[Dict]:
        """Get information about all agents"""
        return [agent.get_info() for agent in cls._agents.values()]
    
    @classmethod
    def remove_agent(cls, agent_id: str) -> bool:
        """Remove an agent instance"""
        if agent_id in cls._agents:
            del cls._agents[agent_id]
            return True
        return False
    
    @classmethod
    def clear_all(cls) -> None:
        """Clear all agent instances"""
        cls._agents.clear()
    
    @classmethod
    def get_registered_classes(cls) -> List[str]:
        """Get list of registered agent class names"""
        return list(cls._agent_classes.keys())
