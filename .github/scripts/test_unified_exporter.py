#!/usr/bin/env python3
"""
Test script for unified_variable_exporter.py
============================================

This script provides comprehensive testing for the unified variable exporter.
"""

import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path


class UnifiedExporterTester:
    """Test suite for unified variable exporter"""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages"""
        print(f"🧪 [TEST] {message}")
    
    def setup_test_environment(self):
        """Setup test environment with temporary files"""
        self.temp_dir = tempfile.mkdtemp(prefix="unified_exporter_test_")
        self.log(f"Created test directory: {self.temp_dir}")
        
        # Create test pipeline_vars.yaml
        pipeline_vars_content = """# Test pipeline variables
TEST_VAR_1: "test_value_1"
TEST_VAR_2: "test_value_2"
JSON_VAR: '{"key": "value"}'
BOOLEAN_VAR: "true"
NUMBER_VAR: "123"
"""
        
        pipeline_vars_file = os.path.join(self.temp_dir, "pipeline_vars.yaml")
        with open(pipeline_vars_file, "w", encoding="utf-8") as f:
            f.write(pipeline_vars_content)
        
        # Set test environment variables
        os.environ["CI_PROJECT_DIR"] = self.temp_dir
        os.environ["TEST_ENV_VAR"] = "test_env_value"
        
        return pipeline_vars_file
    
    def cleanup_test_environment(self):
        """Cleanup test environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
            self.log("Cleaned up test directory")
    
    def run_test(self, test_name: str, command: list, expected_vars: list = None):
        """Run a single test"""
        self.log(f"Running test: {test_name}")
        
        try:
            # Change to temp directory for pipeline_vars.yaml
            original_cwd = os.getcwd()
            os.chdir(self.temp_dir)
            
            # Run the command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            # Check if command succeeded
            if result.returncode != 0:
                self.test_results.append({
                    "test": test_name,
                    "status": "FAILED",
                    "error": f"Command failed with return code {result.returncode}",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                })
                self.log(f"❌ Test {test_name} FAILED: Command failed", "ERROR")
                return False
            
            # Check expected variables
            if expected_vars:
                missing_vars = []
                for var in expected_vars:
                    if var not in os.environ:
                        missing_vars.append(var)
                
                if missing_vars:
                    self.test_results.append({
                        "test": test_name,
                        "status": "FAILED",
                        "error": f"Missing expected variables: {missing_vars}",
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    })
                    self.log(f"❌ Test {test_name} FAILED: Missing variables {missing_vars}", "ERROR")
                    return False
            
            self.test_results.append({
                "test": test_name,
                "status": "PASSED",
                "stdout": result.stdout,
                "stderr": result.stderr
            })
            self.log(f"✅ Test {test_name} PASSED")
            return True
            
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "FAILED",
                "error": str(e),
                "stdout": "",
                "stderr": ""
            })
            self.log(f"❌ Test {test_name} FAILED: {e}", "ERROR")
            return False
        finally:
            os.chdir(original_cwd)
    
    def test_basic_export(self):
        """Test basic variable export"""
        command = [
            sys.executable, 
            "unified_variable_exporter.py",
            "--step", "generate_inventory",
            "--matrix-env", "test-cluster/e01",
            "--list-vars"
        ]
        
        expected_vars = [
            "TEST_VAR_1", "TEST_VAR_2", "JSON_VAR", "BOOLEAN_VAR", "NUMBER_VAR",
            "CLUSTER_NAME", "ENVIRONMENT_NAME", "ENV_NAME", "FULL_ENV"
        ]
        
        return self.run_test("Basic Export", command, expected_vars)
    
    def test_json_variables(self):
        """Test export with JSON variables"""
        json_vars = {
            "JSON_TEST_VAR": "json_value",
            "ANOTHER_JSON_VAR": "another_json_value"
        }
        
        command = [
            sys.executable,
            "unified_variable_exporter.py",
            "--step", "env_build",
            "--matrix-env", "test-cluster/e01",
            "--variables-json", json.dumps(json_vars),
            "--list-vars"
        ]
        
        expected_vars = [
            "JSON_TEST_VAR", "ANOTHER_JSON_VAR",
            "TEST_VAR_1", "TEST_VAR_2"  # From pipeline_vars.yaml
        ]
        
        return self.run_test("JSON Variables", command, expected_vars)
    
    def test_api_input_simulation(self):
        """Test API input simulation"""
        # Simulate API input through environment variable
        os.environ["GITHUB_PIPELINE_API_INPUT"] = "API_VAR_1=api_value_1\nAPI_VAR_2=api_value_2"
        
        command = [
            sys.executable,
            "unified_variable_exporter.py",
            "--step", "credential_rotation",
            "--matrix-env", "test-cluster/e01",
            "--list-vars"
        ]
        
        expected_vars = [
            "API_VAR_1", "API_VAR_2",
            "TEST_VAR_1", "TEST_VAR_2"  # From pipeline_vars.yaml
        ]
        
        result = self.run_test("API Input Simulation", command, expected_vars)
        
        # Cleanup
        if "GITHUB_PIPELINE_API_INPUT" in os.environ:
            del os.environ["GITHUB_PIPELINE_API_INPUT"]
        
        return result
    
    def test_script_generation(self):
        """Test shell script generation"""
        script_file = os.path.join(self.temp_dir, "test_export.sh")
        
        command = [
            sys.executable,
            "unified_variable_exporter.py",
            "--step", "git_commit",
            "--matrix-env", "test-cluster/e01",
            "--generate-script", script_file
        ]
        
        result = self.run_test("Script Generation", command)
        
        if result and os.path.exists(script_file):
            # Check if script contains expected exports
            with open(script_file, "r", encoding="utf-8") as f:
                script_content = f.read()
            
            expected_exports = ["export TEST_VAR_1", "export CLUSTER_NAME", "export ENV_NAME"]
            missing_exports = [exp for exp in expected_exports if exp not in script_content]
            
            if missing_exports:
                self.log(f"❌ Script generation test FAILED: Missing exports {missing_exports}", "ERROR")
                return False
            else:
                self.log("✅ Script generation test PASSED")
                return True
        
        return result
    
    def test_step_specific_variables(self):
        """Test step-specific variable export"""
        command = [
            sys.executable,
            "unified_variable_exporter.py",
            "--step", "env_build",
            "--matrix-env", "test-cluster/e01",
            "--list-vars"
        ]
        
        expected_vars = [
            "INSTANCES_DIR", "module_ansible_dir", "module_inventory",
            "envgen_args", "envgen_debug", "GIT_STRATEGY", "COMMIT_ENV"
        ]
        
        return self.run_test("Step-Specific Variables", command, expected_vars)
    
    def test_credential_rotation_variables(self):
        """Test credential rotation specific variables"""
        # Set credential rotation environment variables
        os.environ["CRED_ROTATION_PAYLOAD"] = '{"test": "payload"}'
        os.environ["CRED_ROTATION_FORCE"] = "true"
        
        command = [
            sys.executable,
            "unified_variable_exporter.py",
            "--step", "credential_rotation",
            "--matrix-env", "test-cluster/e01",
            "--list-vars"
        ]
        
        expected_vars = [
            "CRED_ROTATION_PAYLOAD", "CRED_ROTATION_FORCE",
            "PUBLIC_AGE_KEYS"  # This should be set by the exporter
        ]
        
        result = self.run_test("Credential Rotation Variables", command, expected_vars)
        
        # Cleanup
        for var in ["CRED_ROTATION_PAYLOAD", "CRED_ROTATION_FORCE"]:
            if var in os.environ:
                del os.environ[var]
        
        return result
    
    def run_all_tests(self):
        """Run all tests"""
        self.log("🚀 Starting unified exporter test suite...")
        
        # Setup
        self.setup_test_environment()
        
        try:
            # Run tests
            tests = [
                self.test_basic_export,
                self.test_json_variables,
                self.test_api_input_simulation,
                self.test_script_generation,
                self.test_step_specific_variables,
                self.test_credential_rotation_variables
            ]
            
            passed = 0
            total = len(tests)
            
            for test_func in tests:
                if test_func():
                    passed += 1
            
            # Print results
            self.log(f"\n📊 Test Results: {passed}/{total} tests passed")
            
            # Print failed tests
            failed_tests = [r for r in self.test_results if r["status"] == "FAILED"]
            if failed_tests:
                self.log("\n❌ Failed Tests:")
                for test in failed_tests:
                    self.log(f"  - {test['test']}: {test.get('error', 'Unknown error')}")
            
            return passed == total
            
        finally:
            self.cleanup_test_environment()
    
    def print_detailed_results(self):
        """Print detailed test results"""
        print("\n📋 Detailed Test Results:")
        print("=" * 50)
        
        for result in self.test_results:
            print(f"\nTest: {result['test']}")
            print(f"Status: {result['status']}")
            if result.get('error'):
                print(f"Error: {result['error']}")
            if result.get('stdout'):
                print(f"Stdout: {result['stdout'][:200]}...")
            if result.get('stderr'):
                print(f"Stderr: {result['stderr'][:200]}...")


def main():
    """Main function"""
    tester = UnifiedExporterTester()
    
    try:
        success = tester.run_all_tests()
        tester.print_detailed_results()
        
        if success:
            print("\n🎉 All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
