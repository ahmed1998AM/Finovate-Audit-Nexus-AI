"""
Audit Service - خدمة إدارة مشاريع المراجعة والتدقيق
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from database.db_manager import get_db_manager
from connectors.sap_connector.connector import SAPErpConnector, SAPConnectionConfig
from agents.chief_agent.agent import get_chief_agent

logger = logging.getLogger(__name__)


class AuditService:
    """
    خدمة إدارة مشاريع المراجعة والتدقيق
    
    المسؤولة عن:
    - إنشاء مشاريع مراجعة جديدة
    - إدارة مراحل المراجعة
    - تتبع التقدم
    - إدارة النتائج والملاحظات
    - توليد تقارير المراجعة
    """
    
    def __init__(self, db_session=None):
        """
        تهيئة خدمة المراجعة
        
        Args:
            db_session: جلسة قاعدة البيانات
        """
        self.db_session = db_session
        self.db_manager = get_db_manager()
        self.chief_agent = get_chief_agent()
        self.active_projects = {}
        logger.info("AuditService initialized")

    async def run_full_ai_audit(self, company_code: str, fiscal_year: str, engagement_id: int) -> Dict[str, Any]:
        """
        Run a full AI-driven audit workflow
        """
        session = self.db_manager.get_session()
        try:
            # 1. Connect to ERP (Mocked)
            config = SAPConnectionConfig(
                host="sap-erp.company.com",
                system_number="00",
                client="100",
                username="audit_user",
                password="secure_password"
            )
            connector = SAPErpConnector(config)
            connector.connect()

            # 2. Fetch Data
            journal_entries = connector.get_journal_entries(company_code, fiscal_year)
            income_statement = connector.get_financial_statements(company_code, fiscal_year, "income_statement")
            balance_sheet = connector.get_financial_statements(company_code, fiscal_year, "balance_sheet")

            # 3. Save raw data
            self.db_manager.save_financial_data(session, journal_entries, "SAP")
            
            # 4. Run AI analysis
            audit_data = {
                "journal_entries": journal_entries,
                "income_statement": {"current": income_statement},
                "balance_sheet": balance_sheet,
                "entity_id": company_code,
                "fiscal_year": fiscal_year
            }
            analysis_results = await self.chief_agent.run_audit_workflow(audit_data)

            # 5. Save findings
            if 'fraud_agent' in analysis_results.get('core_results', {}):
                fraud_findings = analysis_results['core_results']['fraud_agent']
                self.db_manager.save_anomalies(session, fraud_findings.get('fraud_indicators', []))
            
            if 'risk_assessment' in analysis_results:
                self.db_manager.save_risk_assessment(session, analysis_results['risk_assessment'], engagement_id)

            return analysis_results
        finally:
            session.close()
    
    def create_audit_project(
        self,
        company_id: int,
        project_name: str,
        audit_type: str,
        start_date: datetime,
        end_date: datetime,
        team_members: List[int],
        scope: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        إنشاء مشروع مراجعة جديد
        
        Args:
            company_id: معرف الشركة
            project_name: اسم المشروع
            audit_type: نوع المراجعة (financial, tax, fraud, compliance)
            start_date: تاريخ البدء
            end_date: تاريخ الانتهاء
            team_members: قائمة أعضاء الفريق
            scope: نطاق المراجعة
            
        Returns:
            معلومات المشروع المنشأ
        """
        project_id = f"AUD-{datetime.now().strftime('%Y%m%d')}-{len(self.active_projects) + 1:04d}"
        
        project = {
            'project_id': project_id,
            'company_id': company_id,
            'project_name': project_name,
            'audit_type': audit_type,
            'start_date': start_date,
            'end_date': end_date,
            'team_members': team_members,
            'scope': scope,
            'status': 'planning',
            'progress': 0,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        self.active_projects[project_id] = project
        logger.info(f"Created audit project: {project_id}")
        
        return project
    
    def update_project_status(self, project_id: str, status: str, progress: Optional[float] = None) -> bool:
        """
        تحديث حالة المشروع
        
        Args:
            project_id: معرف المشروع
            status: الحالة الجديدة
            progress: نسبة التقدم (اختياري)
            
        Returns:
            True إذا نجح التحديث
        """
        if project_id not in self.active_projects:
            logger.error(f"Project {project_id} not found")
            return False
        
        project = self.active_projects[project_id]
        project['status'] = status
        if progress is not None:
            project['progress'] = min(100, max(0, progress))
        project['updated_at'] = datetime.now()
        
        logger.info(f"Updated project {project_id} status to {status}")
        return True
    
    def add_finding(
        self,
        project_id: str,
        finding_type: str,
        severity: str,
        description: str,
        evidence: List[str],
        recommendation: str,
        affected_accounts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        إضافة ملاحظة/نتيجة مراجعة
        
        Args:
            project_id: معرف المشروع
            finding_type: نوع النتيجة (error, fraud, compliance, risk)
            severity: الخطورة (low, medium, high, critical)
            description: الوصف
            evidence: الأدلة
            recommendation: التوصية
            affected_accounts: الحسابات المتأثرة
            
        Returns:
            معلومات النتيجة
        """
        if project_id not in self.active_projects:
            logger.error(f"Project {project_id} not found")
            return {}
        
        finding_id = f"FND-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(self.active_projects[project_id].get('findings', [])) + 1:04d}"
        
        finding = {
            'finding_id': finding_id,
            'project_id': project_id,
            'finding_type': finding_type,
            'severity': severity,
            'description': description,
            'evidence': evidence,
            'recommendation': recommendation,
            'affected_accounts': affected_accounts or [],
            'status': 'open',
            'created_at': datetime.now(),
            'reviewed_by': None,
            'reviewed_at': None
        }
        
        if 'findings' not in self.active_projects[project_id]:
            self.active_projects[project_id]['findings'] = []
        
        self.active_projects[project_id]['findings'].append(finding)
        logger.info(f"Added finding {finding_id} to project {project_id}")
        
        return finding
    
    def get_project_summary(self, project_id: str) -> Dict[str, Any]:
        """
        الحصول على ملخص المشروع
        
        Args:
            project_id: معرف المشروع
            
        Returns:
            ملخص المشروع
        """
        if project_id not in self.active_projects:
            logger.error(f"Project {project_id} not found")
            return {}
        
        project = self.active_projects[project_id]
        findings = project.get('findings', [])
        
        summary = {
            'project_id': project_id,
            'project_name': project['project_name'],
            'status': project['status'],
            'progress': project['progress'],
            'total_findings': len(findings),
            'findings_by_severity': {
                'critical': len([f for f in findings if f['severity'] == 'critical']),
                'high': len([f for f in findings if f['severity'] == 'high']),
                'medium': len([f for f in findings if f['severity'] == 'medium']),
                'low': len([f for f in findings if f['severity'] == 'low'])
            },
            'findings_by_type': {
                'error': len([f for f in findings if f['finding_type'] == 'error']),
                'fraud': len([f for f in findings if f['finding_type'] == 'fraud']),
                'compliance': len([f for f in findings if f['finding_type'] == 'compliance']),
                'risk': len([f for f in findings if f['finding_type'] == 'risk'])
            },
            'start_date': project['start_date'],
            'end_date': project['end_date']
        }
        
        return summary
    
    def list_projects(self, company_id: Optional[int] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        قائمة مشاريع المراجعة
        
        Args:
            company_id: تصفية حسب الشركة (اختياري)
            status: تصفية حسب الحالة (اختياري)
            
        Returns:
            قائمة المشاريع
        """
        projects = list(self.active_projects.values())
        
        if company_id is not None:
            projects = [p for p in projects if p['company_id'] == company_id]
        
        if status is not None:
            projects = [p for p in projects if p['status'] == status]
        
        return projects
    
    def close_project(self, project_id: str, final_report: str) -> bool:
        """
        إغلاق المشروع
        
        Args:
            project_id: معرف المشروع
            final_report: التقرير النهائي
            
        Returns:
            True إذا نجح الإغلاق
        """
        if project_id not in self.active_projects:
            logger.error(f"Project {project_id} not found")
            return False
        
        project = self.active_projects[project_id]
        project['status'] = 'closed'
        project['progress'] = 100
        project['final_report'] = final_report
        project['closed_at'] = datetime.now()
        project['updated_at'] = datetime.now()
        
        logger.info(f"Closed project {project_id}")
        return True
