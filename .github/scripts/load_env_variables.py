#!/usr/bin/env python3
import sys
import yaml
import json
import os


def getenv_and_log(key, default=""):
    value = os.getenv(key, default)
    print(f"{key}: {value}")
    return value


def sanitize_json(value):
    try:
        json_object = json.loads(value)
        return json.dumps(json_object)
    except (json.JSONDecodeError, TypeError):
        raise ValueError(f"Invalid JSON provided: {value}")


def convert_to_github_env(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str) and value.lower() in ["true", "false"]:
        return value.lower()
    return value


def validate_boolean(value, key):
    if isinstance(value, bool) or (isinstance(value, str) and value.lower() in ["true", "false"]):
        return convert_to_github_env(value)
    raise ValueError(f"{key} should be a boolean (true/false). Got: {value}")


def validate_json(value, key):
    try:
        if isinstance(value, str):
            value = value.strip().replace('\n', ' ')
        parsed_json = json.loads(value)
        return json.dumps(parsed_json)
    except (json.JSONDecodeError, TypeError):
        raise ValueError(f"{key} must be a valid JSON object")


def validate_string(value, key):
    if isinstance(value, str):
        return value
    raise ValueError(f"{key} must be a string. Got {type(value).__name__}")


def main():
    if len(sys.argv) < 2:
        print("Usage: load_env_params.py <yaml_config_file>")
        sys.exit(1)

    config_file = sys.argv[1]

    with open(config_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}

    github_env_file = os.getenv('GITHUB_ENV')
    github_output_file = os.getenv('GITHUB_OUTPUT')

    if not github_env_file or not github_output_file:
        print("Error: GITHUB_ENV or GITHUB_OUTPUT variable is not set!")
        sys.exit(1)

    # Default values for all variables
    default_values = {
        "ENV_INVENTORY_INIT": "false",
        "GENERATE_EFFECTIVE_SET": "false",
        "ENV_TEMPLATE_TEST": "false",
        "ENV_TEMPLATE_NAME": "",
        "SD_DATA": "{}",
        "SD_VERSION": "",
        "SD_SOURCE_TYPE": "",
        "SD_DELTA": "false",
        "ENV_SPECIFIC_PARAMETERS": "{}",
    }

    validators = {
        # Variables from pipeline_vars.yaml only
        "ENV_INVENTORY_INIT": validate_boolean,
        "GENERATE_EFFECTIVE_SET": validate_boolean,
        "ENV_TEMPLATE_TEST": validate_boolean,
        "ENV_TEMPLATE_NAME": validate_string,
        "SD_DATA": validate_json,
        "SD_VERSION": validate_string,
        "SD_SOURCE_TYPE": validate_string,
        "SD_DELTA": validate_boolean,
        "ENV_SPECIFIC_PARAMETERS": validate_json,
    }

    validated_data = {}

    for key, validator in validators.items():
        # Use value from file if exists, otherwise use default
        raw_value = data.get(key, default_values[key])

        try:
            if validator == validate_boolean:
                if isinstance(raw_value, bool):
                    validated_data[key] = convert_to_github_env(raw_value)
                elif isinstance(raw_value, str) and raw_value.lower() in ["true", "false"]:
                    validated_data[key] = raw_value.lower()
                else:
                    print(f"Warning: {key} has invalid value '{raw_value}', using default '{default_values[key]}'")
                    validated_data[key] = default_values[key]
            elif validator == validate_json:
                if not raw_value:
                    validated_data[key] = "{}"
                else:
                    validated_data[key] = validate_json(raw_value, key)
            else:  # string
                validated_data[key] = validate_string(raw_value, key)
        except ValueError as e:
            print(f"Warning: {e}, using default value '{default_values[key]}'")
            validated_data[key] = default_values[key]

    with open(github_env_file, 'a', encoding='utf-8') as env_file, \
            open(github_output_file, 'a', encoding='utf-8') as output_file:

        for key, value in validated_data.items():
            env_file.write(f"{key}={convert_to_github_env(value)}\n")
            output_file.write(f"{key}={convert_to_github_env(value)}\n")


if __name__ == "__main__":
    main()