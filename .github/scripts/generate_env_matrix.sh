#!/bin/bash
# Script to generate environment matrix from ENV_NAMES variable

echo "Generating environment matrix from ENV_NAMES..."

# Get the ENV_NAMES content
ENV_NAMES="${ENV_NAMES:-}"

if [ -z "$ENV_NAMES" ]; then
    echo "ENV_NAMES is empty, cannot generate matrix"
    exit 1
fi

echo "Raw ENV_NAMES: $ENV_NAMES"

# Split by comma and create matrix JSON
IFS=',' read -ra ENV_ARRAY <<< "$ENV_NAMES"

# Create JSON array for matrix
matrix_json="["
for i in "${!ENV_ARRAY[@]}"; do
    env_name=$(echo "${ENV_ARRAY[$i]}" | xargs)  # Trim whitespace
    if [ -n "$env_name" ]; then
        if [ $i -gt 0 ]; then
            matrix_json="$matrix_json,"
        fi
        matrix_json="$matrix_json\"$env_name\""
    fi
done
matrix_json="$matrix_json]"

# Create the full matrix structure
matrix_output="{\"include\":[{\"env_name\":$matrix_json}]}"

echo "Generated matrix: $matrix_output"

# Add to GitHub output
if [ -n "$GITHUB_OUTPUT" ]; then
    echo "env_matrix=$matrix_output" >> "$GITHUB_OUTPUT"
    echo "✅ Matrix written to GITHUB_OUTPUT"
else
    echo "❌ GITHUB_OUTPUT variable is not set!"
    exit 1
fi
