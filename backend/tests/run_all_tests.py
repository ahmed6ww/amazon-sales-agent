#!/usr/bin/env python3
"""
Test Runner for All 24 Requirements

This script runs all requirement tests and provides a comprehensive report.
Usage: python run_all_tests.py
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def run_pytest_tests():
    """Run tests using pytest"""
    print("=" * 80)
    print("RUNNING ALL 24 REQUIREMENT TESTS WITH PYTEST")
    print("=" * 80)
    
    # Test files to run
    test_files = [
        "tests/test_requirements_1_6.py",
        "tests/test_requirements_7_12.py", 
        "tests/test_requirements_13_18.py",
        "tests/test_requirements_19_24.py"
    ]
    
    # Run pytest for each test file
    total_passed = 0
    total_failed = 0
    
    for test_file in test_files:
        print(f"\n{'='*20} Running {test_file} {'='*20}")
        
        try:
            # Run pytest with verbose output
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_file, 
                "-v", 
                "--tb=short",
                "--no-header"
            ], 
            cwd=backend_dir,
            capture_output=True, 
            text=True
            )
            
            # Parse pytest output
            output_lines = result.stdout.split('\n')
            passed = 0
            failed = 0
            
            for line in output_lines:
                if " PASSED " in line:
                    passed += 1
                elif " FAILED " in line:
                    failed += 1
            
            total_passed += passed
            total_failed += failed
            
            print(f"Results: {passed} passed, {failed} failed")
            
            if result.returncode != 0:
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
            
        except Exception as e:
            print(f"Error running {test_file}: {e}")
            total_failed += 1
    
    return total_passed, total_failed

def run_comprehensive_test():
    """Run the comprehensive test suite"""
    print("\n" + "=" * 80)
    print("RUNNING COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    try:
        from tests.test_all_requirements import run_comprehensive_tests
        results = run_comprehensive_tests()
        return results
    except Exception as e:
        print(f"Error running comprehensive tests: {e}")
        return None

def main():
    """Main test runner"""
    print("Starting comprehensive test suite for all 24 requirements...")
    
    # Run pytest tests
    pytest_passed, pytest_failed = run_pytest_tests()
    
    # Run comprehensive test suite
    comprehensive_results = run_comprehensive_test()
    
    # Generate final report
    print("\n" + "=" * 80)
    print("FINAL TEST REPORT")
    print("=" * 80)
    
    print(f"Pytest Results: {pytest_passed} passed, {pytest_failed} failed")
    
    if comprehensive_results:
        print(f"Comprehensive Results: {comprehensive_results['passed_tests']} passed, {comprehensive_results['failed_tests']} failed")
        print(f"Success Rate: {comprehensive_results['success_rate']:.1f}%")
    
    total_tests = pytest_passed + pytest_failed
    if total_tests > 0:
        overall_success_rate = (pytest_passed / total_tests) * 100
        print(f"Overall Success Rate: {overall_success_rate:.1f}%")
        
        if overall_success_rate >= 90:
            print("\n🎉 EXCELLENT: All requirements are well implemented!")
        elif overall_success_rate >= 70:
            print("\n👍 GOOD: Most requirements are implemented, some need work.")
        elif overall_success_rate >= 50:
            print("\n⚠️  FAIR: About half the requirements are implemented.")
        else:
            print("\n❌ POOR: Most requirements need significant work.")
    
    print("\n" + "=" * 80)
    print("TEST RUNNER COMPLETED")
    print("=" * 80)
    
    # Exit with appropriate code
    if pytest_failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {pytest_failed} tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


