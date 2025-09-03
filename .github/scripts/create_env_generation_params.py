#!/usr/bin/env python3
"""
Script to create ENV_GENERATION_PARAMS JSON from environment variables.
"""

import json
import os
import sys


def create_env_generation_params():
    """Create ENV_GENERATION_PARAMS JSON from environment variables."""
    
    # Get environment variables with defaults
    params = {
        "SD_SOURCE_TYPE": os.getenv("SD_SOURCE_TYPE", ""),
        "SD_VERSION": os.getenv("SD_VERSION", ""),
        "SD_DATA": os.getenv("SD_DATA", "{}"),
        "SD_DELTA": os.getenv("SD_DELTA", ""),
        "ENV_SPECIFIC_PARAMETERS": os.getenv("ENV_SPECIFIC_PARAMETERS", ""),
        "ENV_TEMPLATE_NAME": os.getenv("ENV_TEMPLATE_NAME", "")
    }
    
    print("Creating ENV_GENERATION_PARAMS:")
    for key, value in params.items():
        if value:
            print(f"  {key}: {value}")
        else:
            print(f"  {key}: (empty)")
    
    # Create JSON
    env_generation_params = json.dumps(params, separators=(',', ':'))
    print(f"Generated JSON: {env_generation_params}")
    
    # Write to GITHUB_ENV
    github_env_file = os.getenv("GITHUB_ENV")
    if not github_env_file:
        print("Error: GITHUB_ENV variable is not set!")
        sys.exit(1)
    
    with open(github_env_file, "a", encoding="utf-8") as f:
        f.write(f"ENV_GENERATION_PARAMS={env_generation_params}\n")
    
    print("✅ ENV_GENERATION_PARAMS written to GITHUB_ENV")


if __name__ == "__main__":
    create_env_generation_params()
