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
    print("[TEST] Running Unit Tests")
    print("="*60)
    
    test_dir = Path(__file__).parent / "tests" / "unit"
    if not test_dir.exists():
        print("[WARN] Unit tests directory not found")
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
    print("[LINK] Running Integration Tests")
    print("="*60)
    
    test_dir = Path(__file__).parent / "tests" / "integration"
    if not test_dir.exists():
        print("[WARN] Integration tests directory not found")
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
    print("[PLUG] Running Connector Tests")
    print("="*60)
    
    test_files = [
        str(Path(__file__).parent / "tests" / "unit" / "test_connector_fallbacks.py"),
        str(Path(__file__).parent / "tests" / "unit" / "test_connector_loader.py"),
    ]
    exit_code = pytest.main([
        "-v",
        "--tb=short",
        *test_files,
    ])
    
    return exit_code


def run_agent_tests():
    """تشغيل اختبارات الوكلاء"""
    print("\n" + "="*60)
    print("[BOT] Running Agent Tests")
    print("="*60)
    
    test_dir = Path(__file__).parent / "tests" / "unit" / "agents"
    if not test_dir.exists():
        print("[WARN] Agent tests directory not found")
        return 0
        
    exit_code = pytest.main([
        "-v",
        "--tb=short",
        str(test_dir)
    ])
    
    return exit_code


def run_performance_tests():
    """تشغيل اختبارات الأداء والتحمل"""
    print("\n" + "="*60)
    print("[ZAP] Running Performance & Load Tests")
    print("="*60)

    test_dir = Path(__file__).parent / "tests" / "performance"
    if not test_dir.exists():
        print("[WARN] Performance tests directory not found")
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
    print("[ROCKET] Finovate Audit Nexus AI - Full Test Suite")
    print("="*60)
    
    results = {
        "unit": run_unit_tests(),
        "integration": run_integration_tests(),
        "connectors": run_connector_tests(),
        "agents": run_agent_tests(),
        "performance": run_performance_tests(),
    }
    
    print("\n" + "="*60)
    print("[CHART] Test Results Summary")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v == 0)
    
    for test_type, exit_code in results.items():
        status = "[PASS] PASSED" if exit_code == 0 else "[FAIL] FAILED"
        print(f"  {test_type.capitalize()}: {status}")
        
    print(f"\nTotal: {passed_tests}/{total_tests} test suites passed")
    
    if passed_tests == total_tests:
        print("\n[CONFETTI] All tests passed successfully!")
        return 0
    else:
        print(f"\n[WARN] {total_tests - passed_tests} test suite(s) failed")
        return 1


def generate_coverage_report():
    """توليد تقرير التغطية"""
    print("\n" + "="*60)
    print("[CHART] Generating Coverage Report")
    print("="*60)
    
    try:
        import coverage
    except ImportError:
        print("[WARN] coverage package not installed. Install with: pip install coverage")
        return
        
    cov = coverage.Coverage()
    cov.start()
    
    # استيراد جميع الوحدات
    try:
        import connectors
        import backend.agents
        import backend.services
    except Exception as e:
        print(f"[WARN] Error importing modules: {e}")
        
    cov.stop()
    cov.save()
    
    print("\nCoverage Report:")
    cov.report()
    
    # توليد تقرير HTML
    cov.html_report(directory="htmlcov")
    print("\n[FILE] HTML report generated in htmlcov/")


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
        elif command == "performance":
            sys.exit(run_performance_tests())
        elif command == "coverage":
            generate_coverage_report()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: unit, integration, connectors, agents, performance, coverage")
            sys.exit(1)
    else:
        sys.exit(run_all_tests())
