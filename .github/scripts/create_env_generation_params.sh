#!/bin/bash
# Script for creating environment generation parameters in JSON format

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

# Create JSON string from non-empty environment variables
json_parts=()

# Loop through each variable in the array
for var in "${possible_vars[@]}"; do
    # Check if the variable exists in GitHub environment
    if [ -n "${!var}" ]; then
        echo "true - Variable $var exists with value: ${!var}"
        # Add variable to JSON parts
        json_parts+=("\"$var\": \"${!var}\"")
    else
        echo "false - Variable $var not found"
    fi
done

# Create the JSON string
if [ ${#json_parts[@]} -gt 0 ]; then
    json_content=$(IFS=,; echo "{${json_parts[*]}}")
    # Escape quotes for GitHub environment
    ENV_GENERATION_PARAMS=$(echo "$json_content" | sed 's/"/\\"/g')
else
    ENV_GENERATION_PARAMS=\"{}\"
fi

echo "Generated ENV_GENERATION_PARAMS: $ENV_GENERATION_PARAMS"

# Add to GitHub environment
if [ -n "$GITHUB_ENV" ]; then
    echo "ENV_GENERATION_PARAMS=$ENV_GENERATION_PARAMS" >> "$GITHUB_ENV"
    echo "✅ ENV_GENERATION_PARAMS written to GITHUB_ENV"
else
    echo "❌ GITHUB_ENV variable is not set!"
    exit 1
fi
