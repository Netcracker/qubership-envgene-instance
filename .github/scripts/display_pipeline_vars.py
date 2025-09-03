#!/usr/bin/env python3
"""
Dynamic pipeline variables display script.
Reads all variables from GITHUB_ENV and displays non-empty pipeline-related variables.
"""
import os
import sys


def get_pipeline_variables():
    """
    Read all variables from GITHUB_ENV file or environment variables.
    Returns a dictionary of non-empty pipeline variables.
    """
    variables = {}
    
    # First, try to read from GITHUB_ENV file
    github_env_file = os.getenv("GITHUB_ENV")
    if github_env_file:
        try:
            with open(github_env_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and "=" in line and not line.startswith("#"):
                        try:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Only include non-empty values
                            if value:
                                variables[key] = value
                        except ValueError:
                            print(f"⚠️  Warning: Skipping malformed line {line_num}: {line}")
                            continue
        except FileNotFoundError:
            print(f"⚠️  GITHUB_ENV file not found: {github_env_file}")
        except Exception as e:
            print(f"⚠️  Error reading GITHUB_ENV file: {e}")
    
    # If no variables from file, fall back to environment variables
    if not variables:
        print("📝 Reading from environment variables (GITHUB_ENV file not available)")
        
        # Get all environment variables
        for key, value in os.environ.items():
            if value and is_pipeline_variable(key):
                variables[key] = value
    
    return variables


def is_pipeline_variable(key):
    """
    Determine if a variable is pipeline-related based on its name.
    """
    # System variables to exclude
    system_vars = {
        'CI_COMMIT_REF_NAME', 'CI_PROJECT_DIR', 'SECRET_KEY', 
        'GITHUB_USER_EMAIL', 'GITHUB_USER_NAME', 'GITHUB_TOKEN',
        'ENVGENE_AGE_PUBLIC_KEY', 'ENVGENE_AGE_PRIVATE_KEY',
        'GITHUB_ENV', 'GITHUB_OUTPUT', 'GITHUB_WORKSPACE',
        'GITHUB_REPOSITORY', 'GITHUB_SHA', 'GITHUB_REF',
        'GITHUB_ACTIONS', 'RUNNER_OS', 'RUNNER_ARCH'
    }
    
    # Docker image variables
    docker_vars = {
        'DOCKER_IMAGE_PIPEGENE', 'DOCKER_IMAGE_ENVGENE', 
        'DOCKER_IMAGE_EFFECTIVE_SET_GENERATOR'
    }
    
    # Pipeline configuration variables (these we definitely want to show)
    pipeline_vars = {
        'DEPLOYMENT_TICKET_ID', 'ENV_NAMES', 'ENV_INVENTORY_INIT',
        'ENV_BUILDER', 'GENERATE_EFFECTIVE_SET', 'CMDB_IMPORT',
        'GET_PASSPORT', 'ENV_TEMPLATE_VERSION', 'ENV_TEMPLATE_TEST',
        'ENV_TEMPLATE_NAME', 'SD_DATA', 'SD_VERSION', 'SD_SOURCE_TYPE',
        'SD_DELTA', 'ENV_SPECIFIC_PARAMETERS', 'CRED_ROTATION_PAYLOAD',
        'CRED_ROTATION_FORCE', 'BG_STATE', 'ENV_GENERATION_PARAMS',
        'GITHUB_PIPELINE_API_INPUT'
    }
    
    # Include pipeline vars, docker vars, exclude system vars
    if key in system_vars:
        return False
    
    if key in pipeline_vars or key in docker_vars:
        return True
    
    # Include any other variables that might be custom pipeline variables
    # but exclude obvious system/CI variables
    if key.startswith(('GITHUB_', 'RUNNER_', 'CI_')) and key not in pipeline_vars:
        return False
    
    return True


def display_variables(show_docker=True, show_pipeline=True):
    """
    Display pipeline variables in organized sections.
    """
    variables = get_pipeline_variables()
    
    if not variables:
        print("No variables found in GITHUB_ENV")
        return
    
    # Separate variables into categories
    docker_vars = {}
    pipeline_vars = {}
    other_vars = {}
    
    for key, value in variables.items():
        if not is_pipeline_variable(key):
            continue
            
        if key.startswith('DOCKER_IMAGE_'):
            docker_vars[key] = value
        elif key in {
            'DEPLOYMENT_TICKET_ID', 'ENV_NAMES', 'ENV_INVENTORY_INIT',
            'ENV_BUILDER', 'GENERATE_EFFECTIVE_SET', 'CMDB_IMPORT',
            'GET_PASSPORT', 'ENV_TEMPLATE_VERSION', 'ENV_TEMPLATE_TEST',
            'ENV_TEMPLATE_NAME', 'SD_DATA', 'SD_VERSION', 'SD_SOURCE_TYPE',
            'SD_DELTA', 'ENV_SPECIFIC_PARAMETERS', 'CRED_ROTATION_PAYLOAD',
            'CRED_ROTATION_FORCE', 'BG_STATE', 'ENV_GENERATION_PARAMS',
            'GITHUB_PIPELINE_API_INPUT'
        }:
            pipeline_vars[key] = value
        else:
            other_vars[key] = value
    
    # Display Docker Images section
    if show_docker and docker_vars:
        print("=== Docker Images ===")
        for key in sorted(docker_vars.keys()):
            print(f"{key} = {docker_vars[key]}")
        print("")
    
    # Display Pipeline Configuration section
    if show_pipeline and pipeline_vars:
        print("=== Pipeline Configuration (Non-empty values only) ===")
        for key in sorted(pipeline_vars.keys()):
            print(f"{key} = {pipeline_vars[key]}")
        print("")
    
    # Display other variables if any
    if other_vars:
        print("=== Other Variables ===")
        for key in sorted(other_vars.keys()):
            print(f"{key} = {other_vars[key]}")
        print("")
    
    total_count = len(docker_vars) + len(pipeline_vars) + len(other_vars)
    
    if total_count == 0:
        print("ℹ️  No pipeline variables found to display")
        print("   This could mean:")
        print("   - Variables are not set yet")
        print("   - GITHUB_ENV file is empty or doesn't exist")
        print("   - All variables have empty values")
    else:
        print(f"📊 Total variables displayed: {total_count}")
        
        # Show source information
        github_env_file = os.getenv("GITHUB_ENV")
        if github_env_file and os.path.exists(github_env_file):
            print(f"📁 Source: GITHUB_ENV file ({github_env_file})")
        else:
            print("📁 Source: Environment variables")


def main():
    """
    Main function for command-line usage.
    """
    # Parse command line arguments
    show_docker = True
    show_pipeline = True
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--no-docker":
            show_docker = False
        elif sys.argv[1] == "--only-pipeline":
            show_docker = False
        elif sys.argv[1] == "--only-docker":
            show_pipeline = False
        elif sys.argv[1] == "--help":
            print("Usage: python display_pipeline_vars.py [--no-docker|--only-pipeline|--only-docker]")
            print("  --no-docker     : Don't show Docker image variables")
            print("  --only-pipeline : Show only pipeline configuration variables")
            print("  --only-docker   : Show only Docker image variables")
            return
    
    display_variables(show_docker=show_docker, show_pipeline=show_pipeline)


if __name__ == "__main__":
    main()
