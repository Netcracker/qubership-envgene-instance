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

    # Try to parse as YAML with better error handling
    try:
        yaml_data = yaml.safe_load(api_input_string)
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
            
            # Special handling for CRED_ROTATION_PAYLOAD
            if 'CRED_ROTATION_PAYLOAD' in yaml_data:
                cred_payload = yaml_data['CRED_ROTATION_PAYLOAD']
                print(f"🔍 Found CRED_ROTATION_PAYLOAD: {cred_payload}")
                
                # Check if it's a malformed JSON (missing quotes)
                if isinstance(cred_payload, str) and cred_payload.startswith('{') and 'rotation_items:' in cred_payload:
                    print("🔍 Detected malformed CRED_ROTATION_PAYLOAD, attempting to fix...")
                    # Try to fix the JSON format by adding quotes
                    try:
                        # Replace unquoted keys with quoted keys
                        import re
                        # Pattern to match unquoted keys: key:value
                        pattern = r'(\w+):([^,}]+)'
                        fixed_payload = re.sub(pattern, r'"\1":"\2"', cred_payload)
                        print(f"🔍 Fixed CRED_ROTATION_PAYLOAD: {fixed_payload}")
                        
                        # Validate the fixed JSON
                        json.loads(fixed_payload)
                        yaml_data['CRED_ROTATION_PAYLOAD'] = fixed_payload
                        print("✅ Successfully fixed CRED_ROTATION_PAYLOAD")
                    except Exception as e:
                        print(f"⚠️  Warning: Could not fix CRED_ROTATION_PAYLOAD: {e}")
                        # Keep original value, will be handled by validation later
            
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
            # Pre-process line to handle spaces around = sign
            if " = " in line:
                line = line.replace(" = ", "=")
            # Handle cases where there might be spaces around =
            # Find the first = that's not inside quotes
            eq_pos = -1
            in_quotes = False
            quote_char = None
            
            for i, char in enumerate(line):
                if char in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
                    if not in_quotes:
                        in_quotes = True
                        quote_char = char
                    elif char == quote_char:
                        in_quotes = False
                        quote_char = None
                elif char == '=' and not in_quotes:
                    eq_pos = i
                    break
            
            if eq_pos == -1:
                # Fallback to simple split if no unquoted = found
                if "=" in line:
                    key, value = line.split("=", 1)
                else:
                    continue
            else:
                key = line[:eq_pos]
                value = line[eq_pos + 1:]
            
            key = key.strip()
            value = value.strip()
            
            # Remove outer quotes if present - all variables are treated as strings
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

    if key in boolean_vars:
        if isinstance(value, str) and value.lower() in ["true", "false"]:
            return value.lower()
        elif isinstance(value, bool):
            return "true" if value else "false"
        else:
            print(f"Warning: {key} should be boolean, got '{value}', keeping as string")
            return str(value)

    # For all other variables (including JSON strings), return as string
    # No need to validate JSON format - they are stored as strings
    return str(value)


def main():
    api_input = os.getenv("GITHUB_PIPELINE_API_INPUT", "")

    if not api_input:
        print("❌ No GITHUB_PIPELINE_API_INPUT provided, skipping API input processing")
        return

    print(f"✅ Processing GITHUB_PIPELINE_API_INPUT ({len(api_input)} chars)")

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

    with open(github_env_file, "a", encoding="utf-8") as env_file, open(
        github_output_file, "a", encoding="utf-8"
    ) as output_file:

        for key, value in variables.items():
            validated_value = validate_variable(key, value)
            env_file.write(f"{key}={validated_value}\n")
            output_file.write(f"{key}={validated_value}\n")

    print(f"✅ Processed {len(variables)} variables from API input")


if __name__ == "__main__":
    main()
