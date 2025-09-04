#!/usr/bin/env python3
"""
Universal Export Variables Script
Exports pipeline variables, common configuration variables, and job-specific variables
"""

import os
import sys
import json


def log(message):
    """Log messages with prefix"""
    print(f"🔧 [export_vars] {message}")


def export_pipeline_variables(variables_json):
    """
    Export variables from JSON to environment.
    
    Args:
        variables_json (str): JSON string containing variables
        
    Returns:
        int: Number of variables exported
    """
    if not variables_json or variables_json.strip() in ['{}', 'null', '']:
        log("⚠️  No pipeline variables to export (empty or null JSON)")
        return 0
    
    try:
        # Parse JSON
        variables = json.loads(variables_json)
        
        if not isinstance(variables, dict):
            log("❌ ERROR: JSON is not a dictionary")
            return 0
            
        if not variables:
            log("⚠️  No variables found in JSON")
            return 0
            
    except json.JSONDecodeError as e:
        log(f"❌ ERROR: Invalid JSON format: {e}")
        return 0
    
    # Export variables
    exported_count = 0
    
    for key, value in variables.items():
        # Skip null or empty values
        if value is None or value == "" or value == "null":
            continue
            
        # Convert value to string and export
        value_str = str(value)
        os.environ[key] = value_str
        log(f"  export {key}=\"{value_str}\"")
        exported_count += 1
    
    log(f"✅ Successfully exported {exported_count} pipeline variables")
    return exported_count


def export_common_config():
    """Export common configuration variables"""
    log("Exporting common configuration variables...")
    
    # Get CI_PROJECT_DIR from environment
    ci_project_dir = os.getenv("CI_PROJECT_DIR")
    if not ci_project_dir:
        log("⚠️  CI_PROJECT_DIR not set, skipping common config export")
        return 0
    
    # Common configuration variables
    common_vars = {
        "INSTANCES_DIR": f"{ci_project_dir}/environments",
        "module_ansible_dir": "/module/ansible",
        "module_inventory": f"{ci_project_dir}/configuration/inventory.yaml",
        "module_ansible_cfg": "/module/ansible/ansible.cfg",
        "module_config_default": "/module/templates/defaults.yaml",
        "envgen_args": " -vvv",
        "envgen_debug": "true",
        "GIT_STRATEGY": "none",
        "COMMIT_ENV": "true"
    }
    
    # Export common variables
    for key, value in common_vars.items():
        os.environ[key] = value
        log(f"  export {key}=\"{value}\"")
    
    # Export existing CI/GitHub system variables (if they exist)
    system_vars = [
        "CI_PROJECT_DIR", "SECRET_KEY", "GITHUB_ACTIONS", "GITHUB_REPOSITORY",
        "GITHUB_REF_NAME", "GITHUB_USER_EMAIL", "GITHUB_USER_NAME", "GITHUB_TOKEN"
    ]
    
    for var in system_vars:
        if var in os.environ:
            log(f"  export {var} (already set)")
    
    log("✅ Common configuration variables exported")
    return len(common_vars)


def export_job_variables(matrix_environment):
    """
    Export job-specific variables for matrix environment.
    
    Args:
        matrix_environment (str): Environment name from matrix (e.g., "test-cluster/e01")
        
    Returns:
        int: Number of variables exported
    """
    if not matrix_environment:
        log("⚠️  No matrix environment provided, skipping job-specific variables")
        return 0
    
    log(f"Exporting job-specific variables for environment: {matrix_environment}")
    
    # Extract and export environment-specific variables
    job_vars = {
        "ENV_NAMES": matrix_environment,
        "CLUSTER_NAME": matrix_environment.split('/')[0] if '/' in matrix_environment else matrix_environment,
        "ENVIRONMENT_NAME": matrix_environment.split('/')[1].strip() if '/' in matrix_environment else matrix_environment,
    }
    
    # Set ENV_NAME and ENV_NAME_SHORT
    environment_name = job_vars["ENVIRONMENT_NAME"]
    job_vars["ENV_NAME"] = environment_name
    job_vars["ENV_NAME_SHORT"] = environment_name.split('/')[-1] if '/' in environment_name else environment_name
    
    # Export job variables
    for key, value in job_vars.items():
        os.environ[key] = value
        log(f"  export {key}=\"{value}\"")
    
    log("✅ Job-specific variables exported")
    return len(job_vars)


def main():
    """Main function"""
    # Get arguments
    if len(sys.argv) < 3:
        log("❌ ERROR: Missing required arguments")
        log("Usage: python export_variables.py '<variables_json>' '<matrix_environment>'")
        sys.exit(1)
    
    variables_json = sys.argv[1]
    matrix_environment = sys.argv[2]
    
    log("🚀 Starting variable export process...")
    
    # 1. Export pipeline variables from JSON
    pipeline_count = export_pipeline_variables(variables_json)
    
    # 2. Export common configuration variables
    common_count = export_common_config()
    
    # 3. Export job-specific variables (if matrix environment provided)
    job_count = export_job_variables(matrix_environment)
    
    total_count = pipeline_count + common_count + job_count
    log(f"🎉 Variable export completed successfully ({total_count} total variables)")


if __name__ == "__main__":
    main()
