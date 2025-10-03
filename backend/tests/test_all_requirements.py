"""
Comprehensive Test Suite for All 24 Requirements

This test file runs all requirement tests in sequence and provides
a comprehensive report of the implementation status.
"""

import pytest
import sys
import os
from typing import Dict, Any, List

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from test_requirements_1_6 import TestRequirements1To6
from test_requirements_7_12 import TestRequirements7To12
from test_requirements_13_18 import TestRequirements13To18
from test_requirements_19_24 import TestRequirements19To24


class TestAllRequirements:
    """Comprehensive test suite for all 24 requirements"""
    
    def __init__(self):
        self.test_results = {}
        self.requirement_status = {}
    
    def run_all_tests(self):
        """Run all requirement tests and generate comprehensive report"""
        print("=" * 80)
        print("COMPREHENSIVE TEST SUITE FOR ALL 24 REQUIREMENTS")
        print("=" * 80)
        
        # Initialize test classes
        test_classes = [
            ("Requirements 1-6", TestRequirements1To6()),
            ("Requirements 7-12", TestRequirements7To12()),
            ("Requirements 13-18", TestRequirements13To18()),
            ("Requirements 19-24", TestRequirements19To24())
        ]
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        # Run tests for each requirement group
        for group_name, test_class in test_classes:
            print(f"\n{'='*20} {group_name} {'='*20}")
            
            group_results = self._run_test_group(test_class)
            self.test_results[group_name] = group_results
            
            # Update counters
            group_total = group_results["total"]
            group_passed = group_results["passed"]
            group_failed = group_results["failed"]
            
            total_tests += group_total
            passed_tests += group_passed
            failed_tests += group_failed
            
            print(f"Group Results: {group_passed}/{group_total} passed, {group_failed} failed")
        
        # Generate comprehensive report
        self._generate_comprehensive_report(total_tests, passed_tests, failed_tests)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "test_results": self.test_results
        }
    
    def _run_test_group(self, test_class):
        """Run all tests in a test class using pytest"""
        import subprocess
        import tempfile
        import inspect
        
        # Get test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        group_results = {
            "total": len(test_methods),
            "passed": 0,
            "failed": 0,
            "test_details": {}
        }
        
        # Create a temporary test file for this class
        class_name = test_class.__class__.__name__
        module_name = test_class.__class__.__module__
        
        # Get the test file path
        if "test_requirements_1_6" in module_name:
            test_file = "tests/test_requirements_1_6.py"
        elif "test_requirements_7_12" in module_name:
            test_file = "tests/test_requirements_7_12.py"
        elif "test_requirements_13_18" in module_name:
            test_file = "tests/test_requirements_13_18.py"
        elif "test_requirements_19_24" in module_name:
            test_file = "tests/test_requirements_19_24.py"
        else:
            test_file = None
        
        if test_file:
            # Run pytest for this specific test file
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pytest", 
                    test_file, 
                    "-v", 
                    "--tb=short",
                    "--no-header"
                ], 
                cwd=os.path.join(os.path.dirname(__file__), '..'),
                capture_output=True, 
                text=True
                )
                
                # Parse pytest output
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if " PASSED " in line:
                        group_results["passed"] += 1
                        # Extract test method name
                        if "::" in line:
                            test_name = line.split("::")[-1].split(" ")[0]
                            group_results["test_details"][test_name] = "PASSED"
                    elif " FAILED " in line:
                        group_results["failed"] += 1
                        # Extract test method name
                        if "::" in line:
                            test_name = line.split("::")[-1].split(" ")[0]
                            group_results["test_details"][test_name] = "FAILED"
                
                # If pytest failed, show the output
                if result.returncode != 0:
                    print("STDOUT:", result.stdout)
                    print("STDERR:", result.stderr)
                    
            except Exception as e:
                print(f"Error running pytest for {test_file}: {e}")
                # Fallback to direct method calls
                for test_method in test_methods:
                    try:
                        print(f"Running {test_method}...")
                        getattr(test_class, test_method)()
                        group_results["passed"] += 1
                        group_results["test_details"][test_method] = "PASSED"
                        print(f"✅ {test_method} PASSED")
                    except Exception as e:
                        group_results["failed"] += 1
                        group_results["test_details"][test_method] = f"FAILED: {str(e)}"
                        print(f"❌ {test_method} FAILED: {str(e)}")
        else:
            # Fallback to direct method calls
            for test_method in test_methods:
                try:
                    print(f"Running {test_method}...")
                    getattr(test_class, test_method)()
                    group_results["passed"] += 1
                    group_results["test_details"][test_method] = "PASSED"
                    print(f"✅ {test_method} PASSED")
                except Exception as e:
                    group_results["failed"] += 1
                    group_results["test_details"][test_method] = f"FAILED: {str(e)}"
                    print(f"❌ {test_method} FAILED: {str(e)}")
        
        return group_results
    
    def _generate_comprehensive_report(self, total_tests, passed_tests, failed_tests):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n" + "-" * 80)
        print("REQUIREMENT STATUS SUMMARY")
        print("-" * 80)
        
        # Map test results to requirements
        requirement_mapping = {
            "Requirements 1-6": [1, 2, 3, 4, 5, 6],
            "Requirements 7-12": [7, 8, 9, 10, 11, 12],
            "Requirements 13-18": [13, 14, 15, 16, 17, 18],
            "Requirements 19-24": [19, 20, 21, 22, 23, 24]
        }
        
        for group_name, requirements in requirement_mapping.items():
            group_results = self.test_results.get(group_name, {})
            group_success_rate = (group_results.get("passed", 0) / group_results.get("total", 1)) * 100
            
            print(f"\n{group_name}:")
            for req_num in requirements:
                status = "✅ IMPLEMENTED" if group_success_rate >= 80 else "❌ NEEDS WORK"
                print(f"  Requirement {req_num}: {status}")
        
        print("\n" + "-" * 80)
        print("DETAILED TEST RESULTS")
        print("-" * 80)
        
        for group_name, group_results in self.test_results.items():
            print(f"\n{group_name}:")
            for test_name, test_result in group_results["test_details"].items():
                status_icon = "✅" if test_result == "PASSED" else "❌"
                print(f"  {status_icon} {test_name}: {test_result}")
        
        print("\n" + "=" * 80)
        print("TEST SUITE COMPLETED")
        print("=" * 80)
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: All requirements are well implemented!")
        elif success_rate >= 70:
            print("👍 GOOD: Most requirements are implemented, some need work.")
        elif success_rate >= 50:
            print("⚠️  FAIR: About half the requirements are implemented.")
        else:
            print("❌ POOR: Most requirements need significant work.")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate
        }


def run_comprehensive_tests():
    """Main function to run all tests"""
    test_suite = TestAllRequirements()
    return test_suite.run_all_tests()


if __name__ == "__main__":
    # Run the comprehensive test suite
    results = run_comprehensive_tests()
    
    # Exit with appropriate code
    if results["failed_tests"] == 0:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n❌ {results['failed_tests']} tests failed!")
        sys.exit(1)


