"""
Finovate Audit Nexus AI - Agent Registry Module
تسجيل تلقائي لجميع الوكلاء الذكية في النظام
"""

import os
import importlib
from typing import Dict, Any, List
from loguru import logger


class AgentRegistry:
    """
    سجل الوكلاء الذكية
    يقوم بتحميل وتسجيل جميع الوكلاء المتاحة في النظام تلقائياً
    """
    
    def __init__(self):
        # Use absolute path from project root
        self.agents_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'agents')
        self.registered_agents = {}
        logger.info(f"Agent Registry initialized - Path: {self.agents_path}")
    
    def discover_agents(self) -> List[str]:
        """
        اكتشاف جميع الوكلاء المتاحة في مجلد agents
        
        Returns:
            List[str]: قائمة بأسماء الوكلاء المكتشفة
        """
        agent_names = []
        
        if not os.path.exists(self.agents_path):
            logger.warning(f"Agents directory not found: {self.agents_path}")
            return agent_names
        
        # البحث عن جميع مجلدات الوكلاء
        for item in os.listdir(self.agents_path):
            item_path = os.path.join(self.agents_path, item)
            
            # تجاهل الملفات والمجلدات الخاصة
            if item.startswith('__') or not os.path.isdir(item_path):
                continue
            
            # التحقق من وجود ملف agent.py
            agent_file = os.path.join(item_path, 'agent.py')
            if os.path.exists(agent_file):
                agent_names.append(item)
                logger.info(f"Discovered agent: {item}")
        
        return agent_names
    
    def load_agent(self, agent_name: str) -> Any:
        """
        تحميل وكيل محدد ديناميكياً
        
        Args:
            agent_name: اسم الوكيل (اسم المجلد)
            
        Returns:
            Any: نسخة من فئة الوكيل أو None إذا فشل التحميل
        """
        try:
            # استيراد الوحدة ديناميكياً
            module_path = f"agents.{agent_name}.agent"
            module = importlib.import_module(module_path)
            
            # البحث عن الفئة الرئيسية في الوحدة
            agent_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and 'Agent' in attr_name:
                    agent_class = attr
                    break
            
            if agent_class is None:
                logger.warning(f"No agent class found in {module_path}")
                return None
            
            # إنشاء نسخة من الوكيل
            agent_instance = agent_class()
            logger.info(f"Successfully loaded agent: {agent_name} ({agent_class.__name__})")
            return agent_instance
            
        except Exception as e:
            logger.error(f"Failed to load agent {agent_name}: {str(e)}")
            return None
    
    def register_all_agents(self) -> Dict[str, Any]:
        """
        تسجيل جميع الوكلاء المكتشفة
        
        Returns:
            Dict[str, Any]: قاموس بالوكلاء المسجلة
        """
        agent_names = self.discover_agents()
        
        for agent_name in agent_names:
            agent_instance = self.load_agent(agent_name)
            if agent_instance is not None:
                self.registered_agents[agent_name] = agent_instance
        
        logger.info(f"Registered {len(self.registered_agents)} agents")
        return self.registered_agents
    
    def get_agent(self, agent_name: str) -> Any:
        """
        الحصول على وكيل محدد بالاسم
        
        Args:
            agent_name: اسم الوكيل
            
        Returns:
            Any: نسخة الوكيل أو None
        """
        return self.registered_agents.get(agent_name)
    
    def get_all_agents(self) -> Dict[str, Any]:
        """
        الحصول على جميع الوكلاء المسجلة
        
        Returns:
            Dict[str, Any]: قاموس بجميع الوكلاء
        """
        return self.registered_agents
    
    def get_agents_count(self) -> int:
        """
        الحصول على عدد الوكلاء المسجلة
        
        Returns:
            int: عدد الوكلاء
        """
        return len(self.registered_agents)


# دالة مساعدة لتسجيل الوكلاء في Orchestrator
def register_agents_in_orchestrator(orchestrator) -> int:
    """
    تسجيل جميع الوكلاء في المنسق
    
    Args:
        orchestrator: نسخة من AgentOrchestrator
        
    Returns:
        int: عدد الوكلاء المسجلة بنجاح
    """
    registry = AgentRegistry()
    agents = registry.register_all_agents()
    
    registered_count = 0
    for agent_name, agent_instance in agents.items():
        if orchestrator.register_agent(agent_name, agent_instance):
            registered_count += 1
    
    logger.info(f"Registered {registered_count} agents in orchestrator")
    return registered_count


# مثال للاستخدام
if __name__ == "__main__":
    registry = AgentRegistry()
    agents = registry.register_all_agents()
    
    print(f"\n{'='*60}")
    print("🤖 Registered Agents")
    print(f"{'='*60}")
    print(f"Total Agents: {len(agents)}")
    print(f"{'='*60}\n")
    
    for agent_name in sorted(agents.keys()):
        print(f"✅ {agent_name}")
    
    print(f"\n{'='*60}")
