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
                if key == "ENV_NAMES":
                    print(f"🔍 ENV_NAMES from YAML: '{value}' -> '{variables[key]}'")
                elif key == "CRED_ROTATION_PAYLOAD":
                    print(f"🔍 CRED_ROTATION_PAYLOAD from YAML: '{value}' -> '{variables[key]}'")
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
            
            # Remove outer quotes if the entire value is quoted
            if ((value.startswith('"') and value.endswith('"')) or 
                (value.startswith("'") and value.endswith("'"))):
                # Check if it's a JSON value that shouldn't have outer quotes removed
                inner_value = value[1:-1]
                if key in ["CRED_ROTATION_PAYLOAD", "SD_DATA", "ENV_SPECIFIC_PARAMETERS", "BG_STATE"]:
                    # For JSON variables, try to parse the inner value first
                    try:
                        json.loads(inner_value)
                        value = inner_value  # Remove outer quotes for JSON
                        print(f"🔍 Removed outer quotes from {key}: {value}")
                    except json.JSONDecodeError:
                        # Keep outer quotes if inner value is not valid JSON
                        pass
                else:
                    # For non-JSON variables, always remove outer quotes
                    value = inner_value
            
            # Special handling for JSON variables
            if key in ["CRED_ROTATION_PAYLOAD", "SD_DATA", "ENV_SPECIFIC_PARAMETERS", "BG_STATE"]:
                print(f"🔍 Processing JSON variable: {key}")
                
                # Handle different escaping patterns
                processed_value = value
                
                # First, try to unescape double-escaped quotes
                if '\\\"' in processed_value:
                    processed_value = processed_value.replace('\\\"', '"')
                    print(f"🔍 Unescaped double quotes: {processed_value}")
                
                # Handle mixed quotes - if we have both \" and " in the string
                # This might be a case where some quotes are escaped and others aren't
                if '\"' in processed_value and '"' in processed_value:
                    print(f"🔍 Detected mixed quote escaping, attempting to normalize...")
                    # Try to fix inconsistent escaping
                    # Replace \" with " except when it's already inside a quoted string
                    import re
                    # This regex tries to handle the complex case of mixed escaping
                    # It's a heuristic approach
                    if processed_value.count('\"') > processed_value.count('"'):
                        # More escaped quotes than regular ones, probably over-escaped
                        processed_value = processed_value.replace('\"', '"')
                        print(f"🔍 Normalized escaping: {processed_value}")
                
                # Try to parse as JSON
                try:
                    json.loads(processed_value)
                    print(f"🔍 {key} is valid JSON after processing")
                    variables[key] = processed_value
                except json.JSONDecodeError as e:
                    print(f"🔍 {key} is not valid JSON after processing: {e}")
                    # Try original value
                    try:
                        json.loads(value)
                        print(f"🔍 {key} is valid JSON (original)")
                        variables[key] = value
                    except json.JSONDecodeError:
                        print(f"🔍 {key} is not valid JSON, keeping as string")
                        variables[key] = value
            else:
                # Remove quotes if present for non-JSON variables
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]
                variables[key] = sanitize_value(value)
            
            if key == "ENV_NAMES":
                print(f"🔍 ENV_NAMES from key=value: '{value}' -> '{variables[key]}'")
            elif key == "CRED_ROTATION_PAYLOAD":
                print(f"🔍 CRED_ROTATION_PAYLOAD from key=value: '{value}' -> '{variables[key]}'")

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

    json_vars = ["SD_DATA", "ENV_SPECIFIC_PARAMETERS", "CRED_ROTATION_PAYLOAD", "BG_STATE"]

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

    # Validate other important variables for API mode
    # Check if they're provided either in API input or as workflow dispatch inputs
    api_important_vars = ["DEPLOYMENT_TICKET_ID", "ENV_TEMPLATE_VERSION"]
    for var in api_important_vars:
        api_value = variables.get(var, "").strip()
        env_value = os.getenv(var, "").strip()
        
        if not api_value and not env_value:
            print(f"⚠️  WARNING: {var} is recommended for API mode but is empty or missing")
        elif api_value:
            print(f"✅ {var} is provided via API input: '{api_value}'")
        elif env_value:
            print(f"✅ {var} is provided via workflow dispatch: '{env_value}'")

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
