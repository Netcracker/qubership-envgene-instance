#!/usr/bin/env python3
import json
import os
import sys

import yaml


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
    if isinstance(value, bool) or (
        isinstance(value, str) and value.lower() in ["true", "false"]
    ):
        return convert_to_github_env(value)
    raise ValueError(f"{key} should be a boolean (true/false). Got: {value}")


def validate_json(value, key):
    try:
        if isinstance(value, str):
            value = value.strip().replace("\n", " ")
        parsed_json = json.loads(value)
        return json.dumps(parsed_json)
    except (json.JSONDecodeError, TypeError):
        raise ValueError(f"{key} must be a valid JSON object")


def validate_string(value, key):
    if isinstance(value, str):
        return value
    raise ValueError(f"{key} must be a string. Got {type(value).__name__}")


def validate_cred_rotation_payload(value, key):
    """
    Validates CRED_ROTATION_PAYLOAD structure according to the specified format:
    {
      "rotation_items": [
        {
          "namespace": "<namespace>",
          "application": "<application-name>",  # optional
          "context": "enum[`pipeline`,`deployment`, `runtime`]",
          "parameter_key": "<parameter-key>",
          "parameter_value": "<new-parameter-value>"
        }
      ]
    }
    """
    try:
        if isinstance(value, str):
            value = value.strip().replace("\n", " ")
            if not value:  # Empty string is valid (default empty payload)
                return "{}"
            parsed_json = json.loads(value)
        else:
            parsed_json = value

        # If empty object, return as is
        if not parsed_json:
            return "{}"

        # Validate structure
        if not isinstance(parsed_json, dict):
            raise ValueError(f"{key} must be a JSON object")

        if "rotation_items" not in parsed_json:
            raise ValueError(f"{key} must contain 'rotation_items' field")

        if not isinstance(parsed_json["rotation_items"], list):
            raise ValueError(f"{key}.rotation_items must be an array")

        # Validate each rotation item
        valid_contexts = ["pipeline", "deployment", "runtime"]
        for i, item in enumerate(parsed_json["rotation_items"]):
            if not isinstance(item, dict):
                raise ValueError(f"{key}.rotation_items[{i}] must be an object")

            # Required fields
            required_fields = [
                "namespace",
                "context",
                "parameter_key",
                "parameter_value",
            ]
            for field in required_fields:
                if field not in item:
                    raise ValueError(
                        f"{key}.rotation_items[{i}] must contain '{field}' field"
                    )
                if not isinstance(item[field], str):
                    raise ValueError(
                        f"{key}.rotation_items[{i}].{field} must be a string"
                    )

            # Optional field - application
            if "application" in item and not isinstance(item["application"], str):
                raise ValueError(
                    f"{key}.rotation_items[{i}].application must be a string if provided"
                )

            # Validate context enum
            if item["context"] not in valid_contexts:
                raise ValueError(
                    f"{key}.rotation_items[{i}].context must be one of: {valid_contexts}"
                )

        # Return JSON encoded as base64 to avoid quote loss
        json_str = json.dumps(parsed_json, separators=(",", ":"))
        import base64

        encoded_json = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
        return encoded_json
    except (json.JSONDecodeError, TypeError) as e:
        raise ValueError(f"{key} must be a valid JSON object: {str(e)}")


def main():
    if len(sys.argv) < 2:
        print("Usage: load_env_params.py <yaml_config_file>")
        sys.exit(1)

    config_file = sys.argv[1]

    with open(config_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    github_env_file = os.getenv("GITHUB_ENV")
    github_output_file = os.getenv("GITHUB_OUTPUT")

    if not github_env_file or not github_output_file:
        print("Error: GITHUB_ENV or GITHUB_OUTPUT variable is not set!")
        sys.exit(1)

    # Load existing environment variables from GITHUB_ENV file
    if os.path.exists(github_env_file):
        with open(github_env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value
                    print(f"Loaded environment variable: {key}={value}")

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
        "ENV_BUILDER": "true",
        "GET_PASSPORT": "false",
        "CMDB_IMPORT": "false",
        "DEPLOYMENT_TICKET_ID": "",
        "ENV_TEMPLATE_VERSION": "",
        "CRED_ROTATION_PAYLOAD": "{}",
        "CRED_ROTATION_FORCE": "false",
    }

    validators = {
        # Variables from pipeline_vars.yaml
        "ENV_INVENTORY_INIT": validate_boolean,
        "GENERATE_EFFECTIVE_SET": validate_boolean,
        "ENV_TEMPLATE_TEST": validate_boolean,
        "ENV_TEMPLATE_NAME": validate_string,
        "SD_DATA": validate_json,
        "SD_VERSION": validate_string,
        "SD_SOURCE_TYPE": validate_string,
        "SD_DELTA": validate_boolean,
        "ENV_SPECIFIC_PARAMETERS": validate_json,
        # Additional variables from workflow inputs
        "ENV_BUILDER": validate_boolean,
        "GET_PASSPORT": validate_boolean,
        "CMDB_IMPORT": validate_boolean,
        "DEPLOYMENT_TICKET_ID": validate_string,
        "ENV_TEMPLATE_VERSION": validate_string,
        # New credential rotation variables
        "CRED_ROTATION_PAYLOAD": validate_cred_rotation_payload,
        "CRED_ROTATION_FORCE": validate_boolean,
    }

    validated_data = {}

    for key, validator in validators.items():
        # Priority: 1. Environment variable (from API input), 2. File value, 3. Default
        env_value = os.getenv(key)
        # Debug only for specific variables
        if key in ["ENV_BUILDER", "GET_PASSPORT", "CMDB_IMPORT"]:
            print(
                f"DEBUG: Checking {key}, env_value={env_value}, env_value is None={env_value is None}"
            )
        if env_value is not None:
            raw_value = env_value
            print(f"Using environment value for {key}: {raw_value}")
        else:
            raw_value = data.get(key, default_values[key])
            print(
                f"Using {'file' if key in data else 'default'} value for {key}: {raw_value}"
            )

        try:
            if validator == validate_boolean:
                if isinstance(raw_value, bool):
                    validated_data[key] = convert_to_github_env(raw_value)
                elif isinstance(raw_value, str) and raw_value.lower() in [
                    "true",
                    "false",
                ]:
                    validated_data[key] = raw_value.lower()
                else:
                    print(
                        f"Warning: {key} has invalid value '{raw_value}', using default '{default_values[key]}'"
                    )
                    validated_data[key] = default_values[key]
            elif validator == validate_json:
                if not raw_value:
                    validated_data[key] = "{}"
                else:
                    validated_data[key] = validate_json(raw_value, key)
            elif validator == validate_cred_rotation_payload:
                validated_data[key] = validate_cred_rotation_payload(raw_value, key)
            else:  # string
                validated_data[key] = validate_string(raw_value, key)
        except ValueError as e:
            print(f"Warning: {e}, using default value '{default_values[key]}'")
            validated_data[key] = default_values[key]

    with open(github_env_file, "a", encoding="utf-8") as env_file, open(
        github_output_file, "a", encoding="utf-8"
    ) as output_file:

        for key, value in validated_data.items():
            # Always write to files to ensure consistency
            converted_value = convert_to_github_env(value)
            env_file.write(f"{key}={converted_value}\n")
            output_file.write(f"{key}={converted_value}\n")
            if os.getenv(key) is not None:
                print(
                    f"Overwriting {key} from environment with validated value: {converted_value}"
                )
            else:
                print(f"Setting {key} to: {converted_value}")


if __name__ == "__main__":
    main()
