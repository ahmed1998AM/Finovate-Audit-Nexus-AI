"""
Finovate Audit Nexus AI - Professional Reports Viewer
عارض التقارير الاحترافي
"""
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportsViewer:
    """
    عارض التقارير الاحترافي
    يدعم PDF, Excel, Word, HTML
    """
    
    def __init__(self, exports_dir: str = "exports", reports_dir: str = "reports"):
        self.exports_dir = Path(exports_dir)
        self.reports_dir = Path(reports_dir)
        
        # تأكد من وجود المجلدات
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def list_reports(self, report_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """سرد جميع التقارير المتاحة"""
        reports = []
        
        # البحث في مجلد التقارير
        for file_path in self.reports_dir.glob("**/*"):
            if file_path.is_file():
                report_info = self._get_file_info(file_path)
                if report_type is None or report_info["type"] == report_type:
                    reports.append(report_info)
        
        # البحث في مجلد التصدير
        for file_path in self.exports_dir.glob("**/*"):
            if file_path.is_file():
                report_info = self._get_file_info(file_path)
                if report_type is None or report_info["type"] == report_type:
                    reports.append(report_info)
        
        return sorted(reports, key=lambda x: x["modified"], reverse=True)
    
    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """الحصول على معلومات الملف"""
        file_ext = file_path.suffix.lower()
        
        type_mapping = {
            ".pdf": "PDF",
            ".xlsx": "Excel",
            ".xls": "Excel",
            ".docx": "Word",
            ".doc": "Word",
            ".html": "HTML",
            ".htm": "HTML",
            ".csv": "CSV",
            ".json": "JSON"
        }
        
        return {
            "name": file_path.name,
            "path": str(file_path.absolute()),
            "type": type_mapping.get(file_ext, "Unknown"),
            "extension": file_ext,
            "size_bytes": file_path.stat().st_size,
            "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
            "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
    
    def get_report_summary(self, report_path: str) -> Dict[str, Any]:
        """الحصول على ملخص التقرير"""
        path = Path(report_path)
        
        if not path.exists():
            return {"error": "File not found"}
        
        file_ext = path.suffix.lower()
        
        if file_ext == ".pdf":
            return self._summarize_pdf(path)
        elif file_ext in [".xlsx", ".xls"]:
            return self._summarize_excel(path)
        elif file_ext in [".docx", ".doc"]:
            return self._summarize_word(path)
        elif file_ext in [".html", ".htm"]:
            return self._summarize_html(path)
        elif file_ext == ".csv":
            return self._summarize_csv(path)
        
        return {"type": "Unknown", "path": str(path)}
    
    def _summarize_pdf(self, path: Path) -> Dict[str, Any]:
        """تلخيص ملف PDF"""
        try:
            # في الإنتاج، استخدم PyMuPDF أو pdfplumber
            # import fitz
            # doc = fitz.open(path)
            # pages = len(doc)
            # doc.close()
            
            return {
                "type": "PDF",
                "name": path.name,
                "size_mb": round(path.stat().st_size / (1024 * 1024), 2),
                "pages": "N/A (install PyMuPDF for details)",
                "preview": "PDF document - requires PDF reader",
                "metadata": {
                    "created": datetime.fromtimestamp(path.stat().st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error summarizing PDF: {e}")
            return {"type": "PDF", "error": str(e)}
    
    def _summarize_excel(self, path: Path) -> Dict[str, Any]:
        """تلخيص ملف Excel"""
        try:
            import pandas as pd
            
            # قراءة أسماء الأوراق
            excel_file = pd.ExcelFile(path)
            sheet_names = excel_file.sheet_names
            
            sheets_info = []
            for sheet in sheet_names[:5]:  # أول 5 أوراق فقط
                df = pd.read_excel(path, sheet_name=sheet, nrows=5)
                sheets_info.append({
                    "name": sheet,
                    "rows": len(df),
                    "columns": list(df.columns.tolist())
                })
            
            return {
                "type": "Excel",
                "name": path.name,
                "size_mb": round(path.stat().st_size / (1024 * 1024), 2),
                "sheets": sheet_names,
                "sheets_preview": sheets_info,
                "total_sheets": len(sheet_names),
                "preview": f"Excel workbook with {len(sheet_names)} sheet(s)"
            }
        except Exception as e:
            logger.error(f"Error summarizing Excel: {e}")
            return {"type": "Excel", "error": str(e)}
    
    def _summarize_word(self, path: Path) -> Dict[str, Any]:
        """تلخيص ملف Word"""
        try:
            # في الإنتاج، استخدم python-docx
            # from docx import Document
            # doc = Document(path)
            # paragraphs = len(doc.paragraphs)
            
            return {
                "type": "Word",
                "name": path.name,
                "size_mb": round(path.stat().st_size / (1024 * 1024), 2),
                "preview": "Word document - requires Word reader",
                "metadata": {
                    "created": datetime.fromtimestamp(path.stat().st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error summarizing Word: {e}")
            return {"type": "Word", "error": str(e)}
    
    def _summarize_html(self, path: Path) -> Dict[str, Any]:
        """تلخيص ملف HTML"""
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
            
            # استخراج العنوان
            title = "No Title"
            if "<title>" in content:
                start = content.find("<title>") + 7
                end = content.find("</title>")
                if end > start:
                    title = content[start:end].strip()
            
            return {
                "type": "HTML",
                "name": path.name,
                "size_kb": round(path.stat().st_size / 1024, 2),
                "title": title,
                "content_length": len(content),
                "preview": content[:500] + "..." if len(content) > 500 else content
            }
        except Exception as e:
            logger.error(f"Error summarizing HTML: {e}")
            return {"type": "HTML", "error": str(e)}
    
    def _summarize_csv(self, path: Path) -> Dict[str, Any]:
        """تلخيص ملف CSV"""
        try:
            import pandas as pd
            
            df = pd.read_csv(path, nrows=5)
            
            return {
                "type": "CSV",
                "name": path.name,
                "size_kb": round(path.stat().st_size / 1024, 2),
                "columns": df.columns.tolist(),
                "rows_sample": len(df),
                "preview": df.head().to_dict('records')
            }
        except Exception as e:
            logger.error(f"Error summarizing CSV: {e}")
            return {"type": "CSV", "error": str(e)}
    
    def export_report(self, data: Dict[str, Any], filename: str, 
                     format: str = "excel") -> str:
        """تصدير تقرير جديد"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "excel":
            if not filename.endswith(".xlsx"):
                filename = filename.replace(".xlsx", "") + ".xlsx"
            
            filepath = self.exports_dir / f"{timestamp}_{filename}"
            
            try:
                import pandas as pd
                
                # تحويل البيانات إلى DataFrame
                if isinstance(data, dict):
                    df = pd.DataFrame([data])
                elif isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    df = pd.DataFrame([{"data": str(data)}])
                
                # الحفظ كـ Excel
                df.to_excel(filepath, index=False)
                
                logger.info(f"Report exported to {filepath}")
                return str(filepath)
                
            except Exception as e:
                logger.error(f"Error exporting Excel: {e}")
                raise
        
        elif format == "csv":
            if not filename.endswith(".csv"):
                filename = filename.replace(".csv", "") + ".csv"
            
            filepath = self.exports_dir / f"{timestamp}_{filename}"
            
            try:
                import pandas as pd
                
                if isinstance(data, dict):
                    df = pd.DataFrame([data])
                elif isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    df = pd.DataFrame([{"data": str(data)}])
                
                df.to_csv(filepath, index=False)
                
                logger.info(f"Report exported to {filepath}")
                return str(filepath)
                
            except Exception as e:
                logger.error(f"Error exporting CSV: {e}")
                raise
        
        elif format == "json":
            if not filename.endswith(".json"):
                filename = filename.replace(".json", "") + ".json"
            
            filepath = self.exports_dir / f"{timestamp}_{filename}"
            
            import json
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Report exported to {filepath}")
            return str(filepath)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def delete_report(self, report_path: str) -> bool:
        """حذف تقرير"""
        try:
            path = Path(report_path)
            
            # التأكد من أن الملف في المجلدات المسموحة
            if not (str(path.absolute()).startswith(str(self.exports_dir.absolute())) or
                   str(path.absolute()).startswith(str(self.reports_dir.absolute()))):
                logger.error("Cannot delete file outside allowed directories")
                return False
            
            path.unlink()
            logger.info(f"Deleted report: {report_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting report: {e}")
            return False
    
    def search_reports(self, keyword: str) -> List[Dict[str, Any]]:
        """البحث في التقارير"""
        all_reports = self.list_reports()
        keyword_lower = keyword.lower()
        
        matching_reports = []
        for report in all_reports:
            if (keyword_lower in report["name"].lower() or
                keyword_lower in report.get("type", "").lower()):
                matching_reports.append(report)
        
        return matching_reports
    
    def get_statistics(self) -> Dict[str, Any]:
        """إحصائيات التقارير"""
        all_reports = self.list_reports()
        
        stats = {
            "total_reports": len(all_reports),
            "by_type": {},
            "total_size_mb": 0,
            "newest_report": None,
            "oldest_report": None
        }
        
        for report in all_reports:
            # حسب النوع
            report_type = report["type"]
            if report_type not in stats["by_type"]:
                stats["by_type"][report_type] = 0
            stats["by_type"][report_type] += 1
            
            # الحجم الكلي
            stats["total_size_mb"] += report.get("size_mb", 0)
        
        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        
        if all_reports:
            stats["newest_report"] = all_reports[0]["name"]
            stats["oldest_report"] = all_reports[-1]["name"]
        
        return stats


# Factory function
def create_reports_viewer(exports_dir: str = "exports", 
                         reports_dir: str = "reports") -> ReportsViewer:
    """إنشاء عارض تقارير"""
    return ReportsViewer(exports_dir, reports_dir)
