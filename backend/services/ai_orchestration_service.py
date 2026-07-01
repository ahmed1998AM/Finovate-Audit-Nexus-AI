"""
AI Orchestration Service - خدمة تنسيق وإدارة الوكلاء الذكية
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AIOrchestrationService:
    """
    خدمة تنسيق وإدارة الوكلاء الذكية

    المسؤولة عن:
    - إدارة دورة حياة الوكلاء
    - تنسيق العمل بين الوكلاء
    - إدارة مهام الذكاء الاصطناعي
    - تتبع تقدم المهام
    - جمع النتائج وتوحيدها
    """

    def __init__(self):
        """تهيئة خدمة التنسيق"""
        self.active_agents = {}
        self.task_queue = []
        self.completed_tasks = {}
        self.agent_registry = {}
        logger.info("AIOrchestrationService initialized")

    def register_agent(self, agent_id: str, agent_type: str, capabilities: List[str]) -> bool:
        """
        تسجيل وكيل في النظام

        Args:
            agent_id: معرف الوكيل
            agent_type: نوع الوكيل
            capabilities: قدرات الوكيل

        Returns:
            True إذا نجح التسجيل
        """
        self.agent_registry[agent_id] = {
            'agent_id': agent_id,
            'agent_type': agent_type,
            'capabilities': capabilities,
            'status': 'available',
            'current_task': None,
            'tasks_completed': 0,
            'registered_at': datetime.now()
        }

        logger.info(f"Registered agent: {agent_id} ({agent_type})")
        return True

    def assign_task(
        self,
        task_id: str,
        agent_id: str,
        task_type: str,
        task_data: Dict[str, Any],
        priority: int = 5
    ) -> Dict[str, Any]:
        """
        تعيين مهمة لوكيل

        Args:
            task_id: معرف المهمة
            agent_id: معرف الوكيل
            task_type: نوع المهمة
            task_data: بيانات المهمة
            priority: الأولوية (1-10)

        Returns:
            معلومات المهمة
        """
        if agent_id not in self.agent_registry:
            logger.error(f"Agent {agent_id} not found")
            return {'success': False, 'error': 'Agent not found'}

        task = {
            'task_id': task_id,
            'agent_id': agent_id,
            'task_type': task_type,
            'task_data': task_data,
            'priority': priority,
            'status': 'pending',
            'created_at': datetime.now(),
            'started_at': None,
            'completed_at': None,
            'result': None
        }

        self.task_queue.append(task)
        self.agent_registry[agent_id]['current_task'] = task_id
        self.agent_registry[agent_id]['status'] = 'busy'

        logger.info(f"Assigned task {task_id} to agent {agent_id}")
        return task

    def start_task(self, task_id: str) -> bool:
        """
        بدء تنفيذ مهمة

        Args:
            task_id: معرف المهمة

        Returns:
            True إذا نجح البدء
        """
        task = next((t for t in self.task_queue if t['task_id'] == task_id), None)

        if not task:
            logger.error(f"Task {task_id} not found")
            return False

        task['status'] = 'running'
        task['started_at'] = datetime.now()

        logger.info(f"Started task: {task_id}")
        return True

    def complete_task(self, task_id: str, result: Dict[str, Any]) -> bool:
        """
        إكمال مهمة

        Args:
            task_id: معرف المهمة
            result: نتيجة المهمة

        Returns:
            True إذا نجح الإكمال
        """
        task = next((t for t in self.task_queue if t['task_id'] == task_id), None)

        if not task:
            logger.error(f"Task {task_id} not found")
            return False

        task['status'] = 'completed'
        task['completed_at'] = datetime.now()
        task['result'] = result

        # تحديث حالة الوكيل
        agent_id = task['agent_id']
        if agent_id in self.agent_registry:
            self.agent_registry[agent_id]['status'] = 'available'
            self.agent_registry[agent_id]['current_task'] = None
            self.agent_registry[agent_id]['tasks_completed'] += 1

        self.completed_tasks[task_id] = task

        logger.info(f"Completed task: {task_id}")
        return True

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        الحصول على حالة مهمة

        Args:
            task_id: معرف المهمة

        Returns:
            حالة المهمة
        """
        # البحث في قائمة الانتظار
        task = next((t for t in self.task_queue if t['task_id'] == task_id), None)

        if not task:
            # البحث في المكتملة
            task = self.completed_tasks.get(task_id)

        if not task:
            return {'exists': False}

        return {
            'exists': True,
            'task_id': task['task_id'],
            'agent_id': task['agent_id'],
            'task_type': task['task_type'],
            'status': task['status'],
            'priority': task['priority'],
            'created_at': task['created_at'],
            'started_at': task['started_at'],
            'completed_at': task['completed_at'],
            'result': task.get('result')
        }

    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """
        الحصول على حالة وكيل

        Args:
            agent_id: معرف الوكيل

        Returns:
            حالة الوكيل
        """
        if agent_id not in self.agent_registry:
            return {'exists': False}

        agent = self.agent_registry[agent_id]

        return {
            'exists': True,
            'agent_id': agent['agent_id'],
            'agent_type': agent['agent_type'],
            'status': agent['status'],
            'current_task': agent['current_task'],
            'tasks_completed': agent['tasks_completed'],
            'capabilities': agent['capabilities']
        }

    def list_agents(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        قائمة الوكلاء

        Args:
            status: تصفية حسب الحالة (اختياري)

        Returns:
            قائمة الوكلاء
        """
        agents = list(self.agent_registry.values())

        if status is not None:
            agents = [a for a in agents if a['status'] == status]

        return agents

    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """
        الحصول على المهام المعلقة

        Returns:
            قائمة المهام المعلقة
        """
        return [t for t in self.task_queue if t['status'] == 'pending']

    def get_running_tasks(self) -> List[Dict[str, Any]]:
        """
        الحصول على المهام الجارية

        Returns:
            قائمة المهام الجارية
        """
        return [t for t in self.task_queue if t['status'] == 'running']

    def cancel_task(self, task_id: str) -> bool:
        """
        إلغاء مهمة

        Args:
            task_id: معرف المهمة

        Returns:
            True إذا نجح الإلغاء
        """
        task = next((t for t in self.task_queue if t['task_id'] == task_id), None)

        if not task:
            logger.error(f"Task {task_id} not found")
            return False

        task['status'] = 'cancelled'

        # تحرير الوكيل
        agent_id = task['agent_id']
        if agent_id in self.agent_registry:
            self.agent_registry[agent_id]['status'] = 'available'
            self.agent_registry[agent_id]['current_task'] = None

        logger.info(f"Cancelled task: {task_id}")
        return True

    def orchestrate_multi_agent_workflow(
        self,
        workflow_id: str,
        workflow_steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        تنسيق سير عمل متعدد الوكلاء

        Args:
            workflow_id: معرف سير العمل
            workflow_steps: خطوات سير العمل

        Returns:
            نتيجة سير العمل
        """
        logger.info(f"Starting multi-agent workflow: {workflow_id}")

        workflow_result = {
            'workflow_id': workflow_id,
            'status': 'running',
            'started_at': datetime.now(),
            'steps': [],
            'final_result': None
        }

        for step in workflow_steps:
            step_id = step.get('step_id', f"STEP-{len(workflow_result['steps']) + 1}")
            agent_id = step.get('agent_id')
            task_data = step.get('task_data', {})

            # إنشاء مهمة للخطوة
            task_id = f"{workflow_id}-{step_id}"
            self.assign_task(task_id, agent_id, step.get('type', 'generic'), task_data)

            # محاكاة التنفيذ
            self.start_task(task_id)

            step_result = {
                'step_id': step_id,
                'task_id': task_id,
                'agent_id': agent_id,
                'status': 'completed',
                'result': {'data': f"Result from {agent_id}"}
            }

            self.complete_task(task_id, step_result['result'])
            workflow_result['steps'].append(step_result)

        workflow_result['status'] = 'completed'
        workflow_result['completed_at'] = datetime.now()
        workflow_result['final_result'] = {
            'total_steps': len(workflow_steps),
            'successful_steps': len([s for s in workflow_result['steps'] if s['status'] == 'completed'])
        }

        logger.info(f"Completed workflow: {workflow_id}")
        return workflow_result
