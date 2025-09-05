#!/usr/bin/env python3
"""
Demo script for unified_variable_exporter.py
============================================

This script demonstrates how to use the unified variable exporter.
"""

import os
import sys
import json
from pathlib import Path


def demo_basic_usage():
    """Demonstrate basic usage of the unified exporter"""
    print("🎯 Demo: Basic Usage")
    print("=" * 40)
    
    # Import the exporter
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from unified_variable_exporter import UnifiedVariableExporter
    
    # Create exporter instance
    exporter = UnifiedVariableExporter(
        step_name="generate_inventory",
        matrix_environment="test-cluster/e01"
    )
    
    # Export variables
    result = exporter.export_all_variables()
    
    print(f"✅ Exported {result['total_exported']} variables")
    print(f"Step: {result['step_name']}")
    print(f"Matrix Environment: {result['matrix_environment']}")
    
    # Show some key variables
    key_vars = ['CLUSTER_NAME', 'ENVIRONMENT_NAME', 'ENV_NAME', 'FULL_ENV']
    print("\nKey Variables:")
    for var in key_vars:
        if var in os.environ:
            print(f"  {var}: {os.environ[var]}")


def demo_with_json_variables():
    """Demonstrate usage with JSON variables"""
    print("\n🎯 Demo: With JSON Variables")
    print("=" * 40)
    
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from unified_variable_exporter import UnifiedVariableExporter
    
    # JSON variables to inject
    json_vars = {
        "MY_CUSTOM_VAR": "custom_value",
        "ANOTHER_VAR": "another_value",
        "JSON_CONFIG": '{"setting": "value"}'
    }
    
    # Create exporter with JSON variables
    exporter = UnifiedVariableExporter(
        step_name="env_build",
        matrix_environment="test-cluster/e01",
        variables_json=json.dumps(json_vars)
    )
    
    # Export variables
    result = exporter.export_all_variables()
    
    print(f"✅ Exported {result['total_exported']} variables")
    
    # Show custom variables
    print("\nCustom Variables:")
    for var in json_vars.keys():
        if var in os.environ:
            print(f"  {var}: {os.environ[var]}")


def demo_api_input_simulation():
    """Demonstrate API input simulation"""
    print("\n🎯 Demo: API Input Simulation")
    print("=" * 40)
    
    # Simulate API input
    api_input = """
API_VAR_1=api_value_1
API_VAR_2=api_value_2
JSON_API_VAR={"key": "value"}
"""
    
    # Set environment variable
    os.environ["GITHUB_PIPELINE_API_INPUT"] = api_input
    
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from unified_variable_exporter import UnifiedVariableExporter
    
    # Create exporter
    exporter = UnifiedVariableExporter(
        step_name="credential_rotation",
        matrix_environment="test-cluster/e01"
    )
    
    # Export variables
    result = exporter.export_all_variables()
    
    print(f"✅ Exported {result['total_exported']} variables")
    
    # Show API variables
    print("\nAPI Variables:")
    api_vars = ['API_VAR_1', 'API_VAR_2', 'JSON_API_VAR']
    for var in api_vars:
        if var in os.environ:
            print(f"  {var}: {os.environ[var]}")
    
    # Cleanup
    if "GITHUB_PIPELINE_API_INPUT" in os.environ:
        del os.environ["GITHUB_PIPELINE_API_INPUT"]


def demo_script_generation():
    """Demonstrate shell script generation"""
    print("\n🎯 Demo: Script Generation")
    print("=" * 40)
    
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from unified_variable_exporter import UnifiedVariableExporter
    
    # Create exporter
    exporter = UnifiedVariableExporter(
        step_name="git_commit",
        matrix_environment="test-cluster/e01"
    )
    
    # Export variables
    result = exporter.export_all_variables()
    
    # Generate shell script
    script_content = exporter.generate_export_script("demo_export.sh")
    
    print(f"✅ Generated export script with {len(result['exported_vars'])} variables")
    print("\nScript preview (first 10 lines):")
    print("-" * 30)
    
    lines = script_content.split('\n')
    for i, line in enumerate(lines[:10]):
        print(f"{i+1:2d}: {line}")
    
    if len(lines) > 10:
        print(f"... and {len(lines) - 10} more lines")


def demo_step_comparison():
    """Demonstrate differences between steps"""
    print("\n🎯 Demo: Step Comparison")
    print("=" * 40)
    
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from unified_variable_exporter import UnifiedVariableExporter
    
    steps = ["generate_inventory", "credential_rotation", "env_build", "generate_effective_set", "git_commit"]
    
    for step in steps:
        print(f"\n--- {step.upper()} ---")
        
        exporter = UnifiedVariableExporter(
            step_name=step,
            matrix_environment="test-cluster/e01"
        )
        
        result = exporter.export_all_variables()
        
        # Show step-specific variables
        step_specific = []
        for var in result['exported_vars']:
            if var.startswith(('module_', 'envgen_', 'CRED_ROTATION_', 'PUBLIC_AGE')):
                step_specific.append(var)
        
        if step_specific:
            print(f"Step-specific variables: {', '.join(step_specific)}")
        else:
            print("No step-specific variables")


def main():
    """Main demo function"""
    print("🚀 Unified Variable Exporter Demo")
    print("=" * 50)
    
    try:
        # Set up basic environment
        os.environ["CI_PROJECT_DIR"] = os.getcwd()
        
        # Run demos
        demo_basic_usage()
        demo_with_json_variables()
        demo_api_input_simulation()
        demo_script_generation()
        demo_step_comparison()
        
        print("\n🎉 Demo completed successfully!")
        print("\nTo run the actual exporter:")
        print("python .github/scripts/unified_variable_exporter.py --step generate_inventory --matrix-env test-cluster/e01 --list-vars")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
