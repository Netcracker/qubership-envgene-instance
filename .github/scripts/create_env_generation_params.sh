#!/bin/bash
# Empty shell script for creating environment generation parameters

# Array of possible environment variables
possible_vars=(
    "SD_SOURCE_TYPE"
    "SD_VERSION"
    "SD_DATA"
    "SD_DELTA"
    "ENV_SPECIFIC_PARAMETERS"
    "ENV_TEMPLATE_NAME"
)

echo "Array created with ${#possible_vars[@]} elements"

# Loop through each variable in the array
for var in "${possible_vars[@]}"; do
    # Check if the variable exists in GitHub environment
    if [ -n "${!var}" ]; then
        echo "true - Variable $var exists"
    else
        echo "false - Variable $var not found"
    fi
done
