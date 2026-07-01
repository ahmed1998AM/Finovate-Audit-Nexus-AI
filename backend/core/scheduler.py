"""
Finovate Audit Nexus AI - Continuous Audit Scheduler
نظام جدولة المراجعات الدورية
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ScheduleInterval(Enum):
    """فواصل الجدولة"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


@dataclass
class ScheduledTask:
    """مهمة مجدولة"""
    task_id: str
    name: str
    function: Callable
    interval: ScheduleInterval
    interval_value: Optional[int] = None  # للفواصل المخصصة (بالدقائق)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    enabled: bool = True
    metadata: Optional[Dict] = None


class ContinuousAuditScheduler:
    """مجدول المراجعات المستمرة"""
    
    def __init__(self):
        self._tasks: Dict[str, ScheduledTask] = {}
        self._running = False
        self._check_interval = 60  # تحقق كل 60 ثانية
        self._loop: Optional[asyncio.AbstractEventLoop] = None
    
    def _get_loop(self):
        if self._loop is None or self._loop.is_closed():
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
        return self._loop
    
    def register_task(
        self,
        task_id: str,
        name: str,
        function: Callable,
        interval: ScheduleInterval,
        interval_value: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """تسجيل مهمة مجدولة"""
        if task_id in self._tasks:
            logger.warning(f"Task {task_id} already registered")
            return False
        
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            function=function,
            interval=interval,
            interval_value=interval_value,
            metadata=metadata
        )
        
        # حساب وقت التشغيل القادم
        task.next_run = self._calculate_next_run(task)
        
        self._tasks[task_id] = task
        logger.info(f"Registered scheduled task: {name} ({task_id}) - {interval.value}")
        return True
    
    def _calculate_next_run(self, task: ScheduledTask) -> datetime:
        """حساب وقت التشغيل القادم"""
        now = datetime.now()
        
        if task.interval == ScheduleInterval.HOURLY:
            return now + timedelta(hours=1)
        elif task.interval == ScheduleInterval.DAILY:
            return now + timedelta(days=1)
        elif task.interval == ScheduleInterval.WEEKLY:
            return now + timedelta(weeks=1)
        elif task.interval == ScheduleInterval.MONTHLY:
            return now + timedelta(days=30)
        elif task.interval == ScheduleInterval.CUSTOM and task.interval_value:
            return now + timedelta(minutes=task.interval_value)
        else:
            return now + timedelta(hours=1)  # افتراضي
    
    def unregister_task(self, task_id: str) -> bool:
        """إلغاء تسجيل مهمة"""
        if task_id in self._tasks:
            del self._tasks[task_id]
            logger.info(f"Unregistered task: {task_id}")
            return True
        return False
    
    def enable_task(self, task_id: str) -> bool:
        """تفعيل مهمة"""
        if task_id in self._tasks:
            self._tasks[task_id].enabled = True
            return True
        return False
    
    def disable_task(self, task_id: str) -> bool:
        """تعطيل مهمة"""
        if task_id in self._tasks:
            self._tasks[task_id].enabled = False
            return True
        return False
    
    async def _execute_task(self, task: ScheduledTask):
        """تنفيذ مهمة مجدولة"""
        logger.info(f"Executing scheduled task: {task.name} ({task.task_id})")
        
        try:
            # إذا كانت الدالة async
            if asyncio.iscoroutinefunction(task.function):
                result = await task.function()
            else:
                result = task.function()
            
            task.last_run = datetime.now()
            task.next_run = self._calculate_next_run(task)
            
            logger.info(f"Task completed: {task.name} - Next run: {task.next_run}")
            
            # حفظ النتيجة في قاعدة البيانات إذا لزم الأمر
            if task.metadata and task.metadata.get("save_result"):
                await self._save_task_result(task, result)
                
        except Exception as e:
            logger.error(f"Task failed: {task.name} - {str(e)}")
            # إعادة جدولة المهمة حتى لو فشلت
            task.next_run = self._calculate_next_run(task)
    
    async def _save_task_result(self, task: ScheduledTask, result):
        """حفظ نتيجة المهمة في قاعدة البيانات"""
        try:
            from backend.database import get_db_session
            from backend.database.models import AuditLog
            
            with get_db_session() as session:
                log = AuditLog(
                    action="scheduled_audit",
                    resource_type="ScheduledTask",
                    resource_id=task.task_id,
                    new_value={"result": str(result), "task_name": task.name},
                    timestamp=datetime.now()
                )
                session.add(log)
                session.commit()
        except Exception as e:
            logger.error(f"Failed to save task result: {e}")
    
    async def _check_and_run_tasks(self):
        """التحقق من المهام وتنفيذها"""
        now = datetime.now()
        
        for task in self._tasks.values():
            if not task.enabled:
                continue
            
            if task.next_run and now >= task.next_run:
                asyncio.create_task(self._execute_task(task))
    
    async def start(self):
        """بدء المجدول"""
        if self._running:
            logger.warning("Scheduler is already running")
            return
        
        self._running = True
        logger.info("Starting Continuous Audit Scheduler")
        
        loop = self._get_loop()
        
        while self._running:
            await self._check_and_run_tasks()
            await asyncio.sleep(self._check_interval)
    
    def stop(self):
        """إيقاف المجدول"""
        self._running = False
        logger.info("Stopping Continuous Audit Scheduler")
    
    def get_scheduled_tasks(self) -> List[Dict]:
        """الحصول على قائمة المهام المجدولة"""
        return [
            {
                "task_id": task.task_id,
                "name": task.name,
                "interval": task.interval.value,
                "interval_value": task.interval_value,
                "enabled": task.enabled,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "next_run": task.next_run.isoformat() if task.next_run else None,
                "metadata": task.metadata
            }
            for task in self._tasks.values()
        ]
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """الحصول على حالة مهمة محددة"""
        task = self._tasks.get(task_id)
        if task:
            return {
                "task_id": task.task_id,
                "name": task.name,
                "interval": task.interval.value,
                "enabled": task.enabled,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "next_run": task.next_run.isoformat() if task.next_run else None,
                "metadata": task.metadata
            }
        return None


_scheduler_instance: Optional[ContinuousAuditScheduler] = None


def get_scheduler() -> ContinuousAuditScheduler:
    """الحصول على نسخة المجدول"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = ContinuousAuditScheduler()
    return _scheduler_instance


# وظائف مساعدة للمراجعات الشائعة

async def run_fraud_detection_audit():
    """تشغيل مراجعة كشف الاحتيال الدورية"""
    logger.info("Running periodic fraud detection audit")
    from backend.orchestrator.agent_orchestrator import AgentOrchestrator
    from agents.fraud_agent.agent import FraudDetectionAgent
    
    orchestrator = AgentOrchestrator(auto_register_agents=False)
    fraud_agent = FraudDetectionAgent()
    orchestrator.register_agent("fraud_agent", fraud_agent)
    
    # تنفيذ المراجعة مع بيانات من قاعدة البيانات
    # هذا مثال بسيط - في الإنتاج يجب جلب البيانات الفعلية
    sample_data = {"transactions": []}
    result = await orchestrator.execute_audit_workflow(sample_data)
    
    return result


async def run_compliance_check():
    """تشغيل فحص الامتثال الدوري"""
    logger.info("Running periodic compliance check")
    from agents.compliance_agent.agent import ComplianceStandardsAgent
    
    agent = ComplianceStandardsAgent()
    result = await agent.check_compliance({})
    
    return result


async def run_risk_assessment():
    """تشغيل تقييم المخاطر الدوري"""
    logger.info("Running periodic risk assessment")
    from agents.risk_agent.agent import RiskScoringAgent
    
    agent = RiskScoringAgent()
    result = await agent.assess_risks({})
    
    return result


def setup_default_scheduled_tasks():
    """إعداد المهام المجدولة الافتراضية"""
    scheduler = get_scheduler()
    
    # مراجعة الاحتيال يومياً
    scheduler.register_task(
        task_id="fraud_detection_daily",
        name="Daily Fraud Detection",
        function=run_fraud_detection_audit,
        interval=ScheduleInterval.DAILY,
        metadata={"save_result": True, "priority": "high"}
    )
    
    # فحص الامتثال أسبوعياً
    scheduler.register_task(
        task_id="compliance_weekly",
        name="Weekly Compliance Check",
        function=run_compliance_check,
        interval=ScheduleInterval.WEEKLY,
        metadata={"save_result": True, "priority": "medium"}
    )
    
    # تقييم المخاطر شهرياً
    scheduler.register_task(
        task_id="risk_monthly",
        name="Monthly Risk Assessment",
        function=run_risk_assessment,
        interval=ScheduleInterval.MONTHLY,
        metadata={"save_result": True, "priority": "medium"}
    )
    
    logger.info("Default scheduled tasks configured")
