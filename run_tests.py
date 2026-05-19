"""
Finovate Audit Nexus AI - Test Suite Runner
تشغيل مجموعة الاختبارات الشاملة
"""

import pytest
import sys
import os
from pathlib import Path


def run_unit_tests():
    """تشغيل اختبارات الوحدة"""
    print("\n" + "="*60)
    print("🧪 Running Unit Tests")
    print("="*60)
    
    test_dir = Path(__file__).parent / "tests" / "unit"
    if not test_dir.exists():
        print("⚠️  Unit tests directory not found")
        return 0
        
    exit_code = pytest.main([
        "-v",
        "--tb=short",
        str(test_dir),
        "-k", "not integration"
    ])
    
    return exit_code


def run_integration_tests():
    """تشغيل اختبارات التكامل"""
    print("\n" + "="*60)
    print("🔗 Running Integration Tests")
    print("="*60)
    
    test_dir = Path(__file__).parent / "tests" / "integration"
    if not test_dir.exists():
        print("⚠️  Integration tests directory not found")
        return 0
        
    exit_code = pytest.main([
        "-v",
        "--tb=short",
        str(test_dir)
    ])
    
    return exit_code


def run_connector_tests():
    """تشغيل اختبارات الموصلات"""
    print("\n" + "="*60)
    print("🔌 Running Connector Tests")
    print("="*60)
    
    test_dir = Path(__file__).parent / "tests" / "unit" / "connectors"
    if not test_dir.exists():
        print("⚠️  Connector tests directory not found")
        return 0
        
    exit_code = pytest.main([
        "-v",
        "--tb=short",
        str(test_dir)
    ])
    
    return exit_code


def run_agent_tests():
    """تشغيل اختبارات الوكلاء"""
    print("\n" + "="*60)
    print("🤖 Running Agent Tests")
    print("="*60)
    
    test_dir = Path(__file__).parent / "tests" / "unit" / "agents"
    if not test_dir.exists():
        print("⚠️  Agent tests directory not found")
        return 0
        
    exit_code = pytest.main([
        "-v",
        "--tb=short",
        str(test_dir)
    ])
    
    return exit_code


def run_all_tests():
    """تشغيل جميع الاختبارات"""
    print("\n" + "="*60)
    print("🚀 Finovate Audit Nexus AI - Full Test Suite")
    print("="*60)
    
    results = {
        "unit": run_unit_tests(),
        "integration": run_integration_tests(),
        "connectors": run_connector_tests(),
        "agents": run_agent_tests()
    }
    
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v == 0)
    
    for test_type, exit_code in results.items():
        status = "✅ PASSED" if exit_code == 0 else "❌ FAILED"
        print(f"  {test_type.capitalize()}: {status}")
        
    print(f"\nTotal: {passed_tests}/{total_tests} test suites passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed successfully!")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test suite(s) failed")
        return 1


def generate_coverage_report():
    """توليد تقرير التغطية"""
    print("\n" + "="*60)
    print("📈 Generating Coverage Report")
    print("="*60)
    
    try:
        import coverage
    except ImportError:
        print("⚠️  coverage package not installed. Install with: pip install coverage")
        return
        
    cov = coverage.Coverage()
    cov.start()
    
    # استيراد جميع الوحدات
    try:
        from connectors import *
        from backend.agents import *
        from backend.services import *
    except Exception as e:
        print(f"⚠️  Error importing modules: {e}")
        
    cov.stop()
    cov.save()
    
    print("\nCoverage Report:")
    cov.report()
    
    # توليد تقرير HTML
    cov.html_report(directory="htmlcov")
    print("\n📄 HTML report generated in htmlcov/")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "unit":
            sys.exit(run_unit_tests())
        elif command == "integration":
            sys.exit(run_integration_tests())
        elif command == "connectors":
            sys.exit(run_connector_tests())
        elif command == "agents":
            sys.exit(run_agent_tests())
        elif command == "coverage":
            generate_coverage_report()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: unit, integration, connectors, agents, coverage")
            sys.exit(1)
    else:
        sys.exit(run_all_tests())
