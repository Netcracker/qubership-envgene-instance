#!/usr/bin/env python3
import json
import os
import re
import sys

import yaml


def sanitize_value(value):
    """Sanitize and convert value to appropriate type"""
    if isinstance(value, str):
        value = value.strip()
        # Handle JSON strings
        if value.startswith("{") and value.endswith("}"):
            try:
                json.loads(value)
                return value
            except:
                pass
        # Handle boolean strings
        if value.lower() in ["true", "false"]:
            return value.lower()
    return str(value)


def parse_api_input(api_input_string):
    """Parse API input string and extract variables"""
    variables = {}

    if not api_input_string or api_input_string.strip() == "":
        return variables

    # Try to parse as JSON first
    try:
        json_data = json.loads(api_input_string)
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                variables[key] = sanitize_value(value)
            return variables
    except json.JSONDecodeError:
        pass

    # Try to parse as YAML
    try:
        yaml_data = yaml.safe_load(api_input_string)
        if isinstance(yaml_data, dict):
            for key, value in yaml_data.items():
                variables[key] = sanitize_value(value)
            return variables
    except yaml.YAMLError:
        pass

    # Parse as key=value pairs (fallback)
    lines = api_input_string.split("\n")
    for line in lines:
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            # Remove quotes if present
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]
            variables[key] = sanitize_value(value)

    return variables


def validate_variable(key, value):
    """Validate variable based on known variable types"""
    boolean_vars = [
        "ENV_INVENTORY_INIT",
        "GENERATE_EFFECTIVE_SET",
        "ENV_TEMPLATE_TEST",
        "SD_DELTA",
        "ENV_BUILDER",
        "GET_PASSPORT",
        "CMDB_IMPORT",
    ]

    json_vars = ["SD_DATA", "ENV_SPECIFIC_PARAMETERS"]

    if key in boolean_vars:
        if isinstance(value, str) and value.lower() in ["true", "false"]:
            return value.lower()
        elif isinstance(value, bool):
            return "true" if value else "false"
        else:
            print(f"Warning: {key} should be boolean, got '{value}', keeping as string")
            return str(value)

    elif key in json_vars:
        if isinstance(value, str):
            try:
                json.loads(value)
                return value
            except json.JSONDecodeError:
                print(
                    f"Warning: {key} should be valid JSON, got '{value}', wrapping in quotes"
                )
                return json.dumps(value)
        else:
            return json.dumps(value)

    # For all other variables, return as string
    return str(value)


def main():
    print("🐍 Python script started")
    print("Environment variables:")
    for key, value in os.environ.items():
        if key.startswith("GITHUB_PIPELINE"):
            print(f"  {key}={value}")

    api_input = os.getenv("GITHUB_PIPELINE_API_INPUT", "")
    print(f"Retrieved GITHUB_PIPELINE_API_INPUT: '{api_input}'")
    print(f"Value type: {type(api_input)}")
    print(f"Is empty: {not api_input}")
    print(f"Is None: {api_input is None}")

    if not api_input:
        print("❌ No GITHUB_PIPELINE_API_INPUT provided, skipping API input processing")
        return

    print(f"✅ Processing GITHUB_PIPELINE_API_INPUT: {api_input}")
    print(f"Input length: {len(api_input)} characters")

    # Parse the API input string
    variables = parse_api_input(api_input)

    if not variables:
        print("No variables parsed from GITHUB_PIPELINE_API_INPUT")
        print("This could be due to invalid JSON/YAML format or empty input")
        return

    github_env_file = os.getenv("GITHUB_ENV")
    github_output_file = os.getenv("GITHUB_OUTPUT")

    if not github_env_file or not github_output_file:
        print("Error: GITHUB_ENV or GITHUB_OUTPUT variable is not set!")
        sys.exit(1)

    # Validate required variables
    if "ENV_NAMES" not in variables or not variables["ENV_NAMES"].strip():
        print("Error: ENV_NAMES is required but not provided in API input")
        print("Available variables:", list(variables.keys()))
        sys.exit(1)

    print("Parsed variables from API input:")
    with open(github_env_file, "a", encoding="utf-8") as env_file, open(
        github_output_file, "a", encoding="utf-8"
    ) as output_file:

        for key, value in variables.items():
            validated_value = validate_variable(key, value)
            print(f"  {key}={validated_value}")
            env_file.write(f"{key}={validated_value}\n")
            output_file.write(f"{key}={validated_value}\n")

    print(f"Successfully processed {len(variables)} variables from API input")


if __name__ == "__main__":
    main()
