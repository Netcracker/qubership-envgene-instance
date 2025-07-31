#!/usr/bin/env python3

import os

import yaml


def test_env_builder():
    """Test ENV_BUILDER value processing"""

    print("=== Testing ENV_BUILDER Processing ===")

    # Simulate the workflow environment
    os.environ["ENV_BUILDER"] = "false"  # Simulate workflow_dispatch input

    print(f"Environment ENV_BUILDER: {os.getenv('ENV_BUILDER')}")

    # Load pipeline_vars.yaml
    with open(".github/pipeline_vars.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    print(f"File data: {data}")

    # Simulate load_env_variables.py logic
    default_values = {
        "ENV_BUILDER": "true",
    }

    # Priority: 1. Environment variable, 2. File value, 3. Default
    env_value = os.getenv("ENV_BUILDER")
    if env_value is not None:
        raw_value = env_value
        print(f"Using environment value for ENV_BUILDER: {raw_value}")
    else:
        raw_value = data.get("ENV_BUILDER", default_values["ENV_BUILDER"])
        print(
            f"Using {'file' if 'ENV_BUILDER' in data else 'default'} value for ENV_BUILDER: {raw_value}"
        )

    # Validate boolean
    if isinstance(raw_value, str) and raw_value.lower() in ["true", "false"]:
        final_value = raw_value.lower()
    else:
        print(
            f"Warning: ENV_BUILDER has invalid value '{raw_value}', using default 'true'"
        )
        final_value = default_values["ENV_BUILDER"]

    print(f"Final ENV_BUILDER value: {final_value}")
    print(f"Type: {type(final_value)}")

    # Test condition
    condition = final_value == "true"
    print(f"Condition 'ENV_BUILDER == true': {condition}")

    return final_value


if __name__ == "__main__":
    test_env_builder()
