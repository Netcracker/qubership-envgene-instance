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
        print(f"🔍 Parsed JSON data: {json_data}")
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                variables[key] = sanitize_value(value)
                if key == "ENV_NAMES":
                    print(f"🔍 ENV_NAMES from JSON: '{value}' -> '{variables[key]}'")
            return variables
    except json.JSONDecodeError as e:
        print(f"🔍 JSON parsing failed: {e}")
        pass

    # Try to parse as YAML with better error handling
    try:
        yaml_data = yaml.safe_load(api_input_string)
        print(f"🔍 Parsed YAML data: {yaml_data}")
        if isinstance(yaml_data, dict):
            # Check if we have a split ENV_NAMES issue
            if 'ENV_NAMES' in yaml_data and any(key.startswith('test-cluster/') for key in yaml_data.keys() if key != 'ENV_NAMES'):
                print("🔍 Detected split ENV_NAMES issue, attempting to reconstruct...")
                # Find all keys that look like environment names
                env_keys = [key for key in yaml_data.keys() if key.startswith('test-cluster/')]
                if env_keys:
                    # Reconstruct ENV_NAMES from the original value and additional keys
                    original_env_names = yaml_data.get('ENV_NAMES', '')
                    additional_envs = [key for key in env_keys if yaml_data.get(key) is None]
                    if additional_envs:
                        reconstructed_env_names = original_env_names + ',' + ','.join(additional_envs)
                        print(f"🔍 Reconstructed ENV_NAMES: '{reconstructed_env_names}'")
                        yaml_data['ENV_NAMES'] = reconstructed_env_names
                        # Remove the split keys
                        for key in env_keys:
                            if yaml_data.get(key) is None:
                                del yaml_data[key]
            
            for key, value in yaml_data.items():
                variables[key] = sanitize_value(value)
                if key == "ENV_NAMES":
                    print(f"🔍 ENV_NAMES from YAML: '{value}' -> '{variables[key]}'")
            return variables
    except yaml.YAMLError as e:
        print(f"🔍 YAML parsing failed: {e}")
        pass

    # If both JSON and YAML failed, try to fix common issues and retry
    print("🔍 Both JSON and YAML parsing failed, attempting to fix common issues...")
    
    # Try to fix unquoted strings with commas in YAML-like format
    fixed_input = api_input_string
    if "ENV_NAMES:" in fixed_input and "," in fixed_input:
        # Look for ENV_NAMES: value, pattern and quote the value
        import re
        pattern = r'ENV_NAMES:\s*([^,\s]+(?:,[^,\s]+)*)'
        match = re.search(pattern, fixed_input)
        if match:
            env_names_value = match.group(1)
            print(f"🔍 Found ENV_NAMES value: '{env_names_value}'")
            # Replace the unquoted value with quoted value
            fixed_input = re.sub(pattern, f'ENV_NAMES: "{env_names_value}"', fixed_input)
            print(f"🔍 Fixed input: {fixed_input}")
            
            # Try parsing the fixed input as YAML
            try:
                yaml_data = yaml.safe_load(fixed_input)
                print(f"🔍 Parsed fixed YAML data: {yaml_data}")
                if isinstance(yaml_data, dict):
                    for key, value in yaml_data.items():
                        variables[key] = sanitize_value(value)
                        if key == "ENV_NAMES":
                            print(f"🔍 ENV_NAMES from fixed YAML: '{value}' -> '{variables[key]}'")
                    return variables
            except yaml.YAMLError as e:
                print(f"🔍 Fixed YAML parsing also failed: {e}")
                pass

    # Parse as key=value pairs (fallback)
    print("🔍 Falling back to key=value parsing...")
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
            if key == "ENV_NAMES":
                print(f"🔍 ENV_NAMES from key=value: '{value}' -> '{variables[key]}'")

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
        
        # Try to extract ENV_NAMES from the raw input string as a last resort
        print("🔍 Attempting to extract ENV_NAMES from raw input...")
        if "ENV_NAMES" in api_input:
            # Look for ENV_NAMES in the raw string
            import re
            patterns = [
                r'ENV_NAMES["\s]*:\s*["\']?([^"\',\s]+(?:,[^"\',\s]+)*)["\']?',
                r'ENV_NAMES["\s]*:\s*([^,\s]+(?:,[^,\s]+)*)',
            ]
            for pattern in patterns:
                match = re.search(pattern, api_input)
                if match:
                    env_names_value = match.group(1)
                    print(f"🔍 Extracted ENV_NAMES from raw input: '{env_names_value}'")
                    variables["ENV_NAMES"] = env_names_value
                    break
            else:
                print("🔍 Could not extract ENV_NAMES from raw input")
                print("❌ ERROR: ENV_NAMES is required for API mode but could not be found!")
                print("Please ensure your API input contains ENV_NAMES with valid environment names.")
                print("Example: {\"ENV_NAMES\": \"test-cluster/e01,test-cluster/e02\", ...}")
                sys.exit(1)
        else:
            print("❌ ERROR: ENV_NAMES is required for API mode but not found in input!")
            print("Please ensure your API input contains ENV_NAMES with valid environment names.")
            print("Example: {\"ENV_NAMES\": \"test-cluster/e01,test-cluster/e02\", ...}")
            sys.exit(1)
    else:
        # Validate that ENV_NAMES contains all expected environments
        env_names = variables["ENV_NAMES"]
        print(f"🔍 Validating ENV_NAMES: '{env_names}'")
        
        # Check if we're missing any environments that were in the original input
        if "test-cluster/e01" in api_input and "test-cluster/e02" in api_input:
            expected_envs = ["test-cluster/e01", "test-cluster/e02"]
            current_envs = [env.strip() for env in env_names.split(",")]
            missing_envs = [env for env in expected_envs if env not in current_envs]
            
            if missing_envs:
                print(f"🔍 Missing environments in ENV_NAMES: {missing_envs}")
                print("🔍 Attempting to add missing environments...")
                for missing_env in missing_envs:
                    if missing_env not in env_names:
                        env_names = env_names + "," + missing_env
                        print(f"🔍 Added missing environment: {missing_env}")
                
                variables["ENV_NAMES"] = env_names
                print(f"🔍 Updated ENV_NAMES: '{env_names}'")
        
        # Additional validation for ENV_NAMES format
        if env_names:
            envs = [env.strip() for env in env_names.split(",") if env.strip()]
            if not envs:
                print("❌ ERROR: ENV_NAMES contains no valid environment names!")
                print(f"Raw ENV_NAMES value: '{env_names}'")
                sys.exit(1)
            
            # Validate each environment name format
            for env in envs:
                if not env or env == "":
                    print(f"❌ ERROR: Empty environment name found in ENV_NAMES: '{env_names}'")
                    sys.exit(1)
                if "/" not in env:
                    print(f"⚠️  WARNING: Environment name '{env}' doesn't contain '/' - may be invalid")
            
            print(f"✅ Validated {len(envs)} environment(s): {envs}")

    # Validate other important variables for API mode
    api_important_vars = ["DEPLOYMENT_TICKET_ID", "ENV_TEMPLATE_VERSION"]
    for var in api_important_vars:
        if var not in variables or not variables[var].strip():
            print(f"⚠️  WARNING: {var} is recommended for API mode but is empty or missing")
        else:
            print(f"✅ {var} is provided: '{variables[var]}'")

    print("Parsed variables from API input:")
    with open(github_env_file, "a", encoding="utf-8") as env_file, open(
        github_output_file, "a", encoding="utf-8"
    ) as output_file:

        for key, value in variables.items():
            validated_value = validate_variable(key, value)
            print(f"  {key}={validated_value}")
            if key == "ENV_NAMES":
                print(f"🔍 ENV_NAMES from API input: '{validated_value}'")
                print(f"🔍 ENV_NAMES length: {len(validated_value)}")
                print(f"🔍 ENV_NAMES contains comma: {',' in validated_value}")
                # Split and show individual environments
                envs = [env.strip() for env in validated_value.split(",")]
                print(f"🔍 Individual environments: {envs}")
            env_file.write(f"{key}={validated_value}\n")
            output_file.write(f"{key}={validated_value}\n")

    print(f"Successfully processed {len(variables)} variables from API input")


if __name__ == "__main__":
    main()
