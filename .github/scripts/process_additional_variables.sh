#!/bin/bash
# Script to parse ADDITIONAL_VARIABLES and add them to GitHub environment

echo "Processing ADDITIONAL_VARIABLES..."

# Get the ADDITIONAL_VARIABLES content
ADDITIONAL_VARS="${ADDITIONAL_VARIABLES:-}"

if [ -z "$ADDITIONAL_VARS" ]; then
    echo "ADDITIONAL_VARIABLES is empty, skipping..."
    exit 0
fi

echo "Raw ADDITIONAL_VARIABLES: $ADDITIONAL_VARS"

# Split by comma and process each variable assignment
IFS=',' read -ra VAR_PAIRS <<< "$ADDITIONAL_VARS"

for pair in "${VAR_PAIRS[@]}"; do
    # Remove any leading/trailing whitespace
    pair_clean=$(echo "$pair" | xargs)
    
    if [ -n "$pair_clean" ]; then
        # Split into key and value
        IFS='=' read -r var_name var_value <<< "$pair_clean"
        
        # Remove any whitespace from variable name
        var_name_clean=$(echo "$var_name" | xargs)
        
        if [ -n "$var_name_clean" ] && [ -n "$var_value" ]; then
            echo "Found variable: $var_name_clean=$var_value"
            
            # Add to GitHub environment
            if [ -n "$GITHUB_ENV" ]; then
                echo "$var_name_clean=$var_value" >> "$GITHUB_ENV"
                echo "✅ $var_name_clean written to GITHUB_ENV"
            else
                echo "❌ GITHUB_ENV variable is not set!"
            fi
        else
            echo "⚠️  Invalid variable assignment: $pair_clean"
        fi
    fi
done

echo "Finished processing ADDITIONAL_VARIABLES"
